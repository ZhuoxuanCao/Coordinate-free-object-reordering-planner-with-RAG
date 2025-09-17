# Separated Front-Back Relationship Rule

**Query Intent**: separated front back arrangement, depth separation, two-object vs three-object layouts

## Relationship Definition
- 两个物体：`relationship = "separated_front_back"`，位置仅有 `front`、`back`。
- 三个物体：若需要前后层级且共有三个对象，使用 `relationship = "separate_vertical"`，位置为 `bottom`、`middle`、`top`（对应前→中→后）。

## Required JSON Formats

### 两个物体
```json
{
  "target_structure": {
    "relationship": "separated_front_back",
    "placements": [
      { "position": "front", "object 1": "green cube" },
      { "position": "back",  "object 2": "blue cube" }
    ]
  }
}
```

### 三个物体（前后分层）
```json
{
  "target_structure": {
    "relationship": "separate_vertical",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "middle", "object 2": "red cube" },
      { "position": "top",    "object 3": "green cube" }
    ]
  }
}
```

## Critical Constraints
- 对象键使用 `object 1/2/3`。
- position 值严格限制为示例中的词汇；不得引入 `front-left` 等混合描述。
- 不得添加额外键或坐标。
- 输出必须是纯 JSON，无评论或 Markdown。

## Execution Guidance
- 当前文档将三物体的前后布局映射到 bottom/middle/top，保持与总结文档一致。
- 若输入仅有两个物体且描述为前/后，需使用 `separated_front_back`。
- 任意与上述格式不一致的输入应在上游修正后再进入规划步骤。
