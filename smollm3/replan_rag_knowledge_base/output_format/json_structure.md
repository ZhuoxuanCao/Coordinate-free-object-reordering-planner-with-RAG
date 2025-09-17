# JSON Structure Requirements

**Query Intent**: action plan format, success/blocked schema, final target structure alignment

**Authoritative Source**: `final_expected` 与 `target_structure` 必须遵循《输入的json类型与格式总结》中的字段命名与关系定义。

## 1. 成功输出 (status = "success")
```json
{
  "status": "success",
  "plan": [
    {
      "step": 1,
      "action": "move_to_position|move_to_buffer|move_from_buffer|place_from_supply",
      "object": "blue cube",
      "from": { "type": "scattered" | "stack" | "arrangement" | "buffer", "position": "..."?, "slot": "B1|B2|B3"? },
      "to": { "type": "stack" | "arrangement" | "buffer", "position": "..."?, "slot": "B1|B2|B3"? },
      "reason": "Brief factual explanation"
    }
  ],
  "final_expected": {
    "target_structure": {
      "relationship": "...",
      "placements": [
        { "position": "...", "object 1": "..." }
      ]
    }
  }
}
```
- `plan` 数组可为空（已经满足目标时），但仍需包含在 JSON 中。
- `object` 字段必须位于动作对象的顶层，与《coordinate_free_actions》规则保持一致。
- `from` / `to` 中仅在需要时带上 `position` 或 `slot`，其它字段不得出现。
- `final_expected.target_structure` 的结构需与统一目标结构格式一致（参照 `unified_target_structure_format`）。若为单个物体，仅包含 `object`；多物体需使用 `object 1/2/3`。

## 2. 阻塞输出 (status = "blocked")
```json
{
  "status": "blocked",
  "reason": "Specific explanation of why task cannot be completed"
}
```
- 不允许额外字段。
- `reason` 为必填字符串。

## 3. 通用约束
- 输出必须是严格 JSON，不可包含 Markdown、注释或额外文本。
- 字段顺序可变，但键名必须与示例完全一致。
- 不得出现坐标、余弦、或其他与文档不符的结构。
- 若模型输出多个 JSON，仅保留第一个完整对象。

## 4. 验证清单
- ✅ `status` 为 `success` 或 `blocked`。
- ✅ `plan` 中每个动作都含 `step`、`action`、`object`、`from`、`to`、`reason`。
- ✅ `final_expected.target_structure.relationship` 与文档列举的值之一完全一致。
- ✅ `final_expected.target_structure.placements` 字段命名符合 `object` 或 `object 1/2/3` 规范。
- ✅ 无额外 field、无坐标、无解释文本。
