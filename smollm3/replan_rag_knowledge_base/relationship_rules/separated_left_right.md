# Separated Left-Right Relationship Rule

**Query Intent**: separated left right arrangement, horizontal separation, side-by-side layout

## Relationship Definition
- 两个物体：仅包含 `left` 与 `right` 两个位置。
- 三个物体：按 `left`、`middle`、`right` 排列，对应 `relationship = "separate_horizontal"`。

## Required JSON Formats

### 两个物体（relationship = `separated_left_right`）
```json
{
  "target_structure": {
    "relationship": "separated_left_right",
    "placements": [
      { "position": "left",  "object 1": "green cube" },
      { "position": "right", "object 2": "red cube" }
    ]
  }
}
```

### 三个物体（relationship = `separate_horizontal`）
```json
{
  "target_structure": {
    "relationship": "separate_horizontal",
    "placements": [
      { "position": "left",   "object 1": "blue cube" },
      { "position": "middle", "object 2": "red block" },
      { "position": "right",  "object 3": "green cube" }
    ]
  }
}
```

## Critical Constraints
- `placements` 中的对象字段命名遵循 `object 1/2/3`。
- 不得添加 `object`、`color` 等额外键。
- position 值限定为 `left` / `middle` / `right`。
- 输出必须为纯 JSON，不含解释或 Markdown。
- 与其他关系的格式不得混用；若目标是 3 物体但位置不在 left/middle/right，视为无效输入。

## Execution Guidance
- 处理两物体时，只返回所示两个位置；无需 middle。
- 三物体必须按 left → middle → right 的逻辑描述，但数组顺序可调整。
- 保持对象描述与输入一致，除非上游明确要求修改。
