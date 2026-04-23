"""
ControlNet 实际应用示例
演示真实的 ControlNet 工作流
"""

from controlnet_practice import ControlNetPipeline, ControlNetConfig, ControlNetType


# ============================================================
# 应用示例 1: 人物肖像生成
# ============================================================
def example_1_portrait():
    """生成高质量人物肖像"""
    print("\n" + "="*60)
    print("🎨 应用 1: 人物肖像生成")
    print("="*60)

    pipeline = ControlNetPipeline(base_model="stabilityai/stable-diffusion-2.1")

    # 使用边缘控制保持脸部轮廓
    edge_config = ControlNetConfig(
        type=ControlNetType.CANNY_EDGE,
        model_path="lllyasviel/control_v11p_sd15_canny",
        weight=0.9,
    )

    pipeline.add_controlnet(edge_config)
    pipeline.set_prompt(
        prompt="beautiful woman, portrait, studio lighting, professional photography, 4k, high quality",
        negative_prompt="blurry, deformed, bad face, ugly, distorted"
    )

    print("📸 配置: 使用 Canny Edge 保持脸部轮廓")
    pipeline.show_config()

    print("\n💡 提示:")
    print("  1. 准备一张清晰的脸部参考图")
    print("  2. 提取边缘信息")
    print("  3. 使用权重 0.8-1.0 保持结构")
    print("  4. 提示词强调肖像特征")

    return pipeline


# ============================================================
# 应用示例 2: 室内设计概念图
# ============================================================
def example_2_interior_design():
    """生成室内设计概念图"""
    print("\n" + "="*60)
    print("🏠 应用 2: 室内设计概念图")
    print("="*60)

    pipeline = ControlNetPipeline(base_model="stabilityai/stable-diffusion-2.1")

    # 深度图保持空间感
    depth_config = ControlNetConfig(
        type=ControlNetType.DEPTH,
        model_path="lllyasviel/control_v11f1p_sd15_depth",
        weight=0.85,
    )

    # 边缘保持结构边界
    edge_config = ControlNetConfig(
        type=ControlNetType.CANNY_EDGE,
        model_path="lllyasviel/control_v11p_sd15_canny",
        weight=0.65,
    )

    pipeline.add_controlnet(depth_config)
    pipeline.add_controlnet(edge_config)
    pipeline.set_prompt(
        prompt="luxury modern living room, minimalist design, warm lighting, wooden furniture, plants, large windows, sunlight, 8k",
        negative_prompt="cluttered, dark, ugly, distorted"
    )

    print("🎨 配置: 结合深度和边缘保持设计意图")
    pipeline.show_config()

    print("\n💡 提示:")
    print("  1. 从草图或布局图提取信息")
    print("  2. 深度权重略高以保持空间感")
    print("  3. 提示词描述风格和装饰元素")
    print("  4. 调整权重直到满意")

    return pipeline


# ============================================================
# 应用示例 3: 人物动作生成
# ============================================================
def example_3_character_pose():
    """生成特定姿态的人物"""
    print("\n" + "="*60)
    print("🧑 应用 3: 人物动作生成")
    print("="*60)

    pipeline = ControlNetPipeline(base_model="stabilityai/stable-diffusion-2.1")

    # 使用姿态控制（pose detection）
    # 注: 实际使用需要从参考图提取关键点
    pose_config = ControlNetConfig(
        type=ControlNetType.POSE,
        model_path="lllyasviel/control_v11p_sd15_openpose",
        weight=1.0,
    )

    pipeline.add_controlnet(pose_config)
    pipeline.set_prompt(
        prompt="elegant dancer, flowing dress, dramatic pose, stage lighting, professional dance photography, 8k",
        negative_prompt="blurry, deformed, bad anatomy, distorted"
    )

    print("🎭 配置: 使用 OpenPose 保持特定姿态")
    pipeline.show_config()

    print("\n💡 提示:")
    print("  1. 使用 OpenPose 从参考图提取骨架")
    print("  2. 权重 1.0 强制保持姿态")
    print("  3. 提示词描述角色和衣着")
    print("  4. 适合创建一致的人物动作序列")

    return pipeline


# ============================================================
# 应用示例 4: 建筑概念渲染
# ============================================================
def example_4_architecture():
    """生成建筑设计概念图"""
    print("\n" + "="*60)
    print("🏢 应用 4: 建筑概念渲染")
    print("="*60)

    pipeline = ControlNetPipeline(base_model="stabilityai/stable-diffusion-2.1")

    # 边缘保持建筑线条
    edge_config = ControlNetConfig(
        type=ControlNetType.CANNY_EDGE,
        model_path="lllyasviel/control_v11p_sd15_canny",
        weight=1.0,
        start_step=0.0,
        end_step=0.8,
    )

    # 深度保持透视
    depth_config = ControlNetConfig(
        type=ControlNetType.DEPTH,
        model_path="lllyasviel/control_v11f1p_sd15_depth",
        weight=0.7,
        start_step=0.2,
        end_step=1.0,
    )

    pipeline.add_controlnet(edge_config)
    pipeline.add_controlnet(depth_config)
    pipeline.set_prompt(
        prompt="modern glass building, architectural design, sunset lighting, clear sky, reflective surface, high quality, 8k",
        negative_prompt="distorted, blurry, ugly, unrealistic"
    )

    print("🏗️ 配置: 分阶段的建筑控制")
    pipeline.show_config()

    print("\n💡 提示:")
    print("  1. 从建筑线图提取边缘")
    print("  2. 前期强边缘约束保持结构")
    print("  3. 后期深度约束保持透视")
    print("  4. 逐步约束允许添加材质和光照细节")

    return pipeline


# ============================================================
# 应用示例 5: 概念艺术生成
# ============================================================
def example_5_concept_art():
    """生成高质量概念艺术"""
    print("\n" + "="*60)
    print("🎨 应用 5: 概念艺术生成")
    print("="*60)

    pipeline = ControlNetPipeline(base_model="stabilityai/stable-diffusion-2.1")

    # 轻度边缘约束
    edge_config = ControlNetConfig(
        type=ControlNetType.CANNY_EDGE,
        model_path="lllyasviel/control_v11p_sd15_canny",
        weight=0.6,
    )

    # 轻度深度约束
    depth_config = ControlNetConfig(
        type=ControlNetType.DEPTH,
        model_path="lllyasviel/control_v11f1p_sd15_depth",
        weight=0.5,
    )

    pipeline.add_controlnet(edge_config)
    pipeline.add_controlnet(depth_config)
    pipeline.set_prompt(
        prompt="epic fantasy dragon, majestic pose, magical aura, intricate scales, cinematic lighting, concept art, highly detailed, 8k",
        negative_prompt="realistic, photo, blurry, low quality"
    )

    print("✨ 配置: 轻约束以保留创意空间")
    pipeline.show_config()

    print("\n💡 提示:")
    print("  1. 权重较低允许更多创意")
    print("  2. 提示词可以更加描述性和创意")
    print("  3. 适合概念设计和艺术创作")
    print("  4. 多次迭代改进")

    return pipeline


# ============================================================
# 权重对比实验
# ============================================================
def weight_comparison():
    """展示不同权重的效果"""
    print("\n" + "="*60)
    print("⚖️ 权重对比实验")
    print("="*60)

    print("\n同一场景，不同权重的对比:\n")

    scenarios = [
        {
            "name": "轻约束 (权重 0.5)",
            "weight": 0.5,
            "use_case": "需要大量创意的场景",
        },
        {
            "name": "中等约束 (权重 0.9)",
            "weight": 0.9,
            "use_case": "平衡约束和创意",
        },
        {
            "name": "强约束 (权重 1.3)",
            "weight": 1.3,
            "use_case": "需要精确遵循参考",
        },
    ]

    for scenario in scenarios:
        pipeline = ControlNetPipeline(base_model="stabilityai/stable-diffusion-2.1")

        config = ControlNetConfig(
            type=ControlNetType.CANNY_EDGE,
            model_path="lllyasviel/control_v11p_sd15_canny",
            weight=scenario["weight"],
        )

        pipeline.add_controlnet(config)
        pipeline.set_prompt(
            prompt="a beautiful landscape with mountains and lake",
            negative_prompt="blurry"
        )

        print(f"📊 {scenario['name']}")
        print(f"   用途: {scenario['use_case']}")
        print(f"   特点: ", end="")
        if scenario["weight"] < 0.7:
            print("灵活, 创意空间大, 可能偏离约束")
        elif scenario["weight"] < 1.1:
            print("平衡, 既有约束又有创意")
        else:
            print("严格, 忠实约束, 创意受限")
        print()


# ============================================================
# 主函数
# ============================================================
def main():
    """运行所有应用示例"""
    print("\n" + "="*60)
    print("🚀 ControlNet 实际应用示例")
    print("="*60)
    print("\n本模块演示了 5 种实际应用场景:")
    print("  1. 人物肖像 - 保持脸部特征")
    print("  2. 室内设计 - 保持空间和结构")
    print("  3. 人物动作 - 保持特定姿态")
    print("  4. 建筑概念 - 保持建筑线条和透视")
    print("  5. 概念艺术 - 平衡约束与创意")

    # 执行所有示例
    example_1_portrait()
    example_2_interior_design()
    example_3_character_pose()
    example_4_architecture()
    example_5_concept_art()
    weight_comparison()

    # 总结
    print("\n" + "="*60)
    print("✅ 应用总结")
    print("="*60)
    print("\n关键收获:")
    print("  ✓ 不同应用需要不同的 ControlNet 类型")
    print("  ✓ 权重选择取决于创意和精度需求")
    print("  ✓ 提示词必须与 ControlNet 意图对齐")
    print("  ✓ 步数范围可以精细控制效果")
    print("\n建议的工作流:")
    print("  1. 准备参考图或草图")
    print("  2. 选择合适的 ControlNet 类型")
    print("  3. 设置初始权重 (0.8 - 1.0)")
    print("  4. 编写详细的提示词")
    print("  5. 生成并迭代调整")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
