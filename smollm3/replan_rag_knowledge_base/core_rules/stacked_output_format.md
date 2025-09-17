# Stacked Relationship Target Format

**Query Intent**: stacked relationship json, bottom/middle/top definitions, single-object stack variants

**Authoritative Source**: 仅允许使用《输入的json类型与格式总结》中定义的结构。

## 1. 单物体 Stack 变体
当只有一个物体时，使用下列其中一个 relationship：`stacked_left`、`stacked_middle`、`stacked_right`。`placements` 中只有单个对象条目。

```json
{
  "target_structure": {
    "relationship": "stacked_middle",
    "placements": [
      { "object": "blue cube" }
    ]
  }
}
```

## 2. 双物体 Stacked
- relationship 固定为 `stacked`
- `placements` 仅包含两个条目，字段 `object 1` / `object 2`
- 位置字段仅允许 `bottom`、`top`

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

## 3. 三物体 Stacked
- relationship 仍为 `stacked`
- `placements` 必须包含 `bottom`、`middle`、`top`
- 对象字段命名为 `object 1`、`object 2`、`object 3`

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

## 4. 约束
- `placements` 顺序可变，但必须完整覆盖所需位置。
- 不得额外添加 `object`、`color`、`pos` 等未在示例中出现的字段。
- 描述字符串保持自由格式（颜色 + 类型）。
- 输出必须是纯 JSON，不得混入解释文本或 Markdown。
