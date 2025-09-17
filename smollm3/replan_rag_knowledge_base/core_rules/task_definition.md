# Task Definition - Object Relationship Planner

**Query Intent**: replan task, cube/object reordering, multi-relationship target configuration, JSON structure compliance

**CRITICAL TASK DEFINITION**: 根据目标 `target_structure`（严格遵循《输入的json类型与格式总结》）对当前物体状态进行规划，生成可执行动作方案并给出最终期望结构。

## MANDATORY Task Requirements

**INPUT ANALYSIS**:
- `target_structure`: 关系类型仅来自文档列举集合（单物体 stack、stacked、separated_left_right、separated_front_back、pyramid、stacked_and_separated_left/right、separate_horizontal、separate_vertical）。
- `current_state`: 描述当前关系（可能为 `none`）、已有堆叠、散落物体、缓冲占用等信息。
- 物体数量 ≤ 3，与 `target_structure.placements` 数量一致。

**OUTPUT REQUIREMENTS**:
- `status` + `plan` + `final_expected` 三段式 JSON（参照 `json_structure` 规则）。
- `final_expected.target_structure` 必须与目标关系格式完全一致，并使用相同的字段命名（`object` 或 `object 1/2/3`）。
- 动作列表 `plan` 采用坐标无关的动作类型并保持 `object` 顶层字段。

## CORE OBJECTIVE
- 在遵守文档格式的前提下，将当前配置转换为目标关系结构。
- 处理所有文档支持的关系类型，而不仅限于单一堆叠。

## CRITICAL COMPLIANCE
- 遇到 stack 类目标时遵循自底向上的顺序；分离类目标确保 left/right/front/back 顺序正确。
- 使用标准缓冲槽 `B1/B2/B3` 进行临时存放（如需要）。
- 保持对象描述与输入一致，除非任务明确要求替换。
- 若目标结构已满足，输出空计划但仍提供 `final_expected`。

## SCOPE CONSTRAINTS
- 支持 1~3 个物体的所有文档定义关系。
- 动作步数控制在可执行范围内（建议 ≤8）。
- 不使用坐标、角度等额外数值信息。

## SUCCESS CRITERIA
1. `final_expected.target_structure` 与目标完全一致（关系、字段、对象描述）。
2. `plan` 中每个动作可执行且遵循动作 schema。
3. 不出现与文档相冲突的字段或额外输出。
4. 针对特定关系类型执行正确的顺序与缓冲策略。

## FAILURE CONDITIONS
- `target_structure` 中字段命名不符合文档要求。
- 动作或最终结构与目标不一致。
- 引入未定义的关系或额外字段。
- 缺少必须的 action 字段或缓冲槽非法。
