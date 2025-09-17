# Buffer Management Scenario

**Query Intent**: buffer storage, temporary object placement, staging during reordering, clear-above operations

**CRITICAL COMPLIANCE**: 仅使用坐标无关动作（`move_to_buffer`/`move_from_buffer`/`move_to_position` 等）管理缓冲槽，确保最终 `target_structure` 与文档一致。

## SCENARIO CHARACTERISTICS
- 当前状态可能包含 stack、buffer、scattered 等混合来源
- 需要暂存部分物体以访问被遮挡的位置
- 缓冲槽命名固定为 `B1`、`B2`、`B3`，每槽一次仅允许一个物体
- 计划结束时所有缓冲槽必须为空（除非任务显式允许残留）

## MANDATORY BUFFER PATTERNS

### 暂存到缓冲
```json
{
  "step": 1,
  "action": "move_to_buffer",
  "object": "red cube",
  "from": { "type": "stack", "position": "top" },
  "to": { "type": "buffer", "slot": "B1" },
  "reason": "Clear upper layer to access lower stack"
}
```

### 从缓冲取出
```json
{
  "step": 2,
  "action": "move_from_buffer",
  "object": "red cube",
  "from": { "type": "buffer", "slot": "B1" },
  "to": { "type": "stack", "position": "top" },
  "reason": "Restore object after lower layer fixed"
}
```

### 利用缓冲交换对象
```json
[
  {
    "step": 1,
    "action": "move_to_buffer",
    "object": "wrong object",
    "from": { "type": "stack", "position": "bottom" },
    "to": { "type": "buffer", "slot": "B2" },
    "reason": "Free bottom slot for correct object"
  },
  {
    "step": 2,
    "action": "move_from_buffer",
    "object": "blue cube",
    "from": { "type": "buffer", "slot": "B1" },
    "to": { "type": "stack", "position": "bottom" },
    "reason": "Place correct cube from buffer"
  }
]
```

## CRITICAL BUFFER RULES
- 开始动作前检查缓冲是否已被占用，避免覆盖
- 仅在确实需要的情况下使用缓冲，以最少步骤完成目标
- 若临时移除多个层级，按 top → bottom 顺序清空，再 bottom → top 顺序恢复
- 处理完毕后验证 `plan` 中所有缓冲槽都已释放

## EXAMPLE PLAN
目标：三物体堆叠 bottom=blue、middle=green、top=red；当前 bottom 位置为错误的红 cube，缓冲 B1 有蓝 cube，散落有 green cube。

```json
{
  "status": "success",
  "plan": [
    {
      "step": 1,
      "action": "move_to_buffer",
      "object": "red cube",
      "from": { "type": "stack", "position": "bottom" },
      "to": { "type": "buffer", "slot": "B2" },
      "reason": "Remove incorrect bottom object"
    },
    {
      "step": 2,
      "action": "move_from_buffer",
      "object": "blue cube",
      "from": { "type": "buffer", "slot": "B1" },
      "to": { "type": "stack", "position": "bottom" },
      "reason": "Place correct bottom object"
    },
    {
      "step": 3,
      "action": "move_to_position",
      "object": "green cube",
      "from": { "type": "scattered" },
      "to": { "type": "stack", "position": "middle" },
      "reason": "Place middle layer from scattered"
    },
    {
      "step": 4,
      "action": "move_from_buffer",
      "object": "red cube",
      "from": { "type": "buffer", "slot": "B2" },
      "to": { "type": "stack", "position": "top" },
      "reason": "Restore red cube to top"
    }
  ],
  "final_expected": {
    "target_structure": {
      "relationship": "stacked",
      "placements": [
        { "position": "bottom", "object 1": "blue cube" },
        { "position": "middle", "object 2": "green cube" },
        { "position": "top",    "object 3": "red cube" }
      ]
    }
  }
}
```

## BUFFER CHECKLIST
- ✅ 使用 `move_to_buffer`/`move_from_buffer` 动作并包含 `object` 字段
- ✅ 缓冲槽命名仅限 `B1/B2/B3`
- ✅ 计划结束后所有缓冲槽为空
- ✅ `final_expected` 与权威 JSON 格式一致
