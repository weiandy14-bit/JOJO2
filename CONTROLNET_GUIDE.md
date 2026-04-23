# ControlNet 练习工作流指南

## 📚 什么是 ControlNet？

ControlNet 是一种神经网络架构，允许你通过提供额外的**条件信息**来控制图像生成过程。它与 Stable Diffusion 等扩散模型配合使用。

### 核心优势
- **精确控制**: 指定图像的构成、深度、姿态等
- **创意与约束的平衡**: 既保留创意，又有控制力
- **可组合**: 多个 ControlNet 可同时使用

---

## 🎯 五个练习

### 练习 1: 基础边缘控制 (Canny Edge)

**目标**: 学习如何用边缘约束来保持对象轮廓

```python
ControlNetConfig(
    type=ControlNetType.CANNY_EDGE,
    model_path="lllyasviel/control_v11p_sd15_canny",
    weight=1.0,
)
```

**何时使用**:
- 需要特定形状的对象
- 有参考图的轮廓
- 需要高精度的构成

**最佳实践**:
- 权重范围: 0.7 - 1.2
- 从清晰的边缘开始
- 权重 1.0 时效果最稳定

---

### 练习 2: 深度控制 (Depth Map)

**目标**: 学习如何创建有空间层次感的图像

```python
ControlNetConfig(
    type=ControlNetType.DEPTH,
    model_path="lllyasviel/control_v11f1p_sd15_depth",
    weight=1.0,
)
```

**何时使用**:
- 需要 3D 空间感的场景
- 有明确的前景/背景关系
- 创建透视和深度

**最佳实践**:
- 权重范围: 0.8 - 1.2
- 确保深度图对比清晰
- 配合适当的提示词（如 "cinematic", "3D"）

---

### 练习 3: 多 ControlNet 组合

**目标**: 学习如何组合多个 ControlNet 以获得更好的控制

```python
pipeline.add_controlnet(edge_config)     # 0.7
pipeline.add_controlnet(depth_config)    # 0.8
# 总权重: 1.5 (理想范围: < 2.0)
```

**关键原则**:
- 总权重通常 < 2.0
- 不同 ControlNet 发挥不同作用
- 权重分配要均衡

**常见组合**:
| 组合 | 用途 | 推荐权重 |
|------|------|--------|
| 边缘 + 深度 | 完整的结构控制 | 0.7 + 0.8 |
| 边缘 + 姿态 | 人物/动物的形状和姿态 | 0.8 + 0.7 |
| 深度 + 语义 | 场景的结构和内容 | 0.9 + 0.6 |

---

### 练习 4: 渐进式控制 (步数范围)

**目标**: 学习在不同生成阶段应用不同的约束

```python
# 前期强控制 (0% - 70%)
edge_config = ControlNetConfig(
    weight=1.0,
    start_step=0.0,
    end_step=0.7,
)

# 后期弱控制 (50% - 100%)
depth_config = ControlNetConfig(
    weight=0.5,
    start_step=0.5,
    end_step=1.0,
)
```

**生成过程的阶段**:
1. **0-25% (初期)**: 定义大的形状和构成
2. **25-75% (中期)**: 细节逐渐出现
3. **75-100% (后期)**: 纹理和最终细节

**最佳实践**:
- 前期强控制: 保持结构稳定
- 后期弱控制: 允许模型添加创意细节
- 步数重叠: 平滑过渡

---

### 练习 5: 权重调整实验

**目标**: 理解权重如何影响生成结果

```
权重 0.3  → 弱约束，高创意自由度
权重 0.7  → 中等约束，平衡创意
权重 1.0  → 标准约束，稳定生成
权重 1.5  → 强约束，低创意自由度
```

**权重选择建议**:

| 权重 | 约束强度 | 适用场景 | 优点 | 缺点 |
|------|---------|--------|------|------|
| 0.3-0.5 | 弱 | 需要创意的场景 | 灵活有趣 | 可能偏离约束 |
| 0.7-1.0 | 中 | 大多数应用 | 平衡好 | - |
| 1.0-1.3 | 强 | 精确控制 | 忠实约束 | 可能重复 |
| 1.5+ | 很强 | 严格要求 | 非常精确 | 创意受限 |

---

## 🚀 实践步骤

### Step 1: 准备参考图像
```bash
# 放置参考图像
reference_image.jpg
```

### Step 2: 选择 ControlNet 类型

根据你的目标选择合适的类型：

- **Canny Edge**: 已有清晰轮廓的参考
- **Depth**: 需要 3D 空间感
- **Pose**: 人物/动物的姿态控制
- **Semantic**: 按语义区域控制内容
- **Normal**: 表面法线信息

### Step 3: 设置参数

```python
pipeline = ControlNetPipeline(
    base_model="stabilityai/stable-diffusion-2.1"
)

pipeline.add_controlnet(
    ControlNetConfig(
        type=ControlNetType.CANNY_EDGE,
        weight=0.9,  # 根据需要调整
    )
)

pipeline.set_prompt(
    "a beautiful landscape",
    negative_prompt="blurry, low quality"
)
```

### Step 4: 生成并迭代

1. 运行第一次生成
2. 检查结果
3. 调整权重或 ControlNet 类型
4. 重复直到满意

---

## 💡 高级技巧

### 技巧 1: 权重渐进

在生成过程中逐渐改变权重：
```python
# 前期高权重，后期低权重
start_step=0.0, weight=1.2
end_step=0.7

# 后期恢复一些控制
start_step=0.7, weight=0.3
end_step=1.0
```

### 技巧 2: 多种 ControlNet 组合策略

**稳定性优先**:
```
边缘 (1.0) + 深度 (0.6)
```

**创意优先**:
```
边缘 (0.5) + 深度 (0.4)
```

**精确控制**:
```
边缘 (1.2) + 深度 (0.8) + 法线 (0.5)
```

### 技巧 3: 负向提示词

使用负向提示词来排除不想要的效果：

```python
negative_prompt = "blurry, deformed, low quality, 3d render, cartoon"
```

### 技巧 4: 提示词与 ControlNet 对齐

好的提示词应该与 ControlNet 的意图一致：

```python
# 配置 Depth ControlNet
pipeline.set_prompt(
    "cinematic landscape, 3D depth, foreground and background",  # 强调深度
    negative_prompt="flat, 2D"
)
```

---

## 📊 对比表

### ControlNet 类型对比

| 类型 | 输入 | 控制什么 | 难度 | 效果 |
|------|------|--------|------|------|
| Canny | 图像边缘 | 对象轮廓 | 低 | 强 |
| Depth | 深度图 | 空间关系 | 中 | 强 |
| Pose | 关键点 | 人物姿态 | 中 | 强 |
| Semantic | 分割图 | 语义区域 | 高 | 中 |
| Normal | 法线图 | 表面细节 | 高 | 中 |

---

## ⚠️ 常见问题

### Q1: 为什么生成结果不像我的参考图？
**A**: 
- 权重可能太低（< 0.5），增加到 0.8-1.0
- 提示词可能不够具体
- 基础模型可能不适合（尝试不同的 base_model）

### Q2: 为什么结果看起来不自然？
**A**:
- 权重可能太高（> 1.5），降低到 0.8-1.2
- ControlNet 约束过强，尝试使用步数范围削弱后期约束
- 使用负向提示词排除不想要的元素

### Q3: 多个 ControlNet 如何平衡权重？
**A**:
- 主要约束: 1.0
- 辅助约束: 0.5-0.8
- 总和通常 < 2.0

### Q4: 何时使用步数范围？
**A**:
- 需要保持结构但想要创意 → 前期强，后期弱
- 逐步改进细节 → 多个 ControlNet 错开步数

---

## 🎓 学习路径

1. **入门** (1-2 小时)
   - 运行 `python controlnet_practice.py`
   - 理解 5 个练习的概念

2. **基础** (3-4 小时)
   - 尝试单个 ControlNet
   - 调整权重观察效果
   - 编写你自己的配置

3. **进阶** (5+ 小时)
   - 组合多个 ControlNet
   - 实验步数范围
   - 优化提示词

4. **精通** (10+ 小时)
   - 针对不同场景优化参数
   - 创建可复用的配置
   - 构建完整的生成管道

---

## 📝 笔记

最后，记住这几个关键点：

✅ **DO**:
- 从低权重开始，逐步增加
- 为每种场景创建配置模板
- 记录有效的参数组合
- 实验不同的 ControlNet 组合

❌ **DON'T**:
- 直接使用高权重（可能失败）
- 忽视提示词的重要性
- 过度组合 ControlNet（总权重 > 3.0）
- 在同一图中使用相互冲突的约束

---

## 🔗 相关资源

- ControlNet 论文: https://arxiv.org/abs/2302.05543
- Hugging Face Hub: https://huggingface.co/lllyasviel
- Stable Diffusion 文档: https://huggingface.co/docs/diffusers

---

**祝你练习愉快！** 🚀
