#!/usr/bin/env python3
"""
测试replan RAG系统的基本功能
不需要完整的语言模型，只测试RAG检索部分
"""

import json
from replan_rag_system import ReplanRAGSystem

def test_rag_retrieval():
    """测试RAG检索功能"""
    print("=== Testing RAG Retrieval System ===")

    # 初始化RAG系统
    rag_system = ReplanRAGSystem()

    # 测试用例1: 只有底部存在
    target_spec_1 = {
        "target_colors": {"bottom": "blue", "middle": "green", "top": "red"},
        "coords": {"bottom": [230, 240, 150], "middle": [230, 240, 200], "top": [230, 240, 250]},
        "buffer_slots": {"B1": [180, 300, 150], "B2": [280, 300, 150], "B3": [180, 340, 150]},
        "supply": {"red": True, "green": True, "blue": True},
        "allow_residual": False
    }

    current_state_1 = {
        "present_layers": [{"position": "bottom", "color": "blue"}],
        "scattered": []
    }

    print("\n--- Test Case 1: Only Bottom Present ---")

    # 测试场景分类
    scenario = rag_system.classify_scenario_by_embedding(target_spec_1, current_state_1)
    print(f"Scenario classification: {scenario}")

    # 测试规则检索
    rules = rag_system.retrieve_and_filter_rules(target_spec_1, current_state_1)
    print(f"Retrieved {len(rules)} rules:")
    for i, rule in enumerate(rules):
        print(f"  {i+1}. {rule['title']} (similarity: {rule.get('similarity_score', 0):.3f})")

    # 测试prompt构建
    system_prompt, user_prompt = rag_system.build_rag_prompt(target_spec_1, current_state_1)
    print(f"\nSystem prompt length: {len(system_prompt)} chars")
    print(f"User prompt length: {len(user_prompt)} chars")

    print("\n" + "="*50)

    # 测试用例2: 全部分散
    current_state_2 = {
        "present_layers": [],
        "scattered": [
            {"color": "red", "location": "table", "pos": [300, 300, 150]},
            {"color": "green", "location": "table", "pos": [200, 200, 150]},
            {"color": "blue", "location": "table", "pos": [260, 280, 150]}
        ]
    }

    print("\n--- Test Case 2: All Scattered ---")

    scenario = rag_system.classify_scenario_by_embedding(target_spec_1, current_state_2)
    print(f"Scenario classification: {scenario}")

    rules = rag_system.retrieve_and_filter_rules(target_spec_1, current_state_2)
    print(f"Retrieved {len(rules)} rules:")
    for i, rule in enumerate(rules):
        print(f"  {i+1}. {rule['title']} (similarity: {rule.get('similarity_score', 0):.3f})")

    print("\n" + "="*50)

    # 测试用例3: 颜色错误
    current_state_3 = {
        "present_layers": [
            {"position": "bottom", "color": "red"},
            {"position": "middle", "color": "green"}
        ],
        "scattered": []
    }

    print("\n--- Test Case 3: Wrong Bottom Color ---")

    scenario = rag_system.classify_scenario_by_embedding(target_spec_1, current_state_3)
    print(f"Scenario classification: {scenario}")

    rules = rag_system.retrieve_and_filter_rules(target_spec_1, current_state_3)
    print(f"Retrieved {len(rules)} rules:")
    for i, rule in enumerate(rules):
        print(f"  {i+1}. {rule['title']} (similarity: {rule.get('similarity_score', 0):.3f})")

    print("\n=== RAG System Test Complete ===")

def test_knowledge_base_loading():
    """测试知识库加载"""
    print("=== Testing Knowledge Base Loading ===")

    rag_system = ReplanRAGSystem()

    print(f"Loaded {len(rag_system.knowledge_base)} rules from knowledge base")

    # 显示所有规则
    for i, rule in enumerate(rag_system.knowledge_base):
        title = rule.get('title', 'Untitled')
        file_path = rule.get('file_path', '')
        print(f"  {i+1}. {title} ({file_path.split('/')[-1]})")

    print("\n=== Knowledge Base Test Complete ===")

if __name__ == "__main__":
    test_knowledge_base_loading()
    print()
    test_rag_retrieval()