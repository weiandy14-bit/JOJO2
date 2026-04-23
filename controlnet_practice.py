"""
ControlNet 练习工作流
演示如何使用 ControlNet 进行图像生成控制

ControlNet 是一个强大的工具，可以让我们在生成图像时
通过提供条件（边缘、深度、姿态等）来控制生成过程。
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ControlNetType(Enum):
    """支持的 ControlNet 类型"""
    CANNY_EDGE = "canny_edge"        # 边缘检测
    DEPTH = "depth"                  # 深度图
    POSE = "pose"                    # 人体姿态
    SEMANTIC = "semantic"            # 语义分割
    NORMAL = "normal"                # 法线图


@dataclass
class ControlNetConfig:
    """ControlNet 配置"""
    type: ControlNetType
    model_path: str
    weight: float = 1.0              # 控制强度 (0.0 - 2.0)
    start_step: float = 0.0           # 从哪一步开始应用 (0.0 - 1.0)
    end_step: float = 1.0             # 应用到哪一步 (0.0 - 1.0)

    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "model_path": self.model_path,
            "weight": self.weight,
            "start_step": self.start_step,
            "end_step": self.end_step,
        }


class ControlNetPipeline:
    """ControlNet 管道"""

    def __init__(self, base_model: str):
        self.base_model = base_model
        self.controlnets: List[ControlNetConfig] = []
        self.prompt = ""
        self.negative_prompt = ""

    def add_controlnet(self, config: ControlNetConfig) -> "ControlNetPipeline":
        """添加一个 ControlNet 配置"""
        self.controlnets.append(config)
        return self

    def set_prompt(self, prompt: str, negative_prompt: str = "") -> "ControlNetPipeline":
        """设置提示词"""
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        return self

    def get_config(self) -> Dict:
        """获取完整的配置"""
        return {
            "base_model": self.base_model,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "controlnets": [cn.to_dict() for cn in self.controlnets],
        }

    def show_config(self):
        """显示配置"""
        config = self.get_config()
        print("\n📋 ControlNet 管道配置:")
        print(f"基础模型: {config['base_model']}")
        print(f"正向提示: {config['prompt']}")
        print(f"负向提示: {config['negative_prompt']}")
        print(f"\n使用的 ControlNets ({len(config['controlnets'])} 个):")
        for i, cn in enumerate(config['controlnets'], 1):
            print(f"\n  {i}. {cn['type'].upper()}")
            print(f"     权重: {cn['weight']}")
            print(f"     步数范围: {cn['start_step']:.1%} - {cn['end_step']:.1%}")


# ============================================================
# 练习 1: 基础边缘控制
# ============================================================
def practice_1_canny_edge():
    """练习 1: 使用 Canny 边缘检测控制生成"""
    print("\n" + "="*60)
    print("🎯 练习 1: 基础边缘控制 (Canny Edge)")
    print("="*60)

    pipeline = ControlNetPipeline(base_model="stabilityai/stable-diffusion-2.1")

    # 添加 Canny 边缘控制
    canny_config = ControlNetConfig(
        type=ControlNetType.CANNY_EDGE,
        model_path="lllyasviel/control_v11p_sd15_canny",
        weight=1.0,
    )

    pipeline.add_controlnet(canny_config)
    pipeline.set_prompt(
        prompt="a beautiful cat, ultra realistic, high quality",
        negative_prompt="blurry, low quality, deformed"
    )

    print("\n💡 关键点:")
    print("  • Canny 边缘检测用于保持对象的轮廓")
    print("  • weight=1.0 表示完全遵循边缘约束")
    print("  • 适合需要特定形状的场景")

    pipeline.show_config()

    return pipeline


# ============================================================
# 练习 2: 深度控制
# ============================================================
def practice_2_depth_control():
    """练习 2: 使用深度图控制生成"""
    print("\n" + "="*60)
    print("🎯 练习 2: 深度控制 (Depth Map)")
    print("="*60)

    pipeline = ControlNetPipeline(base_model="stabilityai/stable-diffusion-2.1")

    # 添加深度控制
    depth_config = ControlNetConfig(
        type=ControlNetType.DEPTH,
        model_path="lllyasviel/control_v11f1p_sd15_depth",
        weight=1.0,
    )

    pipeline.add_controlnet(depth_config)
    pipeline.set_prompt(
        prompt="a spaceman walking on the moon, cinematic lighting",
        negative_prompt="flat, 2d, cartoon"
    )

    print("\n💡 关键点:")
    print("  • 深度图控制图像的空间层次感")
    print("  • 可以从参考图自动提取深度信息")
    print("  • 适合创建有深度感的3D场景")

    pipeline.show_config()

    return pipeline


# ============================================================
# 练习 3: 多个 ControlNet 组合
# ============================================================
def practice_3_multi_controlnet():
    """练习 3: 组合多个 ControlNet"""
    print("\n" + "="*60)
    print("🎯 练习 3: 多 ControlNet 组合")
    print("="*60)

    pipeline = ControlNetPipeline(base_model="stabilityai/stable-diffusion-2.1")

    # 边缘控制 (构成)
    edge_config = ControlNetConfig(
        type=ControlNetType.CANNY_EDGE,
        model_path="lllyasviel/control_v11p_sd15_canny",
        weight=0.7,
    )

    # 深度控制 (空间感)
    depth_config = ControlNetConfig(
        type=ControlNetType.DEPTH,
        model_path="lllyasviel/control_v11f1p_sd15_depth",
        weight=0.8,
    )

    pipeline.add_controlnet(edge_config)
    pipeline.add_controlnet(depth_config)
    pipeline.set_prompt(
        prompt="a luxurious modern house in the mountains, sunset, 8k",
        negative_prompt="ugly, distorted, blurry"
    )

    print("\n💡 关键点:")
    print("  • 可以同时使用多个 ControlNet")
    print("  • 权重决定各个 ControlNet 的影响程度")
    print("  • 权重和 < 2.0 通常效果最好")
    print(f"  • 当前总权重: {sum(cn.weight for cn in pipeline.controlnets):.1f}")

    pipeline.show_config()

    return pipeline


# ============================================================
# 练习 4: 渐进式控制 (步数范围)
# ============================================================
def practice_4_progressive_control():
    """练习 4: 在不同步骤应用不同的控制"""
    print("\n" + "="*60)
    print("🎯 练习 4: 渐进式控制 (步数范围)")
    print("="*60)

    pipeline = ControlNetPipeline(base_model="stabilityai/stable-diffusion-2.1")

    # 前期强控制边缘
    edge_config = ControlNetConfig(
        type=ControlNetType.CANNY_EDGE,
        model_path="lllyasviel/control_v11p_sd15_canny",
        weight=1.0,
        start_step=0.0,
        end_step=0.7,  # 仅在前 70% 步数使用
    )

    # 后期弱深度控制
    depth_config = ControlNetConfig(
        type=ControlNetType.DEPTH,
        model_path="lllyasviel/control_v11f1p_sd15_depth",
        weight=0.5,
        start_step=0.5,
        end_step=1.0,  # 仅在后 50% 步数使用
    )

    pipeline.add_controlnet(edge_config)
    pipeline.add_controlnet(depth_config)
    pipeline.set_prompt(
        prompt="a dragon breathing fire on a castle, fantasy art",
        negative_prompt="realistic, photo, blurry"
    )

    print("\n💡 关键点:")
    print("  • start_step 和 end_step 定义 ControlNet 的活跃范围")
    print("  • 前期步数: 保持结构 → 使用强控制")
    print("  • 后期步数: 添加细节 → 使用弱控制")
    print("  • 这样可以既保留约束又保留创意空间")

    pipeline.show_config()

    return pipeline


# ============================================================
# 练习 5: 权重调整实验
# ============================================================
def practice_5_weight_tuning():
    """练习 5: 权重调整的影响"""
    print("\n" + "="*60)
    print("🎯 练习 5: 权重调整实验")
    print("="*60)

    print("\n测试不同权重的影响:\n")

    for weight in [0.3, 0.7, 1.0, 1.5]:
        pipeline = ControlNetPipeline(base_model="stabilityai/stable-diffusion-2.1")

        config = ControlNetConfig(
            type=ControlNetType.CANNY_EDGE,
            model_path="lllyasviel/control_v11p_sd15_canny",
            weight=weight,
        )

        pipeline.add_controlnet(config)
        pipeline.set_prompt(
            prompt="a beautiful woman, portrait",
            negative_prompt="blurry"
        )

        print(f"权重 {weight}:")
        print(f"  • 强度: {'弱' if weight < 0.7 else '中' if weight < 1.2 else '强'}")
        print(f"  • 创意自由度: {'高' if weight < 0.7 else '中' if weight < 1.2 else '低'}")
        print()


# ============================================================
# 主函数
# ============================================================
def main():
    """运行所有练习"""
    print("\n" + "="*60)
    print("🚀 ControlNet 完整练习工作流")
    print("="*60)
    print("\n这个工作流演示了 ControlNet 的各种使用方式:")
    print("  1. 基础边缘控制 - 保持对象轮廓")
    print("  2. 深度控制 - 创建空间感")
    print("  3. 多 ControlNet 组合 - 综合多种约束")
    print("  4. 渐进式控制 - 不同步骤不同强度")
    print("  5. 权重调整 - 平衡约束与创意")

    # 执行所有练习
    p1 = practice_1_canny_edge()
    p2 = practice_2_depth_control()
    p3 = practice_3_multi_controlnet()
    p4 = practice_4_progressive_control()
    practice_5_weight_tuning()

    # 总结
    print("\n" + "="*60)
    print("✅ 练习总结")
    print("="*60)
    print("\n核心概念:")
    print("  ✓ ControlNet 类型: 选择合适的约束类型")
    print("  ✓ 权重 (weight): 控制约束的强度")
    print("  ✓ 步数范围: 控制约束应用的时间")
    print("  ✓ 多个 ControlNet: 组合不同的约束")
    print("\n最佳实践:")
    print("  • 从单个 ControlNet 开始")
    print("  • 逐步增加权重直到满意")
    print("  • 使用步数范围微调效果")
    print("  • 根据需要组合多个 ControlNet")
    print("\n下一步:")
    print("  • 准备你自己的参考图像")
    print("  • 根据需要选择 ControlNet 类型")
    print("  • 调整权重和参数")
    print("  • 运行生成管道")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
