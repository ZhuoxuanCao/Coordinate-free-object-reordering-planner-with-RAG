# Pyramid Relationship Rule

**Query Intent**: pyramid arrangement, triangular stack, two-bottom-one-top structure

## Relationship Definition
- 适用于三个物体形成的金字塔：底层左右两个，上层一个。
- relationship 固定为 `pyramid`。
- 位置字段使用 `bottom left`、`bottom right`、`top`。
- 对象字段命名为 `object 1`、`object 2`、`object 3`。

## Required JSON Format
```json
{
  "target_structure": {
    "relationship": "pyramid",
    "placements": [
      { "position": "bottom left",  "object 1": "green cube" },
      { "position": "bottom right", "object 2": "red cube" },
      { "position": "top",          "object 3": "blue cube" }
    ]
  }
}
```

## Critical Constraints
- 必须完整给出三个位置；不可只列出底层或顶部。
- 不得将 position 拆分为多个字段；必须保持单个字符串（如 `"bottom left"`）。
- 输出不得包含额外键、坐标或解释文本。
- 颜色与物体类型描述自由，但需为字符串。

## Execution Guidance
- 当输入描述为“金字塔”、“pyramid”或“底层两个上层一个”时，强制使用该结构。
- 如果检测结果与示例不符，需要先在上游纠正后再处理。
