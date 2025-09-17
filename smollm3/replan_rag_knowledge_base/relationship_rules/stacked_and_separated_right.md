# Stacked and Separated Right Rule

**Query Intent**: 2+1 arrangement, stacked pair with right-separated object

## Relationship Definition
- relationship 固定为 `stacked_and_separated_right`。
- 两个物体形成垂直堆叠，第三个独立放在右侧。
- position 允许值：`bottom`、`top`、`right`。
- 对象字段命名为 `object 1`、`object 2`、`object 3`。

## Required JSON Format
```json
{
  "target_structure": {
    "relationship": "stacked_and_separated_right",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "top",    "object 2": "red cube" },
      { "position": "right",  "object 3": "green cube" }
    ]
  }
}
```

## Critical Constraints
- 不得添加 `left` 或其他位置。
- 输出必须为纯 JSON，无解释性文字。
- `placements` 数组需含全部三个条目。

## Execution Guidance
- 仅在独立物体确实位于右侧时使用此关系。
- 如独立物体在左侧，请转用 `stacked_and_separated_left`。
