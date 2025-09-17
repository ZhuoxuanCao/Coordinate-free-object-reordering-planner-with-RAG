# Bottom-Up Building Pattern

**Query Intent**: bottom-up construction, layer ordering, stack dependency pattern

**CRITICAL COMPLIANCE**: 在所有堆叠相关任务中，动作顺序必须遵循 bottom → middle → top，使用坐标无关动作并保持 `object` 顶层字段。

## POSITION DEPENDENCY
```
TOP    ← depends on MIDDLE
MIDDLE ← depends on BOTTOM
BOTTOM ← foundation
```

## STANDARD PATTERNS

### Pattern A – 直接构建
```json
[
  {
    "step": 1,
    "action": "move_to_position",
    "object": "blue cube",
    "from": { "type": "scattered" },
    "to": { "type": "stack", "position": "bottom" },
    "reason": "Start with bottom foundation"
  },
  {
    "step": 2,
    "action": "move_to_position",
    "object": "green cube",
    "from": { "type": "scattered" },
    "to": { "type": "stack", "position": "middle" },
    "reason": "Build middle layer"
  },
  {
    "step": 3,
    "action": "move_to_position",
    "object": "red cube",
    "from": { "type": "scattered" },
    "to": { "type": "stack", "position": "top" },
    "reason": "Complete top layer"
  }
]
```

### Pattern B – 清理再重建
```json
[
  {
    "step": 1,
    "action": "move_to_buffer",
    "object": "red cube",
    "from": { "type": "stack", "position": "top" },
    "to": { "type": "buffer", "slot": "B1" },
    "reason": "Clear top to access middle"
  },
  {
    "step": 2,
    "action": "move_to_buffer",
    "object": "green cube",
    "from": { "type": "stack", "position": "middle" },
    "to": { "type": "buffer", "slot": "B2" },
    "reason": "Clear middle to access bottom"
  },
  {
    "step": 3,
    "action": "move_to_position",
    "object": "blue cube",
    "from": { "type": "scattered" },
    "to": { "type": "stack", "position": "bottom" },
    "reason": "Fix bottom layer"
  },
  {
    "step": 4,
    "action": "move_from_buffer",
    "object": "green cube",
    "from": { "type": "buffer", "slot": "B2" },
    "to": { "type": "stack", "position": "middle" },
    "reason": "Restore middle layer"
  },
  {
    "step": 5,
    "action": "move_from_buffer",
    "object": "red cube",
    "from": { "type": "buffer", "slot": "B1" },
    "to": { "type": "stack", "position": "top" },
    "reason": "Restore top layer"
  }
]
```

## VALIDATION GUIDELINES
- `move_to_position` 只能在依赖层已正确时执行
- 清理顺序：top → middle → bottom；恢复顺序：bottom → middle → top
- 确保计划结束时缓冲槽为空
- 任何缺失 `object` 字段或旧动作名的步骤均视为非法

## QUICK CHECK
- ✅ 底层首先被放置或修正
- ✅ 中层动作出现在底层完成之后
- ✅ 顶层动作出现在中层完成之后
- ✅ 若需要清理，缓冲动作成对出现（`move_to_buffer` + `move_from_buffer`）
