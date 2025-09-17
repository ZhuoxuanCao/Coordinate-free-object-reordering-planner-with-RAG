#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Replan RAG System - 基于真正的RAG实现的立方体重新规划器
- 外部知识库：规则存储在replan_rag_knowledge_base中
- 语义检索：使用embedding相似度匹配相关规则
- 自然语言理解：理解replan任务的current state和target spec
- 动态组合：根据查询场景动态组合相关规则
- 验证机制：确保生成的计划符合replan约束

111
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

import torch
from torch.nn.attention import SDPBackend, sdpa_kernel
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer

# =============== 配置项 ===============
MODEL_NAME = "Qwen/Qwen3-4B-Instruct-2507-FP8"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 轻量级embedding模型
KNOWLEDGE_BASE_DIR = "replan_rag_knowledge_base"
MAX_NEW_TOKENS = 4096
TEMPERATURE = 0.3  # 降低温度提高一致性
TOP_P = 0.9
DO_SAMPLE = True
TOP_K_RETRIEVAL = 5  # 检索前K个最相关的规则

# 预定义Buffer槽位
BUFFER_SLOTS = {
    "B1": [180, 300, 150],
    "B2": [280, 300, 150],
    "B3": [180, 340, 150]
}

# 支持的关系类型
SUPPORTED_RELATIONSHIPS = [
    "stacked",
    "stacked_left",
    "stacked_middle",
    "stacked_right",
    "separated_left_right",
    "separated_front_back",
    "separate_horizontal",
    "separate_vertical",
    "stacked_and_separated_left",
    "stacked_and_separated_right",
    "pyramid",
    "none"  # 无结构状态
]


def _object_key_sort_key(key: str) -> int:
    """提取 object 键的序号以便排序（object、object 1、object 2 ...）。"""
    suffix = key[len("object"):].strip()
    if suffix.isdigit():
        return int(suffix)
    return 0


def extract_object_value(placement: Dict[str, Any]) -> str:
    """从 placements 条目中提取对象描述，兼容 object / object 1 / object 2 等写法。"""
    if not isinstance(placement, dict):
        return None
    if "object" in placement:
        return placement.get("object")

    candidates = [key for key in placement.keys() if key.startswith("object")]
    for key in sorted(candidates, key=_object_key_sort_key):
        value = placement.get(key)
        if value:
            return value
    return None


def build_position_object_map(placements: List[Dict[str, Any]]) -> Dict[str, str]:
    """将 placements 列表转换为 position->object 的映射，忽略无 position 的条目。"""
    mapping: Dict[str, str] = {}
    for placement in placements or []:
        position = placement.get("position")
        obj = extract_object_value(placement)
        if position and obj:
            mapping[position] = obj
    return mapping


def collect_objects_list(placements: List[Dict[str, Any]]) -> List[str]:
    """提取 placements 中的对象列表（按顺序），包含无 position 的条目。"""
    result: List[str] = []
    for placement in placements or []:
        obj = extract_object_value(placement)
        if obj:
            result.append(obj)
    return result


def format_placements_for_query(placements: List[Dict[str, Any]]) -> str:
    """将placements格式化为 position=object 文本用于查询描述。"""
    parts: List[str] = []
    for placement in placements or []:
        obj = extract_object_value(placement)
        pos = placement.get("position")
        if pos and obj:
            parts.append(f"{pos}={obj}")
        elif obj:
            parts.append(f"object={obj}")
    return " ".join(parts)


def enforce_plan_consistency(plan: List[Dict[str, Any]]) -> None:
    """Enhanced plan consistency validation with support for stacking extensions."""
    stack_positions: Dict[str, str] = {}
    arrangement_positions: Dict[str, str] = {}
    object_stack_targets: Dict[str, str] = {}
    object_arrangement_targets: Dict[str, str] = {}

    # Track "top" position actions for extension validation
    top_placements = []

    for action in plan:
        if not isinstance(action, dict):
            raise ValueError("Each action must be an object")

        obj = action.get("object")
        to = action.get("to")
        fr = action.get("from")

        if isinstance(fr, dict) and isinstance(to, dict) and fr.get("type") == to.get("type") and fr.get("position") == to.get("position") and fr.get("slot") == to.get("slot"):
            raise ValueError("Action has identical 'from' and 'to', which is redundant")

        if isinstance(to, dict) and to.get("type") == "stack":
            pos = to.get("position")
            if not pos:
                raise ValueError("Stack placement action missing target position")
            if obj in object_stack_targets and object_stack_targets[obj] != pos:
                raise ValueError(f"Object '{obj}' placed into multiple stack positions within the same plan")
            object_stack_targets[obj] = pos

            # Special handling for "top" position - allow multiple objects for stacking extension
            if pos == "top":
                top_placements.append(obj)
            else:
                # For bottom/middle, maintain strict uniqueness
                prev = stack_positions.get(pos)
                if prev and prev != obj:
                    raise ValueError(f"Stack position '{pos}' assigned to multiple objects ({prev} vs {obj})")
                stack_positions[pos] = obj

        if isinstance(to, dict) and to.get("type") == "arrangement":
            pos = to.get("position")
            if not pos:
                raise ValueError("Arrangement placement action missing target position")
            if obj in object_arrangement_targets and object_arrangement_targets[obj] != pos:
                raise ValueError(f"Object '{obj}' placed into multiple arrangement positions within the same plan")
            object_arrangement_targets[obj] = pos

            prev = arrangement_positions.get(pos)
            if prev and prev != obj:
                raise ValueError(f"Arrangement position '{pos}' assigned to multiple objects ({prev} vs {obj})")
            arrangement_positions[pos] = obj

    # Validate top placements: allow multiple for stacking extension, but no duplicate objects
    if len(top_placements) != len(set(top_placements)):
        duplicates = [obj for obj in set(top_placements) if top_placements.count(obj) > 1]
        raise ValueError(f"Same object(s) placed to top position multiple times: {duplicates}")

def validate_target_structure_payload(structure: Dict[str, Any]) -> None:
    """验证 target_structure / final_expected.target_structure 的字段是否符合新格式。"""
    if not isinstance(structure, dict):
        raise ValueError("target_structure must be an object")

    relationship = structure.get("relationship")
    placements = structure.get("placements")

    if not relationship:
        raise ValueError("Missing 'relationship' key in target_structure")
    if not isinstance(placements, list) or not placements:
        raise ValueError("'placements' must be a non-empty list")

    # 验证每个 placement 至少有 object 信息
    for placement in placements:
        obj = extract_object_value(placement)
        if not obj:
            raise ValueError("Each placement must include an object description (object/object 1/2/3)")

    # 关系特定的位置信息要求
    def ensure_positions(expected: List[str]) -> None:
        positions = [p.get("position") for p in placements]
        missing = set(expected) - set(positions)
        extra = set(pos for pos in positions if pos) - set(expected)
        if missing or extra:
            raise ValueError(f"Relationship '{relationship}' requires positions {expected}, found {positions}")

    if relationship in {"stacked_left", "stacked_middle", "stacked_right"}:
        if len(placements) != 1:
            raise ValueError(f"{relationship} requires exactly 1 placement")
        # 单物体通常不包含 position；如存在也允许
    elif relationship == "stacked":
        positions = [p.get("position") for p in placements]
        expected_two = ["bottom", "top"]
        expected_three = ["bottom", "middle", "top"]
        if len(placements) == 2:
            ensure_positions(expected_two)
        elif len(placements) == 3:
            ensure_positions(expected_three)
        else:
            raise ValueError("Stacked relationship requires 2 or 3 placements")
    elif relationship == "separated_left_right":
        ensure_positions(["left", "right"])
    elif relationship == "separated_front_back":
        ensure_positions(["front", "back"])
    elif relationship == "separate_horizontal":
        ensure_positions(["left", "middle", "right"])
    elif relationship == "separate_vertical":
        ensure_positions(["bottom", "middle", "top"])
    elif relationship == "pyramid":
        ensure_positions(["bottom left", "bottom right", "top"])
    elif relationship == "stacked_and_separated_left":
        ensure_positions(["bottom", "top", "left"])
    elif relationship == "stacked_and_separated_right":
        ensure_positions(["bottom", "top", "right"])
    else:
        # 若出现未识别的关系，仍允许但至少确保有 position/对象信息
        pass

class ReplanRAGSystem:
    def __init__(self):
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.knowledge_base = []
        self.rule_embeddings = None
        self._rule_lookup: Dict[str, Dict[str, Any]] = {}
        self._load_knowledge_base()

    def classify_scenario_by_embedding(self, target_spec: Dict[str, Any], current_state: Dict[str, Any]) -> str:
        """基于embedding相似度进行场景分类"""
        # 构建查询描述
        target_structure = target_spec.get("target_structure", {})
        current_structure = current_state.get("target_structure", {})

        target_relationship = target_structure.get("relationship")
        current_relationship = current_structure.get("relationship") or "none"

        target_placements = target_structure.get("placements", [])
        current_placements = current_structure.get("placements", [])

        target_map = build_position_object_map(target_placements)
        current_map = build_position_object_map(current_placements)

        target_objects = collect_objects_list(target_placements)
        current_objects = collect_objects_list(current_placements)

        query_parts: List[str] = []

        # 记录基础描述
        if target_relationship:
            query_parts.append(f"target relationship {target_relationship}")
        if target_objects:
            query_parts.append(f"target objects {' '.join(target_objects)}")
        query_parts.append(f"current relationship {current_relationship}")
        if current_objects:
            query_parts.append(f"current objects {' '.join(current_objects)}")

        # 基于目标关系类型构建分析
        if target_relationship == "stacked":
            query_parts.append("stacked arrangement vertical tower building")

            expected_positions = ["bottom", "middle", "top"]
            if len(target_map) == 2:
                expected_positions = ["bottom", "top"]

            if current_relationship == "stacked":
                missing = [pos for pos in expected_positions if pos not in current_map]
                if missing:
                    query_parts.append(f"missing stack positions {' '.join(missing)}")
                else:
                    mismatches = []
                    mismatch_details = []
                    for pos in expected_positions:
                        target_obj = target_map.get(pos)
                        current_obj = current_map.get(pos)
                        if target_obj and current_obj and target_obj != current_obj:
                            mismatches.append(f"{pos} wrong object")
                            mismatch_details.append(f"{pos} has {current_obj} needs {target_obj}")

                    if mismatches:
                        query_parts.extend(mismatches)
                        query_parts.extend(mismatch_details)

                        # 强调替换场景特征
                        if "middle" in [pos for pos in expected_positions if target_map.get(pos) != current_map.get(pos)]:
                            query_parts.append("middle layer replacement physical access constraint")
                            query_parts.append("clear top to access middle blocked position")
                        if "bottom" in [pos for pos in expected_positions if target_map.get(pos) != current_map.get(pos)]:
                            query_parts.append("bottom layer replacement clear entire stack")

                        # 强调对象生命周期
                        wrong_objects = [current_map.get(pos) for pos in expected_positions
                                       if current_map.get(pos) and target_map.get(pos)
                                       and current_map.get(pos) != target_map.get(pos)]
                        target_objects = [target_map.get(pos) for pos in expected_positions if target_map.get(pos)]

                        for wrong_obj in wrong_objects:
                            if wrong_obj not in target_objects:
                                query_parts.append(f"{wrong_obj} not in target permanent removal")
                    else:
                        query_parts.append("correct stack arrangement")
            else:
                query_parts.append("different relationship need stacking")

        elif target_relationship in {"stacked_left", "stacked_middle", "stacked_right"}:
            query_parts.append("single object stack placement")
            target_obj = target_objects[0] if target_objects else None
            current_obj = current_objects[0] if current_objects else None
            if current_relationship == target_relationship and target_obj == current_obj:
                query_parts.append("single object already correct")
            else:
                query_parts.append("single object needs update")

        elif target_relationship in {
            "separated_left_right",
            "separated_front_back",
            "separate_horizontal",
            "separate_vertical",
            "stacked_and_separated_left",
            "stacked_and_separated_right"
        }:
            query_parts.append(f"{target_relationship} arrangement analysis")

            if current_relationship == target_relationship:
                missing = [pos for pos in target_map.keys() if pos not in current_map]
                if missing:
                    query_parts.append(f"missing positions {' '.join(missing)}")
                else:
                    mismatches = []
                    for pos, target_obj in target_map.items():
                        current_obj = current_map.get(pos)
                        if target_obj and current_obj and target_obj != current_obj:
                            mismatches.append(f"{pos} wrong object")
                    if mismatches:
                        query_parts.extend(mismatches)
                    else:
                        query_parts.append("correct separation arrangement")
            else:
                query_parts.append("different relationship need separation")

        elif target_relationship == "pyramid":
            query_parts.append("pyramid arrangement bottom pair top single")
        else:
            query_parts.append("general object reordering")

        query = " ".join(filter(None, query_parts)) + " object reordering planning"

        # 预定义的场景模板 - 按复杂度分层
        templates = {
            "stack_replacement_top": [
                "top layer wrong object replacement",
                "incorrect top object simple replacement",
                "wrong object at top position direct access",
                "top layer object mismatch direct replacement",
                "replace top object no blocking layers",
                "simple top layer correction"
            ],
            "stack_replacement_middle": [
                "middle layer wrong object replacement",
                "incorrect middle object blocked access",
                "wrong object at middle position clear above first",
                "middle layer object mismatch physical constraint",
                "replace middle object clear top first",
                "blocked middle layer access constraint"
            ],
            "stack_replacement_bottom": [
                "bottom layer wrong object replacement",
                "incorrect bottom object clear entire stack",
                "wrong object at bottom position full reconstruction",
                "bottom layer object mismatch clear all above",
                "replace bottom object clear entire stack",
                "foundation layer replacement complete rebuild"
            ],
            "stack_replacement_multiple": [
                "multiple layers wrong objects replacement",
                "complex multi-position object correction",
                "several wrong objects stack reconstruction",
                "multiple layer mismatch complete rebuild"
            ],
            "stacked_building": [
                "stacked arrangement vertical tower building",
                "all objects scattered need stacking bottom up",
                "partial stack need completion",
                "different relationship need stacking",
                "bottom middle top stacking sequence",
                "stack extension add new layer"
            ],
            "separated_arrangement": [
                "separated_left_right arrangement horizontal separation",
                "separated_front_back arrangement horizontal separation",
                "all objects scattered need separation",
                "partial separation need completion",
                "different relationship need separation"
            ],
            "object_reordering": [
                "wrong object replacement correction",
                "object mismatch position needs fixing",
                "incorrect object needs replacement",
                "object mismatch clear and rebuild"
            ],
            "buffer_management": [
                "buffer storage temporary object placement",
                "temporary storage during reconstruction",
                "buffer slots for object rearrangement"
            ],
            "legacy_format": [
                "legacy format object reordering",
                "coordinate based cube planning",
                "all cubes scattered on table",
                "only bottom layer present",
                "multiple layers present"
            ],
            "already_correct": [
                "correct arrangement no changes",
                "target already achieved no action",
                "perfect configuration complete"
            ]
        }

        # 分析替换复杂度以增强查询描述
        replacement_type = self._analyze_replacement_complexity(target_spec, current_state)
        if replacement_type != "none":
            if replacement_type == "top_only":
                query += " top layer simple replacement direct access"
            elif replacement_type == "middle_only":
                query += " middle layer blocked replacement clear above first"
            elif replacement_type == "bottom_only":
                query += " bottom layer complex replacement clear entire stack"
            elif replacement_type == "extension":
                query += " stack extension add new layer"
            elif replacement_type == "multiple":
                query += " multiple layer replacement complex rebuild"

        # 对查询进行embedding
        query_embedding = self.embedding_model.encode([query])

        max_similarity = -1
        best_scenario = "stacked_building"  # 默认场景

        # 与每个场景类别的模板进行相似度比较
        for scenario, template_list in templates.items():
            template_embeddings = self.embedding_model.encode(template_list)
            similarities = cosine_similarity(query_embedding, template_embeddings).flatten()
            max_sim_for_scenario = similarities.max()

            if max_sim_for_scenario > max_similarity:
                max_similarity = max_sim_for_scenario
                best_scenario = scenario

        # 如果是替换场景但相似度不高，强制使用相应的替换分类
        if replacement_type != "none" and max_similarity < 0.7:
            if replacement_type == "top_only":
                best_scenario = "stack_replacement_top"
            elif replacement_type == "middle_only":
                best_scenario = "stack_replacement_middle"
            elif replacement_type == "bottom_only":
                best_scenario = "stack_replacement_bottom"
            elif replacement_type == "multiple":
                best_scenario = "stack_replacement_multiple"

        print(f"[SCENARIO] Classified as '{best_scenario}' (similarity: {max_similarity:.3f}, replacement_type: {replacement_type})")
        return best_scenario

    def retrieve_and_filter_rules(self, target_spec: Dict[str, Any], current_state: Dict[str, Any], top_k: int = TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
        """基于场景和embedding检索相关规则"""
        # 1. 场景分类
        scenario = self.classify_scenario_by_embedding(target_spec, current_state)

        # 2. 构建查询字符串
        target_structure = target_spec.get("target_structure", {})
        target_relationship = target_structure.get("relationship")
        current_structure = current_state.get("target_structure", {})
        current_relationship = current_structure.get("relationship") or "none"

        target_placements_raw = target_structure.get("placements", [])
        current_placements_raw = current_structure.get("placements", [])

        target_map = build_position_object_map(target_placements_raw)
        current_map = build_position_object_map(current_placements_raw)

        target_desc = format_placements_for_query(target_placements_raw)
        current_desc = format_placements_for_query(current_placements_raw)

        query_parts = [f"scenario: {scenario}"]

        if target_relationship:
            query_parts.append(f"target_relationship: {target_relationship}")
            if target_desc:
                query_parts.append(f"target_desc: {target_desc}")
            query_parts.append(f"current_relationship: {current_relationship}")
            if current_desc:
                query_parts.append(f"current_desc: {current_desc}")
            query_parts.append(f"target_objects: {len(target_placements_raw)} current_objects: {len(current_placements_raw)}")

            if target_relationship == "stacked":
                expected_positions = ["bottom", "middle", "top"]
                if len(target_map) == 2:
                    expected_positions = ["bottom", "top"]

                missing = [pos for pos in expected_positions if pos not in current_map]
                if missing:
                    query_parts.append(f"missing stack positions {' '.join(missing)}")
                elif current_relationship == "stacked":
                    mismatches = []
                    for pos in expected_positions:
                        tgt = target_map.get(pos)
                        cur = current_map.get(pos)
                        if tgt and cur and tgt != cur:
                            mismatches.append(f"{pos} wrong object")
                    if mismatches:
                        query_parts.extend(mismatches)
                    else:
                        query_parts.append("stack alignment already correct")
                else:
                    query_parts.append("different relationship need stacking")

            elif target_relationship in {"stacked_left", "stacked_middle", "stacked_right"}:
                target_obj = target_desc or ""
                query_parts.append(f"target_single_object: {target_obj}")
                if current_relationship != target_relationship:
                    query_parts.append("current relationship differs from single stack target")

            elif target_relationship in {
                "separated_left_right",
                "separated_front_back",
                "separate_horizontal",
                "separate_vertical",
                "stacked_and_separated_left",
                "stacked_and_separated_right"
            }:
                missing_positions = sorted(set(target_map.keys()) - set(current_map.keys()))
                if missing_positions:
                    query_parts.append(f"missing positions {' '.join(missing_positions)}")
                elif current_relationship != target_relationship:
                    query_parts.append("current relationship differs from target separation")
                else:
                    mismatches = []
                    for pos, tgt in target_map.items():
                        cur = current_map.get(pos)
                        if tgt and cur and tgt != cur:
                            mismatches.append(f"{pos} wrong object")
                    if mismatches:
                        query_parts.extend(mismatches)

            elif target_relationship == "pyramid":
                if current_relationship != "pyramid":
                    query_parts.append("current relationship differs from pyramid target")
        else:
            query_parts.append("legacy format state detected")

        query = " ".join(filter(None, query_parts))

        # 3. RAG检索
        rules = self.retrieve_relevant_rules(query, top_k=top_k+2)

        # 4. 基于场景过滤规则并去重
        filtered_rules = []
        seen_files = set()  # 防止重复规则

        def add_unique_rules(rule_list, max_count=None):
            """添加唯一规则，避免重复"""
            added = 0
            for rule in rule_list:
                file_path = rule['file_path']
                if file_path not in seen_files:
                    filtered_rules.append(rule)
                    seen_files.add(file_path)
                    added += 1
                    if max_count and added >= max_count:
                        break

        # 必须包含coordinate-free动作规则
        action_rules = [r for r in rules if 'coordinate_free_actions' in r['file_path']]
        add_unique_rules(action_rules, 1)

        # 必须包含统一输出格式规则
        unified_format_rules = [r for r in rules if 'unified_output_format' in r['file_path']]
        add_unique_rules(unified_format_rules, 1)

        # 基于关系类型过滤规则
        if target_relationship:
            if target_relationship == "stacked":
                # stacked关系专用规则
                stacked_rules = [r for r in rules if
                               'stacked' in r['file_path'] and
                               'separated' not in r['file_path']]  # 防止污染
                add_unique_rules(stacked_rules, 2)

            elif target_relationship in ["separated_left_right", "separated_front_back"]:
                # separated关系专用规则
                separated_rules = [r for r in rules if
                                 'separated' in r['file_path'] and
                                 'stacked' not in r['file_path']]  # 防止污染
                add_unique_rules(separated_rules, 2)

        # 添加执行顺序规则
        execution_rules = [r for r in rules if 'execution_order' in r['file_path']]
        add_unique_rules(execution_rules, 1)

        # 如果规则不足，添加其他核心规则
        if len(filtered_rules) < 3:
            other_core_rules = [r for r in rules if
                              'core_rules' in r['file_path'] and
                              r['file_path'] not in seen_files]
            add_unique_rules(other_core_rules, 2)

        # 强制注入关键规则
        enforced_keywords = [
            'core_rules/coordinate_free_actions.md',
            'core_rules/execution_order.md',
            'pattern_rules/bottom_up_building.md',
            'core_rules/unified_output_format.md',
            'output_format/json_structure.md'
        ]

        # Check if any stacking-related relationships are involved
        stacking_relationships = {
            "stacked_left", "stacked_middle", "stacked_right",
            "stacked", "stacked_and_separated_left", "stacked_and_separated_right"
        }

        target_structure = target_spec.get("target_structure", {})
        current_structure = current_state.get("target_structure", {})
        target_rel = target_structure.get("relationship")
        current_rel = current_structure.get("relationship")

        # Inject stacking extension rules if any stacking relationship is involved
        if (target_rel in stacking_relationships or
            current_rel in stacking_relationships):
            enforced_keywords.append('core_rules/stacking_extension.md')
            enforced_keywords.append('scenario_rules/stacking_extension_examples.md')

        # Inject stack replacement rules if replacement scenario detected
        if self._detect_stack_replacement_scenario(target_spec, current_state):
            mismatches = self._get_stack_mismatch_positions(target_spec, current_state)
            # Put position-specific docs first to increase salience
            if "middle" in mismatches:
                enforced_keywords.insert(0, 'pattern_rules/stack_replacement_middle.md')
            if "bottom" in mismatches:
                enforced_keywords.insert(0, 'pattern_rules/stack_replacement_bottom.md')
            enforced_keywords.append('pattern_rules/stack_replacement.md')

        relationship_keyword = None
        if target_relationship:
            if target_relationship in {"stacked_left", "stacked_middle", "stacked_right"}:
                relationship_keyword = 'relationship_rules/stacked.md'
            else:
                relationship_keyword = f'relationship_rules/{target_relationship}.md'
        if relationship_keyword:
            enforced_keywords.append(relationship_keyword)

        for keyword in enforced_keywords:
            if not any(keyword in rule['file_path'] for rule in filtered_rules):
                rule = self._get_rule_by_keyword(keyword)
                if rule:
                    filtered_rules.append(rule)

        # 保留强制规则并裁剪数量
        def is_enforced(rule: Dict[str, Any]) -> bool:
            return any(keyword in rule['file_path'] for keyword in enforced_keywords)

        mandatory_rules = [rule for rule in filtered_rules if is_enforced(rule)]
        optional_rules = [rule for rule in filtered_rules if not is_enforced(rule)]

        # 去除重复文件
        unique_rules = []
        seen_paths = set()
        for rule in mandatory_rules + optional_rules:
            path = rule['file_path']
            if path not in seen_paths:
                unique_rules.append(rule)
                seen_paths.add(path)

        if len(unique_rules) <= top_k:
            return unique_rules

        kept = []
        kept_paths = set()
        for rule in mandatory_rules:
            path = rule['file_path']
            if path not in kept_paths:
                kept.append(rule)
                kept_paths.add(path)

        for rule in optional_rules:
            if len(kept) >= top_k:
                break
            path = rule['file_path']
            if path not in kept_paths:
                kept.append(rule)
                kept_paths.add(path)

        return kept

    def _load_knowledge_base(self):
        """加载外部知识库文件"""
        kb_path = Path(__file__).parent / KNOWLEDGE_BASE_DIR
        if not kb_path.exists():
            raise FileNotFoundError(f"Knowledge base directory not found: {kb_path}")

        # 遍历所有.md文件
        for md_file in kb_path.rglob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析文件内容
            rule = self._parse_rule_file(content, md_file)
            if rule:
                self.knowledge_base.append(rule)
                self._rule_lookup[str(md_file)] = rule

        # 生成规则embeddings
        if self.knowledge_base:
            rule_texts = [rule['searchable_content'] for rule in self.knowledge_base]
            self.rule_embeddings = self.embedding_model.encode(rule_texts)
            print(f"Loaded {len(self.knowledge_base)} rules from knowledge base")

    def _parse_rule_file(self, content: str, file_path: Path) -> Dict[str, Any]:
        """解析单个规则文件"""
        lines = content.split('\n')
        rule = {
            'file_path': str(file_path),
            'title': '',
            'query_intent': '',
            'rule_content': content,
            'searchable_content': ''
        }

        # 提取标题
        for line in lines:
            if line.startswith('# '):
                rule['title'] = line[2:].strip()
                break

        # 提取查询意图
        intent_match = re.search(r'\*\*Query Intent\*\*:\s*(.+)', content)
        if intent_match:
            rule['query_intent'] = intent_match.group(1).strip()

        # 构建可搜索内容
        searchable_parts = [
            rule['title'],
            rule['query_intent'],
            content[:800]  # 前800字符作为上下文
        ]
        rule['searchable_content'] = ' '.join(filter(None, searchable_parts))

        return rule

    def _detect_stack_replacement_scenario(self, target_spec: Dict[str, Any], current_state: Dict[str, Any]) -> bool:
        """
        检测是否存在堆栈替换场景：
        - 当前位置有错误对象需要替换
        - 目标结构中同一位置需要不同对象
        """
        target_structure = target_spec.get("target_structure", {})
        current_structure = current_state.get("target_structure", {})

        target_rel = target_structure.get("relationship")
        current_rel = current_structure.get("relationship")

        # 只检测堆栈相关的关系
        stacking_relationships = {
            "stacked_left", "stacked_middle", "stacked_right",
            "stacked", "stacked_and_separated_left", "stacked_and_separated_right"
        }

        if target_rel not in stacking_relationships:
            return False

        # 如果当前状态也是堆栈关系，检查是否有位置对象不匹配
        if current_rel in stacking_relationships:
            target_placements = target_structure.get("placements", [])
            current_placements = current_structure.get("placements", [])

            target_map = build_position_object_map(target_placements)
            current_map = build_position_object_map(current_placements)

            # 检查是否有相同位置但不同对象的情况（替换场景）
            for position in ["bottom", "middle", "top"]:
                target_obj = target_map.get(position)
                current_obj = current_map.get(position)

                # 如果目标和当前都有这个位置，但对象不同，则是替换场景
                if target_obj and current_obj and target_obj != current_obj:
                    return True

        return False

    def _get_rule_by_keyword(self, keyword: str) -> Dict[str, Any]:
        """根据文件路径关键字获取规则副本。"""
        for path, rule in self._rule_lookup.items():
            if keyword in path:
                return rule.copy()
        return None

    def _analyze_replacement_complexity(self, target_spec: Dict[str, Any], current_state: Dict[str, Any]) -> str:
        """
        分析替换复杂度，返回具体的替换类型：
        - top_only: 仅顶层需要替换（最简单）
        - middle_only: 仅中层需要替换（中等复杂）
        - bottom_only: 仅底层需要替换（最复杂）
        - multiple: 多层需要替换（复杂重建）
        - extension: 堆栈扩展（简单添加）
        - none: 无需替换
        """
        target_structure = target_spec.get("target_structure", {})
        current_structure = current_state.get("target_structure", {})

        if not isinstance(target_structure, dict) or not isinstance(current_structure, dict):
            return "none"

        target_rel = target_structure.get("relationship")
        current_rel = current_structure.get("relationship")

        # 只处理堆栈相关关系
        stacking_relationships = {
            "stacked_left", "stacked_middle", "stacked_right",
            "stacked", "stacked_and_separated_left", "stacked_and_separated_right"
        }

        if target_rel not in stacking_relationships:
            return "none"

        t_map = build_position_object_map(target_structure.get("placements", []))
        c_map = build_position_object_map(current_structure.get("placements", []))

        # 检测扩展场景（层数增加）
        if current_rel in stacking_relationships and len(c_map) < len(t_map):
            # 检查现有层是否正确
            mismatches = []
            for pos in c_map:
                if pos in t_map and t_map[pos] != c_map[pos]:
                    mismatches.append(pos)
            if not mismatches:
                return "extension"

        # 检测替换场景
        mismatches = []
        for pos in ("bottom", "middle", "top"):
            t_obj = t_map.get(pos)
            c_obj = c_map.get(pos)
            if t_obj and c_obj and t_obj != c_obj:
                mismatches.append(pos)

        if not mismatches:
            return "none"
        elif len(mismatches) == 1:
            return f"{mismatches[0]}_only"
        else:
            return "multiple"

    def _get_stack_mismatch_positions(self, target_spec: Dict[str, Any], current_state: Dict[str, Any]) -> List[str]:
        """Return stack positions where target and current differ (both defined)."""
        target_structure = target_spec.get("target_structure", {})
        current_structure = current_state.get("target_structure", {})

        if not isinstance(target_structure, dict) or not isinstance(current_structure, dict):
            return []

        if target_structure.get("relationship") != "stacked" or current_structure.get("relationship") != "stacked":
            return []

        t_map = build_position_object_map(target_structure.get("placements", []))
        c_map = build_position_object_map(current_structure.get("placements", []))

        mismatches: List[str] = []
        for pos in ("bottom", "middle", "top"):
            t_obj = t_map.get(pos)
            c_obj = c_map.get(pos)
            if t_obj and c_obj and t_obj != c_obj:
                mismatches.append(pos)
        return mismatches

    def _build_stacked_system_prompt(self, replacement_type: str, target_spec: Dict[str, Any] = None, current_state: Dict[str, Any] = None) -> List[str]:
        """
        根据替换类型构建分层的系统提示词
        支持未来扩展到其他目标形态

        Args:
            replacement_type: 替换类型 (top_only, middle_only, bottom_only, etc.)
            target_spec: 目标规范 (未来扩展用)
            current_state: 当前状态 (未来扩展用)
        """
        # 基础通用提示词（所有堆栈任务共享）
        base_parts = [
            "/no_think",
            "",
            "You are a precise object reordering planner with access to relevant rules.",
            "",
            "🔴 MANDATORY: Output ONLY strict JSON with no additional text, explanations, or <think> tags.",
            "🔴 CRITICAL: Each action MUST have 'object' field at TOP LEVEL (not inside from/to).",
            "🔴 CRITICAL: Use pure object names (e.g., 'blue cube') without descriptive prefixes.",
            "🔴 CRITICAL: Use correct key names: from/to must use 'type' not 'position' for scattered objects.",
            "",
            "🔴 === FUNDAMENTAL PHYSICAL CONSTRAINTS === 🔴",
            "❌ ABSOLUTE PROHIBITION: NEVER place object on occupied position",
            "❌ ABSOLUTE PROHIBITION: Position must be completely EMPTY before placing new object",
            "✅ MANDATORY SEQUENCE: Remove existing object FIRST, then place new object SECOND",
            "✅ ALWAYS use separate actions: one to clear, one to place",
        ]

        # 根据替换类型添加特定的基础约束
        if replacement_type == "bottom_only":
            base_parts.extend([
                "",
                "🔴 === BOTTOM REPLACEMENT CRITICAL OVERRIDE === 🔴",
                "⚠️⚠️⚠️ BOTTOM LAYER IS COMPLETELY INACCESSIBLE WHILE UPPER LAYERS EXIST",
                "⚠️⚠️⚠️ YOU MUST CLEAR EVERY SINGLE UPPER LAYER BEFORE TOUCHING BOTTOM",
                "⚠️⚠️⚠️ NO EXCEPTIONS - NO SHORTCUTS - NO DIRECT ACCESS",
                "",
                "❌ ABSOLUTE PROHIBITIONS:",
                "❌ NEVER access bottom while middle layer exists (even if middle is correct)",
                "❌ NEVER access bottom while top layer exists (even if top is correct)",
                "❌ NEVER skip clearing middle layer - it BLOCKS bottom access",
                "❌ NEVER think 'middle is correct so I don't need to move it'",
                "",
                "✅ MANDATORY PHYSICS:",
                "✅ Middle layer PHYSICALLY BLOCKS bottom access - must be cleared",
                "✅ Top layer PHYSICALLY BLOCKS middle access - must be cleared first",
                "✅ EXACT sequence: Clear top → Clear middle → Access bottom → Rebuild all",
                "✅ ALL upper layers to buffer (for restoration), wrong bottom to scattered",
                "",
            ])
        else:
            base_parts.extend([
                "",
                "🔴 === OBJECT LIFECYCLE MANAGEMENT === 🔴",
                "📦 BUFFER (Temporary Storage): Objects that EXIST in target but are currently misplaced",
                "  - Use move_to_buffer → move_from_buffer pattern",
                "  - These objects MUST be restored to correct positions",
                "",
                "🗑️ SCATTERED (Permanent Removal): Objects that DO NOT exist anywhere in target",
                "  - Use move_to_position → scattered (no restoration)",
                "  - These objects are permanently removed from stack",
                "",
            ])

        # 根据替换类型添加特定指导
        if replacement_type == "top_only":
            specific_parts = [
                "🔴 === TOP LAYER REPLACEMENT (SIMPLE) === 🔴",
                "✅ SCENARIO: Only top layer needs correction - SIMPLEST case",
                "✅ PATTERN: Remove-then-Place (exactly 2 steps)",
                "✅ NO BLOCKING: Top layer is directly accessible",
                "",
                "🔴 REPLACEMENT SEQUENCE (MANDATORY ORDER):",
                "  1. move_to_position: wrong_top_object → scattered (FIRST: remove current occupant)",
                "  2. move_to_position: correct_top_object → top (SECOND: place target object)",
                "",
                "🔴 CRITICAL PHYSICAL CONSTRAINT:",
                "❌ FORBIDDEN: Placing object on occupied position (position must be empty first)",
                "✅ REQUIRED: ALWAYS clear position before placing new object",
                "✅ REQUIRED: Two separate actions - NEVER combine remove+place",
                "",
                "🔴 CRITICAL RULES:",
                "- Step 1 MUST clear the position (wrong object → scattered)",
                "- Step 2 MUST place target object (correct object → position)",
                "- NO buffer needed (wrong object goes to scattered permanently)",
                "- NO skipping: even simple replacement needs both steps",
                "",
                "EXAMPLE - Current: yellow cube at top, Target: red cube at top:",
                '  Step 1: move_to_position yellow cube from top → scattered (clear position)',
                '  Step 2: move_to_position red cube from scattered → top (place target)',
            ]
        elif replacement_type == "middle_only":
            specific_parts = [
                "🔴 === MIDDLE LAYER REPLACEMENT (COMPLEX) === 🔴",
                "⚠️ SCENARIO: Middle layer blocked by top layer",
                "⚠️ PATTERN: Clear-Replace-Restore (4 steps)",
                "⚠️ BLOCKING: Must clear top to access middle",
                "",
                "🔴 REPLACEMENT SEQUENCE:",
                "  1. move_to_buffer: correct_top_object → B1 (clear blocking layer)",
                "  2. move_to_position: wrong_middle_object → scattered (remove unwanted)",
                "  3. move_to_position: correct_middle_object → middle (place target)",
                "  4. move_from_buffer: correct_top_object → top (restore needed layer)",
                "",
                "🔴 PHYSICAL CONSTRAINTS:",
                "- CANNOT access middle while top exists",
                "- MUST clear top first (even if top is correct)",
                "- MUST restore top after middle replacement",
            ]
        elif replacement_type == "bottom_only":
            specific_parts = [
                "🔴 === BOTTOM LAYER REPLACEMENT - MANDATORY 6-STEP SEQUENCE === 🔴",
                "",
                "⚠️⚠️⚠️ ABSOLUTE REQUIREMENT: EXACTLY 6 STEPS - NO SHORTCUTS ⚠️⚠️⚠️",
                "",
                "🔴 STEP-BY-STEP MANDATORY SEQUENCE:",
                "",
                "STEP 1: CLEAR TOP LAYER (MANDATORY - BLOCKS MIDDLE ACCESS)",
                '{"step": 1, "action": "move_to_buffer", "object": "red cube", "from": {"type": "stack", "position": "top"}, "to": {"type": "buffer", "slot": "B1"}, "reason": "Clear top to access middle"}',
                "",
                "STEP 2: CLEAR MIDDLE LAYER (MANDATORY - BLOCKS BOTTOM ACCESS)",
                '{"step": 2, "action": "move_to_buffer", "object": "green cube", "from": {"type": "stack", "position": "middle"}, "to": {"type": "buffer", "slot": "B2"}, "reason": "Clear middle to access bottom"}',
                "",
                "STEP 3: REMOVE WRONG BOTTOM (NOW ACCESSIBLE)",
                '{"step": 3, "action": "move_to_position", "object": "yellow cube", "from": {"type": "stack", "position": "bottom"}, "to": {"type": "scattered"}, "reason": "Remove incorrect bottom object"}',
                "",
                "STEP 4: PLACE CORRECT BOTTOM (FOUNDATION)",
                '{"step": 4, "action": "move_to_position", "object": "blue cube", "from": {"type": "scattered"}, "to": {"type": "stack", "position": "bottom"}, "reason": "Place correct bottom foundation"}',
                "",
                "STEP 5: RESTORE MIDDLE LAYER (REBUILD FROM BOTTOM UP)",
                '{"step": 5, "action": "move_from_buffer", "object": "green cube", "from": {"type": "buffer", "slot": "B2"}, "to": {"type": "stack", "position": "middle"}, "reason": "Restore middle layer"}',
                "",
                "STEP 6: RESTORE TOP LAYER (COMPLETE STACK)",
                '{"step": 6, "action": "move_from_buffer", "object": "red cube", "from": {"type": "buffer", "slot": "B1"}, "to": {"type": "stack", "position": "top"}, "reason": "Restore top layer"}',
                "",
                "🔴 CRITICAL VALIDATIONS:",
                "❌ NEVER skip any step",
                "❌ NEVER change the order",
                "❌ NEVER access bottom directly (always clear above first)",
                "❌ NEVER use non-existent actions like 'move_from_position'",
                "✅ MUST follow exact 6-step sequence above",
                "✅ MUST use proper action names: move_to_buffer, move_from_buffer, move_to_position",
            ]
        elif replacement_type == "extension":
            specific_parts = [
                "🔴 === STACK EXTENSION (SIMPLE) === 🔴",
                "✅ SCENARIO: Adding layers to existing correct stack",
                "✅ PATTERN: Direct placement (minimal actions)",
                "✅ NO REPLACEMENT: Existing objects are correct",
                "",
                "🔴 EXTENSION LOGIC:",
                "- Place new object at 'top' position",
                "- Existing layers automatically adjust (no explicit moves needed)",
                "- 2→3 layers: just place third object at top",
            ]
        elif replacement_type == "multiple":
            specific_parts = [
                "🔴 === MULTIPLE LAYER REPLACEMENT (COMPLEX REBUILD) === 🔴",
                "⚠️⚠️⚠️ SCENARIO: Multiple layers need correction",
                "⚠️⚠️⚠️ PATTERN: Strategic reconstruction",
                "⚠️⚠️⚠️ APPROACH: Clear all, then rebuild bottom-up",
            ]
        else:  # none or unknown
            specific_parts = [
                "🔴 === GENERAL STACK OPERATION === 🔴",
                "✅ SCENARIO: Standard stack arrangement",
                "✅ FOLLOW: Bottom-up building principles",
            ]

        # 通用结束部分
        ending_parts = [
            "",
            "TASK: Generate action plan for stacked arrangement with coordinate-free actions.",
            "",
            "🔴 MANDATORY ACTION FORMAT:",
            "- Every action MUST have: step, action, object, from, to, reason",
            "- 'object' field MUST be at top level, NOT inside from/to",
            "- Use 'type': 'scattered' NOT 'position': 'scattered'",
            "- Use specific action names: move_to_position, move_to_buffer, move_from_buffer",
            "",
            "OUTPUT TEMPLATE:",
            '{"status": "success", "plan": [{"step": 1, "action": "move_to_position", "object": "blue cube", "from": {"type": "scattered"}, "to": {"type": "stack", "position": "bottom"}, "reason": "Place at position"}], "final_expected": {"target_structure": {"relationship": "stacked", "placements": [{"position": "bottom", "object 1": "blue cube"}, {"position": "middle", "object 2": "green cube"}, {"position": "top", "object 3": "red cube"}]}}}',
            "",
            "/no_think",
        ]

        return base_parts + specific_parts + ending_parts

    def retrieve_relevant_rules(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
        """基于语义相似度检索相关规则"""
        if not self.knowledge_base or self.rule_embeddings is None:
            return []

        # 对查询进行embedding
        query_embedding = self.embedding_model.encode([query])

        # 计算余弦相似度
        similarities = cosine_similarity(query_embedding, self.rule_embeddings).flatten()

        # 获取top_k最相关的规则
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        relevant_rules = []
        for idx in top_indices:
            rule = self.knowledge_base[idx].copy()
            rule['similarity_score'] = similarities[idx]
            relevant_rules.append(rule)

        return relevant_rules

    def build_rag_prompt(self, target_spec: Dict[str, Any], current_state: Dict[str, Any]) -> Tuple[str, str]:
        """构建基于RAG的prompt"""
        # 选择相关规则
        relevant_rules = self.retrieve_and_filter_rules(target_spec, current_state, top_k=TOP_K_RETRIEVAL)

        # 调试输出
        print(f"Retrieved {len(relevant_rules)} rules:")
        for i, rule in enumerate(relevant_rules):
            title = rule.get('title', Path(rule.get('file_path','')).name)
            print(f"  Rule {i+1}: {title}")

        # 检查输出格式类型
        target_structure = target_spec.get("target_structure", {})
        target_relationship = target_structure.get("relationship")

        # 构建系统提示词
        if target_relationship:
            # 新格式：关系型输出
            if target_relationship == "stacked":
                # 分析替换复杂度以选择合适的提示词
                replacement_type = self._analyze_replacement_complexity(target_spec, current_state)
                system_parts = self._build_stacked_system_prompt(replacement_type, target_spec, current_state)
            elif target_relationship in ["separated_left_right", "separated_front_back"]:
                system_parts = [
                    "/no_think",
                    "",
                    "You are a precise object reordering planner with access to relevant rules.",
                    "",
                    "🔴 MANDATORY: Output ONLY strict JSON with no additional text, explanations, or <think> tags.",
                    "🔴 CRITICAL: Each action MUST have 'object' field at TOP LEVEL (not inside from/to).",
                    "🔴 CRITICAL: Use pure object names (e.g., 'blue cube') without descriptive prefixes.",
                    "🔴 CRITICAL: Use correct key names: from/to must use 'type' not 'position' for scattered objects.",
                    "🔴 REQUIRED: Handle separated arrangements with buffer slots B1/B2/B3 when needed.",
                    "🔴 BUFFER: Use predefined buffer slots B1, B2, B3 for temporary storage (coordinates handled internally).",
                    "🔴 FINAL EXPECTED: Success outputs MUST include final_expected.target_structure with all required positions filled.",
                    "🔴 UNIQUE PLACEMENT: Do not place the same object into arrangement positions multiple times.",
                    "",
                    f"TASK: Generate action plan for {target_relationship} arrangement with coordinate-free actions.",
                    "",
                    "🔴 MANDATORY ACTION FORMAT:",
                    "- Every action MUST have: step, action, object, from, to, reason",
                    "- 'object' field MUST be at top level, NOT inside from/to",
                    "- Use 'type': 'scattered' NOT 'position': 'scattered'",
                    "- Use specific action names: move_to_position, move_to_buffer, move_from_buffer",
                    "- Ensure each required position (left/right/front/back) is populated exactly once",
                    "",
                    "OUTPUT TEMPLATE:",
                    '{"status": "success", "plan": [{"step": 1, "action": "move_to_position", "object": "blue cube", "from": {"type": "scattered"}, "to": {"type": "arrangement", "position": "left"}, "reason": "Place object at position"}], "final_expected": {"target_structure": {"relationship": "separated_left_right", "placements": [{"position": "left", "object 1": "blue cube"}, {"position": "right", "object 2": "red cube"}]}}}',
                    "",
                    "/no_think",
                ]
            else:
                system_parts = [
                    "/no_think",
                    "",
                    "You are a precise object reordering planner with access to relevant rules.",
                    "",
                    "🔴 MANDATORY: Output ONLY strict JSON with no additional text, explanations, or <think> tags.",
                    "🔴 CRITICAL: Use pure object names without descriptive prefixes.",
                    "🔴 FINAL EXPECTED: Success outputs MUST include final_expected.target_structure matching target_spec.",
                    "",
                    f"TASK: Generate action plan for {target_relationship} arrangement.",
                    "",
                    "/no_think",
                ]
        else:
            # 旧格式：坐标型输出
            system_parts = [
                "/no_think",
                "",
                "You are a precise cube reordering planner with access to relevant rules.",
                "",
                "🔴 MANDATORY: Output ONLY strict JSON with no additional text, explanations, or <think> tags.",
                "🔴 CRITICAL: All coordinates must be integers, not expressions.",
                "🔴 REQUIRED: Follow bottom-up building order (bottom → middle → top).",
                "🔴 COMPLETE: Must include both 'plan' and 'final_expected' fields for success status.",
                "",
                "TASK: Generate action plan to transform current_state into target_spec configuration.",
                "",
                "OUTPUT TEMPLATE:",
                '{"status": "success", "plan": [...], "final_expected": {"bottom": {...}, "middle": {...}, "top": {...}}}',
                "",
                "/no_think",
            ]

        # 按优先级重新排序规则：物理约束规则优先
        priority_rules = []
        other_rules = []

        for rule in relevant_rules:
            file_path = rule['file_path']
            # 高优先级：物理约束和替换相关规则
            if any(keyword in file_path for keyword in [
                'stack_replacement', 'stacking_extension', 'physical_constraint',
                'coordinate_free_actions', 'execution_order'
            ]):
                priority_rules.append(rule)
            else:
                other_rules.append(rule)

        # 首先添加高优先级规则
        if priority_rules:
            system_parts.append("🔴 === CRITICAL PHYSICAL CONSTRAINT RULES === 🔴")
            for i, rule in enumerate(priority_rules):
                system_parts.append(f"--- PRIORITY Rule {i+1}: {rule.get('title', 'Physical Constraint Rule')} ---")
                system_parts.append(rule['rule_content'])
                system_parts.append("")

        # 然后添加其他规则
        if other_rules:
            system_parts.append("--- Additional Supporting Rules ---")
            for i, rule in enumerate(other_rules):
                system_parts.append(f"--- Rule {i+1}: {rule.get('title', 'Supporting Rule')} ---")
                system_parts.append(rule['rule_content'])
                system_parts.append("")

        system_prompt = "\n".join(system_parts)

        # 构建用户提示词
        user_prompt = (
            "TARGET_SPEC:\n"
            f"{json.dumps(target_spec, indent=2)}\n"
            "\n"
            "CURRENT_STATE:\n"
            f"{json.dumps(current_state, indent=2)}\n"
            "\n"
            "Generate the JSON action plan to transform current_state into target_spec.\n"
            "Output ONLY the JSON, no additional text."
        )

        return system_prompt, user_prompt

def _extract_first_json_object(text: str) -> str:
    """从模型输出中提取第一个顶层完整的JSON对象文本。

    处理情况：
    - 去除```json/``` 包裹、<think> 思考内容
    - 模型在JSON后继续输出额外文本（Extra data）
    - 模型返回多个JSON对象时，仅取第一个完整对象
    - 忽略字符串内的大括号
    """
    t = text.strip()

    # 移除 <think> 标签内容
    t = re.sub(r'<think>.*?</think>', '', t, flags=re.DOTALL).strip()

    # 去除markdown代码块包裹
    if t.startswith("```json") and t.endswith("```"):
        t = t[7:-3].strip()
    elif t.startswith("```") and t.endswith("```"):
        t = t[3:-3].strip()

    # 从第一个 '{' 开始尝试提取一个平衡的 JSON 对象
    start = t.find('{')
    if start == -1:
        return t  # 交由上层报错

    in_str = False
    escape = False
    depth = 0
    end_idx = -1

    for i in range(start, len(t)):
        ch = t[i]

        if in_str:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == '"':
                in_str = False
            continue

        # 非字符串上下文
        if ch == '"':
            in_str = True
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end_idx = i
                break

    if end_idx != -1:
        return t[start:end_idx+1]

    # 没有找到完整闭合，尝试到最后一个 '}' 为止（尽力而为）
    last_brace = t.rfind('}')
    if last_brace != -1 and last_brace > start:
        return t[start:last_brace+1]

    # 直接返回原文，交由json解析报错
    return t


def parse_and_validate(json_text: str) -> Dict[str, Any]:
    """解析并验证JSON输出（鲁棒版本）"""
    # 先尝试直接解析
    t = json_text.strip()
    try:
        data = json.loads(t)
    except Exception:
        # 提取首个完整 JSON 对象再解析
        candidate = _extract_first_json_object(t)
        data = json.loads(candidate)

    # 基础验证
    # 检查是否为纯关系型输出（只有target_structure）
    if "target_structure" in data and "status" not in data:
        # 纯关系型输出验证
        target_structure = data["target_structure"]
        validate_target_structure_payload(target_structure)

    # 检查是否为动作计划输出（包含status和plan）
    elif "status" in data:
        status = data["status"]
        if status not in ["success", "blocked"]:
            raise ValueError(f"Invalid status: {status}")

        if status == "success":
            if "plan" not in data:
                raise ValueError("Missing 'plan' key for success status")

            # 验证plan中的动作
            plan = data["plan"]
            if not isinstance(plan, list):
                raise ValueError("Plan must be a list of actions")

            # 先对动作进行容错规范化（将别名/错误放置的字段提升/修正）
            for action in plan:
                if "step" not in action or "action" not in action:
                    raise ValueError("Each action must have 'step' and 'action' keys")

                # 1) 规范化 from/to 的 scattered 表达：禁止 position: scattered，统一为 type: scattered
                for endpoint_key in ("from", "to"):
                    if endpoint_key in action and isinstance(action[endpoint_key], dict):
                        ep = action[endpoint_key]
                        if ep.get("position") == "scattered" and "type" not in ep:
                            ep["type"] = "scattered"
                            del ep["position"]

                # 2) 提升 object 字段：允许从 color 或 from.color/from.object 提升至顶层
                if "object" not in action:
                    obj = None
                    if "color" in action and action["color"]:
                        # 缺省物体类型按领域设定为 cube
                        obj = f"{action['color']} cube"
                    else:
                        fr = action.get("from", {}) or {}
                        to = action.get("to", {}) or {}
                        if isinstance(fr, dict):
                            obj = fr.get("object") or (f"{fr.get('color')} cube" if fr.get('color') else None)
                        if obj is None and isinstance(to, dict):
                            obj = to.get("object") or (f"{to.get('color')} cube" if to.get('color') else None)

                    if obj:
                        action["object"] = obj
                        # 清理冗余 color 字段，避免二义性
                        action.pop("color", None)
                        if isinstance(action.get("from"), dict):
                            action["from"].pop("color", None)
                            action["from"].pop("object", None)
                        if isinstance(action.get("to"), dict):
                            action["to"].pop("color", None)
                            action["to"].pop("object", None)

                # 3) 最终强制要求 object 存在
                if "object" not in action or not action["object"]:
                    raise ValueError("Each action must specify an 'object'")

                # 检查buffer slot引用
                action_type = action["action"]
                if action_type in ["move_to_buffer", "move_from_buffer"]:
                    if action_type == "move_to_buffer":
                        if "to" not in action or "slot" not in action["to"]:
                            raise ValueError("move_to_buffer action must specify target buffer slot")
                        slot = action["to"]["slot"]
                        if slot not in BUFFER_SLOTS:
                            raise ValueError(f"Invalid buffer slot: {slot}. Must be one of {list(BUFFER_SLOTS.keys())}")
                    elif action_type == "move_from_buffer":
                        if "from" not in action or "slot" not in action["from"]:
                            raise ValueError("move_from_buffer action must specify source buffer slot")
                        slot = action["from"]["slot"]
                        if slot not in BUFFER_SLOTS:
                            raise ValueError(f"Invalid buffer slot: {slot}. Must be one of {list(BUFFER_SLOTS.keys())}")

            enforce_plan_consistency(plan)

            if "final_expected" not in data:
                raise ValueError("Success status requires 'final_expected' field")

            # 验证final_expected
            if "final_expected" in data:
                final_expected = data["final_expected"]
                if "target_structure" in final_expected:
                    validate_target_structure_payload(final_expected["target_structure"])
                elif "relationship" in final_expected and "placements" in final_expected:
                    # 兼容旧格式
                    validate_target_structure_payload({
                        "relationship": final_expected["relationship"],
                        "placements": final_expected["placements"]
                    })
        elif status == "blocked":
            if "reason" not in data:
                raise ValueError("Missing 'reason' key for blocked status")
    else:
        raise ValueError("JSON must contain either 'target_structure' (for relationship output) or 'status' (for action plan output)")

    return data

def validate_target_consistency(result: Dict[str, Any], target_spec: Dict[str, Any]) -> bool:
    """验证结果与目标规范的一致性"""
    if "target_structure" not in target_spec:
        return True  # 旧格式跳过验证

    target_structure = target_spec["target_structure"]
    target_relationship = target_structure.get("relationship")
    target_position_map = build_position_object_map(target_structure.get("placements", []))
    target_objects = collect_objects_list(target_structure.get("placements", []))

    # 检查final_expected
    if "final_expected" in result:
        final_expected = result["final_expected"]
        if "target_structure" in final_expected:
            final_structure = final_expected["target_structure"]
        elif "relationship" in final_expected and "placements" in final_expected:
            final_structure = final_expected
        else:
            final_structure = None

        if final_structure:
            if final_structure.get("relationship") != target_relationship:
                print(f"[CONSISTENCY] Relationship mismatch: expected {target_relationship}, got {final_structure.get('relationship')}")
                return False

            final_position_map = build_position_object_map(final_structure.get("placements", []))
            final_objects = collect_objects_list(final_structure.get("placements", []))

            if target_position_map:
                for position, expected_object in target_position_map.items():
                    if position not in final_position_map:
                        print(f"[CONSISTENCY] Missing position: {position}")
                        return False
                    if final_position_map[position] != expected_object:
                        print(f"[CONSISTENCY] Object mismatch at {position}: expected {expected_object}, got {final_position_map[position]}")
                        return False
            else:
                if final_objects != target_objects:
                    print(f"[CONSISTENCY] Object list mismatch: expected {target_objects}, got {final_objects}")
                    return False

            # 若为 stacked，额外校验计划的自底向上顺序（忽略缓冲动作）
            if target_relationship == "stacked" and "plan" in result and isinstance(result["plan"], list):
                idx = {"bottom": None, "middle": None, "top": None}
                for i, act in enumerate(result["plan"]):
                    to = act.get("to") if isinstance(act, dict) else None
                    if isinstance(to, dict) and to.get("type") == "stack":
                        pos = to.get("position")
                        if pos in idx and idx[pos] is None:
                            idx[pos] = i
                order = [p for p in ["bottom", "middle", "top"] if idx[p] is not None]
                if order and order != sorted(order, key=lambda p: ["bottom", "middle", "top"].index(p)):
                    print(f"[CONSISTENCY] Stacked order invalid: got indices {idx}")
                    return False

            print("[CONSISTENCY] Target consistency validation passed")
            return True

    # 检查target_structure输出（纯关系型）
    elif "target_structure" in result:
        result_structure = result["target_structure"]
        if result_structure.get("relationship") != target_relationship:
            print(f"[CONSISTENCY] Relationship mismatch: expected {target_relationship}, got {result_structure.get('relationship')}")
            return False

        result_position_map = build_position_object_map(result_structure.get("placements", []))
        result_objects = collect_objects_list(result_structure.get("placements", []))

        if target_position_map:
            for position, expected_object in target_position_map.items():
                if position not in result_position_map:
                    print(f"[CONSISTENCY] Missing position: {position}")
                    return False
                if result_position_map[position] != expected_object:
                    print(f"[CONSISTENCY] Object mismatch at {position}: expected {expected_object}, got {result_position_map[position]}")
                    return False
        else:
            if result_objects != target_objects:
                print(f"[CONSISTENCY] Object list mismatch: expected {target_objects}, got {result_objects}")
                return False

        print("[CONSISTENCY] Target consistency validation passed")
        return True

    return True

def generate_replan(target_spec: Dict[str, Any], current_state: Dict[str, Any]):
    """使用真正的RAG生成replan结果"""
    # 初始化RAG系统
    rag_system = ReplanRAGSystem()

    # 加载语言模型
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    def _generate_once(system_prompt: str, user_prompt: str) -> Tuple[Dict[str, Any], str]:
        """执行一次生成"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer([text], return_tensors="pt").to(model.device)

        with sdpa_kernel(SDPBackend.FLASH_ATTENTION):
            outputs = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=DO_SAMPLE,
                temperature=TEMPERATURE,
                top_p=TOP_P
            )

        output_tokens = outputs[0][inputs.input_ids.size(1):]
        raw = tokenizer.decode(output_tokens, skip_special_tokens=True)

        try:
            result = parse_and_validate(raw)
            return result, raw
        except Exception as e:
            print(f"Parse error: {e}")
            return None, raw

    # 生成
    system_prompt, user_prompt = rag_system.build_rag_prompt(target_spec, current_state)
    result, raw = _generate_once(system_prompt, user_prompt)

    if result is None:
        print(f"Generation failed. Full Raw: {repr(raw)}")
        return None

    # 目标一致性验证
    if not validate_target_consistency(result, target_spec):
        print("Target consistency validation failed. Attempting retry...")
        # 可以在这里添加重试逻辑，暂时先输出警告
        print("Warning: Generated result does not match target specification")

    # 美化输出
    formatted = json.dumps(result, indent=2, ensure_ascii=False)
    print(formatted)
    return result

# =============== 测试入口 ===============
if __name__ == "__main__":
    print("=== Test 1: Stacked Relationship - All Scattered ===")
    target_spec_stacked = {
        "target_structure": {
            "relationship": "stacked",
            "placements": [
                {"position": "bottom", "object 1": "blue cube"},
                {"position": "middle", "object 2": "green cube"},
                {"position": "top", "object 3": "red cube"}
            ]
        }
    }

    # current_state_stacked = {
    #     "target_structure": {
    #         "relationship": "stacked",
    #         "placements": [
    #             {"position": "bottom", "object 1": "blue cube"},
    #         ]
    #     }
    # }

    current_state_stacked = {
        "target_structure": {
            "relationship": "stacked",
            "placements": [
                {"position": "bottom", "object 1": "yellow cube"},
                {"position": "middle", "object 2": "green cube"},
                {"position": "top", "object 3": "red cube"}
            ]
        }
    }


    result_stacked = generate_replan(target_spec_stacked, current_state_stacked)

    # print("\n" + "=" * 50 + "\n")

    # print("=== Test 2: Stacked Relationship - Partial Stack ===")
    # current_state_stacked_2 = {
    #     "target_structure": {
    #         "relationship": "stacked",
    #         "placements": [
    #             {"position": "bottom", "object 1": "blue cube"},
    #             {"position": "middle", "object 2": "green cube"},
    #             {"position": "top", "object 3": "green cube"}
    #         ]
    #     }
    # }

    # result_stacked_2 = generate_replan(target_spec_stacked, current_state_stacked_2)
