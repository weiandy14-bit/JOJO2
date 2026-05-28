import os
import sys
import json
import base64
import threading
import datetime
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

import fitz  # PyMuPDF
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
import anthropic

CONFIG_PATH = Path.home() / ".quotation_extractor" / "config.json"

COLUMNS = [
    "案件工號",
    "公共工程編碼",
    "設備名稱",
    "設備類別",
    "狀態",
    "建築類別",
    "位置",
    "廠牌",
    "型號",
    "供應商",
    "單位",
    "單價",
    "規格細項",
    "安裝日期",
    "驗收日期",
    "備註",
]

SUPPORTED_EXT = {".pdf", ".xlsx", ".xls", ".csv", ".jpg", ".jpeg", ".png"}


def load_api_key():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("api_key", "")
    return ""


def save_api_key(key):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"api_key": key}, f)


def ask_api_key(parent):
    key = simpledialog.askstring(
        "API Key",
        "請輸入 Anthropic API Key：",
        parent=parent,
        show="*",
    )
    if key:
        save_api_key(key.strip())
        return key.strip()
    return None


def scan_files(folder):
    files = []
    for root, _, fnames in os.walk(folder):
        for fname in fnames:
            if Path(fname).suffix.lower() in SUPPORTED_EXT:
                files.append(os.path.join(root, fname))
    return sorted(files)


def read_pdf_text(path):
    doc = fitz.open(path)
    texts = []
    for page in doc:
        texts.append(page.get_text())
    doc.close()
    return "\n".join(texts)


def read_excel_text(path):
    ext = Path(path).suffix.lower()
    if ext == ".csv":
        with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
            return f.read()
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    lines = []
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            row_text = "\t".join(str(c) if c is not None else "" for c in row)
            if row_text.strip():
                lines.append(row_text)
    wb.close()
    return "\n".join(lines)


def build_prompt(content_type, content):
    system = (
        "你是一位專業的工程估價單資料擷取助理。"
        "請從提供的文件內容中，擷取所有設備/品項的資料，以 JSON 陣列回傳。"
        "每個品項為一個物件，欄位包含：\n"
        "公共工程編碼、設備名稱、設備類別、位置、廠牌、型號、供應商、單位、單價、規格細項、備註\n"
        "規則：\n"
        "- 設備名稱：品項/品名/項目名稱等都算\n"
        "- 設備類別：若文件無此欄，依設備名稱推判（例如冰水主機→空調）\n"
        "- 位置：填寫估價單表頭的工程名稱/案名\n"
        "- 供應商：估價單表頭的公司名稱\n"
        "- 單價：純數字，無法擷取則空字串\n"
        "- 備註：若文件有備註欄則擷取，否則空字串\n"
        "- 無法取得的欄位填空字串\n"
        "只回傳 JSON 陣列，不要其他說明文字。"
    )
    return system, content


def extract_with_claude(client, file_path, progress_cb=None):
    ext = Path(file_path).suffix.lower()
    messages = []

    if ext == ".pdf":
        text = read_pdf_text(file_path)
        system, _ = build_prompt("text", None)
        messages = [{"role": "user", "content": f"以下是估價單內容：\n\n{text}"}]

    elif ext in {".xlsx", ".xls", ".csv"}:
        text = read_excel_text(file_path)
        system, _ = build_prompt("text", None)
        messages = [{"role": "user", "content": f"以下是估價單內容：\n\n{text}"}]

    elif ext in {".jpg", ".jpeg", ".png"}:
        with open(file_path, "rb") as f:
            img_data = base64.standard_b64encode(f.read()).decode("utf-8")
        media_type = "image/jpeg" if ext in {".jpg", ".jpeg"} else "image/png"
        system, _ = build_prompt("image", None)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": img_data,
                        },
                    },
                    {"type": "text", "text": "以上是估價單圖片，請擷取所有品項資料。"},
                ],
            }
        ]
    else:
        return []

    system, _ = build_prompt(None, None)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system,
        messages=messages,
    )

    raw = response.content[0].text.strip()
    # 清除 markdown code block
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("```", 1)[0]

    try:
        items = json.loads(raw)
        if isinstance(items, dict):
            items = [items]
    except json.JSONDecodeError:
        items = []

    return items


def write_excel(rows, output_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "擷取結果"

    header_font = Font(bold=True)
    for col_idx, col_name in enumerate(COLUMNS, 1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for row_idx, row in enumerate(rows, 2):
        for col_idx, col_name in enumerate(COLUMNS, 1):
            value = row.get(col_name, "")
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            if col_name == "單價" and value != "":
                try:
                    cell.value = float(str(value).replace(",", ""))
                    cell.number_format = "#,##0.00"
                except ValueError:
                    cell.value = value

    # 自動調整欄寬
    for col_idx, col_name in enumerate(COLUMNS, 1):
        max_len = len(col_name)
        for row_idx in range(2, ws.max_row + 1):
            val = ws.cell(row=row_idx, column=col_idx).value
            if val:
                max_len = max(max_len, min(len(str(val)), 50))
        ws.column_dimensions[get_column_letter(col_idx)].width = max_len + 4

    wb.save(output_path)


def map_item_to_row(item):
    """將 Claude 回傳的 dict 對應到輸出欄位"""
    field_map = {
        "公共工程編碼": ["公共工程編碼", "工程編碼", "編碼"],
        "設備名稱": ["設備名稱", "品項", "品名", "項目名稱", "項目", "名稱"],
        "設備類別": ["設備類別", "類別", "分類"],
        "位置": ["位置", "工程名稱", "案名", "案件名稱"],
        "廠牌": ["廠牌", "品牌", "manufacturer"],
        "型號": ["型號", "規格", "model"],
        "供應商": ["供應商", "廠商", "公司", "公司名稱"],
        "單位": ["單位", "unit"],
        "單價": ["單價", "price", "單價(元)", "金額"],
        "規格細項": ["規格細項", "規格", "技術規格", "說明", "備註說明"],
        "備註": ["備註", "remark", "注意", "說明"],
    }

    row = {col: "" for col in COLUMNS}
    for target, candidates in field_map.items():
        for key in candidates:
            if key in item and item[key] not in (None, ""):
                row[target] = item[key]
                break

    return row


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("估價單 AI 擷取工具")
        self.geometry("600x400")
        self.resizable(False, False)
        self._build_ui()
        self.api_key = load_api_key()

    def _build_ui(self):
        pad = {"padx": 16, "pady": 8}

        # 資料夾選擇
        frame_top = tk.Frame(self)
        frame_top.pack(fill="x", **pad)
        tk.Label(frame_top, text="來源資料夾：", width=12, anchor="w").pack(side="left")
        self.folder_var = tk.StringVar()
        tk.Entry(frame_top, textvariable=self.folder_var, width=48).pack(side="left", padx=4)
        tk.Button(frame_top, text="瀏覽", command=self._pick_folder).pack(side="left")

        # 進度
        frame_mid = tk.Frame(self)
        frame_mid.pack(fill="x", **pad)
        self.status_var = tk.StringVar(value="請選擇資料夾後按「開始擷取」")
        tk.Label(frame_mid, textvariable=self.status_var, anchor="w").pack(fill="x")

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill="x", padx=16)

        # 日誌
        frame_log = tk.Frame(self)
        frame_log.pack(fill="both", expand=True, **pad)
        scrollbar = tk.Scrollbar(frame_log)
        scrollbar.pack(side="right", fill="y")
        self.log_box = tk.Text(
            frame_log, height=10, state="disabled", yscrollcommand=scrollbar.set
        )
        self.log_box.pack(fill="both", expand=True)
        scrollbar.config(command=self.log_box.yview)

        # 按鈕
        frame_btn = tk.Frame(self)
        frame_btn.pack(fill="x", padx=16, pady=12)
        self.btn_start = tk.Button(
            frame_btn, text="開始擷取", width=14, command=self._start, bg="#0078D4", fg="white"
        )
        self.btn_start.pack(side="left", padx=4)
        tk.Button(frame_btn, text="設定 API Key", width=14, command=self._set_key).pack(
            side="left", padx=4
        )

    def _pick_folder(self):
        folder = filedialog.askdirectory(title="選擇要掃描的資料夾")
        if folder:
            self.folder_var.set(folder)

    def _set_key(self):
        key = ask_api_key(self)
        if key:
            self.api_key = key
            self._log("API Key 已更新")

    def _log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _start(self):
        folder = self.folder_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("錯誤", "請先選擇有效的資料夾")
            return

        if not self.api_key:
            self.api_key = ask_api_key(self)
            if not self.api_key:
                return

        self.btn_start.config(state="disabled")
        threading.Thread(target=self._run, args=(folder,), daemon=True).start()

    def _run(self, folder):
        try:
            files = scan_files(folder)
            if not files:
                self.after(0, lambda: messagebox.showinfo("提示", "找不到支援的檔案"))
                self.after(0, lambda: self.btn_start.config(state="normal"))
                return

            self._log(f"共找到 {len(files)} 個檔案，開始處理...")
            client = anthropic.Anthropic(api_key=self.api_key)
            all_rows = []

            for i, file_path in enumerate(files, 1):
                fname = os.path.basename(file_path)
                self.after(
                    0,
                    lambda i=i, n=len(files), f=fname: (
                        self.status_var.set(f"第 {i}/{n} 個：{f}"),
                        self.progress_var.set(i / n * 100),
                    ),
                )
                self._log(f"[{i}/{len(files)}] {fname}")
                try:
                    items = extract_with_claude(client, file_path)
                    rows = [map_item_to_row(item) for item in items]
                    all_rows.extend(rows)
                    self._log(f"  → 擷取到 {len(rows)} 筆")
                except Exception as e:
                    self._log(f"  → 錯誤：{e}")

            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            parent_dir = str(Path(folder).parent)
            output_path = os.path.join(parent_dir, f"擷取結果_{ts}.xlsx")
            write_excel(all_rows, output_path)

            self._log(f"\n完成！共 {len(all_rows)} 筆，輸出：{output_path}")
            self.after(
                0,
                lambda: (
                    self.status_var.set("完成！"),
                    messagebox.showinfo("完成", f"擷取完成，共 {len(all_rows)} 筆\n\n{output_path}"),
                    self._open_file(output_path),
                ),
            )
        except Exception as e:
            self._log(f"嚴重錯誤：{e}")
            self.after(0, lambda: messagebox.showerror("錯誤", str(e)))
        finally:
            self.after(0, lambda: self.btn_start.config(state="normal"))

    def _open_file(self, path):
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception:
            pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
