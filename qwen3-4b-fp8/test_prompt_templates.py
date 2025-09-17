#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有提示词模板加载和降级机制
"""

from replan_rag_system import ReplanRAGSystem
import json

def main():
    print("=== 测试所有提示词模板加载 ===")

    try:
        # 初始化RAG系统
        print("初始化RAG系统...")
        rag_system = ReplanRAGSystem()

        print(f"\n✅ 成功加载的模板: {list(rag_system.prompt_templates.keys())}")
        print(f"✅ 模板总数: {len(rag_system.prompt_templates)}")

        # 预期的所有模板
        expected_templates = ['top_only', 'middle_only', 'bottom_only', 'extension', 'multiple']
        missing = set(expected_templates) - set(rag_system.prompt_templates.keys())
        if missing:
            print(f"⚠️ 缺少模板: {missing}")
        else:
            print("✅ 所有预期模板都已加载")

        print("\n=== 测试每个模板的降级机制 ===")

        # 测试每个模板的降级机制
        test_types = ['top_only', 'middle_only', 'bottom_only', 'extension', 'multiple', 'unknown_type']

        for test_type in test_types:
            print(f"\n--- 测试 {test_type} ---")
            try:
                prompt = rag_system._get_prompt_with_fallback(test_type)
                print(f"✅ 返回提示词行数: {len(prompt)}")
                if prompt:
                    print(f"📝 首行预览: {prompt[0]}")
                    # 检查是否包含关键标识
                    prompt_text = ' '.join(prompt)
                    if test_type in ['top_only', 'middle_only', 'bottom_only', 'extension', 'multiple']:
                        if test_type.upper() in prompt_text.upper():
                            print(f"✅ 包含 {test_type} 特定内容")
                        else:
                            print(f"⚠️ 可能使用了通用或降级内容")
                    else:
                        print("✅ 未知类型使用降级机制")
                else:
                    print("❌ 返回空提示词")
            except Exception as e:
                print(f"❌ 测试 {test_type} 失败: {e}")

        print("\n=== 测试模板内容质量 ===")

        # 检查每个模板的关键内容
        quality_checks = {
            'top_only': ['TOP LAYER', '2 steps', 'SIMPLE'],
            'middle_only': ['MIDDLE LAYER', '4 steps', 'COMPLEX', 'BLOCKING'],
            'bottom_only': ['BOTTOM', '6-STEP', 'INACCESSIBLE', 'CLEAR EVERY'],
            'extension': ['EXTENSION', 'MINIMAL', 'AUTO-ADJUSTMENT'],
            'multiple': ['MULTIPLE', 'RECONSTRUCTION', 'STRATEGIC']
        }

        for template_type, keywords in quality_checks.items():
            if template_type in rag_system.prompt_templates:
                prompt_content = ' '.join(rag_system.prompt_templates[template_type]).upper()
                found_keywords = [kw for kw in keywords if kw in prompt_content]
                print(f"📋 {template_type}: 包含关键词 {len(found_keywords)}/{len(keywords)}: {found_keywords}")

        print("\n✅ 所有模板测试完成")
        print("\n=== 测试摘要 ===")
        print(f"📊 预期模板数: {len(expected_templates)}")
        print(f"📊 实际加载数: {len(rag_system.prompt_templates)}")
        print(f"📊 知识库规则数: {len(rag_system.knowledge_base)}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)