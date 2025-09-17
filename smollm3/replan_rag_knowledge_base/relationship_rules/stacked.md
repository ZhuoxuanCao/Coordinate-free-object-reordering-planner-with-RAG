# Stacked Relationship Rule

**Query Intent**: stacked arrangement, vertical stack, single-object stack variants, bottom/middle/top mapping

## Relationship Definitions
- 单物体：使用 `stacked_left` / `stacked_middle` / `stacked_right`
- 双物体：使用 `stacked`，仅含 `bottom` 与 `top`
- 三物体：使用 `stacked`，含 `bottom`、`middle`、`top`

## Required JSON Formats

### 单物体
```json
{
  "target_structure": {
    "relationship": "stacked_left",
    "placements": [
      { "object": "red cube" }
    ]
  }
}
```

### 双物体
```json
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "top",    "object 2": "red cube" }
    ]
  }
}
```

### 三物体
```json
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "middle", "object 2": "green cube" },
      { "position": "top",    "object 3": "red cube" }
    ]
  }
}
```

## Critical Constraints
- 字段名严格遵循上面示例（`object` 或 `object 1/2/3`）。
- 不得添加其他 key（例如 `object_name`、`color`、`pos`）。
- 多物体情形必须完整列出所需位置；不可省略。
- 输出为纯 JSON，无 markdown，无解释文本。
- 颜色 + 形状描述可自由组合，保持字符串格式。

## Execution Guidance
- 单物体 stack 不包含位置字段，直接输出对象。
- 多物体 stack 需从 bottom→top 的逻辑顺序描述，但允许 placements 数组顺序不同。
- 与文档定义不一致的格式视为无效，必须予以修正。
