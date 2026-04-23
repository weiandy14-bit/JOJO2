# ControlNet 快速参考卡

## 🎯 5 秒速查表

### ControlNet 类型快速选择

```
┌─────────────┬──────────────┬────────────────┬─────────┐
│ 类型        │ 最佳权重     │ 主要用途       │ 难度    │
├─────────────┼──────────────┼────────────────┼─────────┤
│ Canny Edge  │ 0.8 - 1.2    │ 轮廓/结构      │ 简单    │
│ Depth       │ 0.7 - 1.0    │ 空间感/透视    │ 简单    │
│ Pose        │ 0.9 - 1.2    │ 人物姿态       │ 中等    │
│ Semantic    │ 0.6 - 0.9    │ 语义区域       │ 困难    │
│ Normal      │ 0.6 - 0.9    │ 表面细节       │ 困难    │
└─────────────┴──────────────┴────────────────┴─────────┘
```

---

## ⚡ 常用配置模板

### 模板 1: 快速肖像
```python
pipeline = ControlNetPipeline("stabilityai/stable-diffusion-2.1")
pipeline.add_controlnet(ControlNetConfig(
    type=ControlNetType.CANNY_EDGE,
    weight=0.9
))
pipeline.set_prompt("portrait, 4k, high quality", "blurry, low quality")
```

### 模板 2: 室内设计
```python
pipeline.add_controlnet(ControlNetConfig(type=ControlNetType.DEPTH, weight=0.85))
pipeline.add_controlnet(ControlNetConfig(type=ControlNetType.CANNY_EDGE, weight=0.65))
pipeline.set_prompt("luxury modern design, 8k")
```

### 模板 3: 创意艺术
```python
pipeline.add_controlnet(ControlNetConfig(type=ControlNetType.CANNY_EDGE, weight=0.5))
pipeline.add_controlnet(ControlNetConfig(type=ControlNetType.DEPTH, weight=0.4))
pipeline.set_prompt("epic fantasy art, highly detailed, cinematic")
```

### 模板 4: 精确控制
```python
edge = ControlNetConfig(type=ControlNetType.CANNY_EDGE, weight=1.0, 
                        start_step=0.0, end_step=0.7)
depth = ControlNetConfig(type=ControlNetType.DEPTH, weight=0.5,
                         start_step=0.5, end_step=1.0)
pipeline.add_controlnet(edge)
pipeline.add_controlnet(depth)
```

---

## 🔧 权重调整速查

| 问题 | 解决方案 |
|------|--------|
| 结果不像参考图 | ↑ 权重 (0.8 → 1.0 → 1.2) |
| 结果看起来生硬 | ↓ 权重 (1.2 → 0.9 → 0.6) |
| 多个 ControlNet 冲突 | 降低辅助的权重，或使用步数范围分离 |
| 想要更创意的结果 | 使用步数范围：强约束前期，弱约束后期 |
| 总是失败生成 | 降低权重总和 < 2.0 |

---

## 📋 步数范围速查

```
生成时间线:
0%        25%       50%       75%      100%
|---------|---------|---------|---------|
  初期         中期         后期
结构定形    细节出现    最终优化

最佳实践:
- 强约束在 0-70% (保持结构)
- 弱约束在 50-100% (允许创意)
- 重叠范围实现平滑过渡
```

---

## 🎨 应用速查

| 应用场景 | 推荐配置 | 关键参数 |
|--------|--------|--------|
| **肖像** | Canny Edge | weight=0.9, neg="blurry" |
| **设计** | Depth + Canny | 0.85 + 0.65 |
| **动作** | Pose | weight=1.0 |
| **建筑** | Canny (前期) + Depth (后期) | 分阶段控制 |
| **艺术** | Canny + Depth | 低权重 (0.5-0.6) |

---

## ❌ 常见错误 & 修复

```
❌ "生成失败"
✅ 降低权重总和 < 2.0，或减少 ControlNet 数量

❌ "结果很模糊"
✅ 提高权重到 1.0+，或改进参考图质量

❌ "看起来不自然"
✅ 降低权重到 0.7-0.9，或调整提示词

❌ "多个 ControlNet 互相抵消"
✅ 使用步数范围分离它们，或调整权重比例

❌ "总是重复相同的模式"
✅ 降低权重，增加提示词多样性
```

---

## 📊 权重决策树

```
开始
 │
 ├─ 精度优先?
 │  ├─ Yes → 权重 1.0-1.3
 │  └─ No  ↓
 │
 ├─ 是否多个 ControlNet?
 │  ├─ Yes → 权重和 < 2.0, 主1.0 + 副0.5-0.8
 │  └─ No  ↓
 │
 ├─ 需要创意空间?
 │  ├─ Yes → 权重 0.5-0.7
 │  └─ No  → 权重 0.9-1.2
 │
 └─ 使用步数范围优化? (可选)
    └─ 前期强, 后期弱
```

---

## 🚀 30秒快速开始

```bash
# 1. 准备参考图
ref.jpg

# 2. 使用模板
python -c "
from controlnet_example import example_1_portrait
pipeline = example_1_portrait()
pipeline.show_config()
"

# 3. 修改参数
# weight=0.9 → 根据需要调整

# 4. 运行生成
# (使用实际的扩散管道库)
```

---

## 📚 完整学习路径

```
第1天 (1h): 运行 controlnet_practice.py 学习理论
第2天 (2h): 运行 controlnet_example.py 看应用
第3天 (3h): 根据模板调整参数实验
第4天 (4h+): 应用到实际项目
```

---

## 💡 专业技巧

### 技巧 1: 权重渐进法
```python
# 从低权重开始
weight = 0.5
# 逐步增加到满意为止
# 0.5 → 0.7 → 0.9 → 1.1
```

### 技巧 2: 步数范围优化
```python
# 保持结构，保留创意
edge = ControlNetConfig(..., start_step=0.0, end_step=0.7)
depth = ControlNetConfig(..., start_step=0.3, end_step=1.0)
```

### 技巧 3: 负向提示词关键
```python
# 与 ControlNet 对齐的负向提示
"blurry, deformed, distorted"  # for Canny
"flat, 2D, cartoon"              # for Depth
"bad anatomy, distorted"        # for Pose
```

### 技巧 4: 多次小迭代
```
生成 → 评估 → 微调 (权重 ±0.1) → 重复
比一次大改变更有效
```

---

## 🔗 相关命令

```bash
# 运行基础练习
python controlnet_practice.py

# 运行应用示例
python controlnet_example.py

# 查看完整指南
less CONTROLNET_GUIDE.md

# 查看本快速参考
less CONTROLNET_QUICK_REFERENCE.md
```

---

**最后记住**: 从低权重开始，逐步增加。大多数问题都能通过调整权重解决。🎯
