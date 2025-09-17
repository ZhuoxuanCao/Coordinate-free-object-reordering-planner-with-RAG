# Stacked and Separated Left Rule

**Query Intent**: 2+1 arrangement, stacked pair with left-separated object

## Relationship Definition
- relationship 固定为 `stacked_and_separated_left`。
- 物体数量为 3，其中两个构成垂直堆叠，另一个独立放在左侧。
- position 允许值：`bottom`、`top`、`left`。
- 对象字段命名为 `object 1`、`object 2`、`object 3`。

## Required JSON Format
```json
{
  "target_structure": {
    "relationship": "stacked_and_separated_left",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "top",    "object 2": "red cube" },
      { "position": "left",   "object 3": "green cube" }
    ]
  }
}
```

## Critical Constraints
- 不得添加其他位置或键。
- `left` 对象为独立物体，不带 `position`=middle/right。
- 输出必须为纯 JSON，无补充文本。
- 顺序可调整，但需包含全部三个条目。

## Execution Guidance
- 判断独立物体位于左侧时使用此关系；位于右侧请使用 `stacked_and_separated_right`。
- 不可混用 `separate_horizontal` 或 `stacked` 等其他关系。
