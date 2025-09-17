# Execution Order Rules

**Query Intent**: execution order, bottom-up building, layer dependencies, buffer clearing sequence

**CRITICAL COMPLIANCE**: 所有动作必须遵循自底向上的构建顺序，并在清理上层时使用坐标无关的缓冲动作。

## MANDATORY EXECUTION SEQUENCE

**RULE R2 - BOTTOM-UP ORDER**
- 在 `stacked` 目标中，底层需先就位
- 中层仅在底层正确后才可放置
- 顶层仅在底层与中层正确后才可放置

**RULE R3 - CLEAR-ABOVE-FIRST**
当需要修正某一堆叠层 L（如 bottom/middle）时：
1. 使用 `move_to_buffer` 自顶向下依次移除 L 以上的层
2. 修正层 L（通常 `move_to_position`）
3. 采用 `move_from_buffer` 自底向上恢复缓冲中的物体

## APPROVED ACTION PATTERNS

### 直接构建（无冲突）
```json
[
  {
    "step": 1,
    "action": "move_to_position",
    "object": "blue cube",
    "from": { "type": "scattered" },
    "to": { "type": "stack", "position": "bottom" },
    "reason": "Establish bottom layer"
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

### 清理后重建（存在错误对象）
```json
[
  {
    "step": 1,
    "action": "move_to_buffer",
    "object": "red cube",
    "from": { "type": "stack", "position": "top" },
    "to": { "type": "buffer", "slot": "B1" },
    "reason": "Clear top layer"
  },
  {
    "step": 2,
    "action": "move_to_buffer",
    "object": "green cube",
    "from": { "type": "stack", "position": "middle" },
    "to": { "type": "buffer", "slot": "B2" },
    "reason": "Clear middle layer"
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

## CRITICAL CONSTRAINTS
- 步骤编号必须连续递增，从 1 开始
- 任何 `move_to_position` 动作都应确认目标位置依赖已满足
- 清理顺序严格遵循 top → middle → bottom；恢复顺序严格遵循 bottom → middle → top
- 禁止在 `plan` 中出现缺失 `object` 字段或旧动作名（如 `move`）

## VIOLATION EXAMPLES
```json
// ❌ middle 在 bottom 之前
{
  "step": 1,
  "action": "move_to_position",
  "object": "green cube",
  "to": { "type": "stack", "position": "middle" }
}

// ❌ 未清理就直接修改 bottom
{
  "step": 1,
  "action": "move_to_position",
  "object": "blue cube",
  "to": { "type": "stack", "position": "bottom" }
}
```

## SUCCESS CHECKLIST
- ✅ 每个动作均使用标准动作名且带顶层 `object`
- ✅ 先清后建的序列使用缓冲槽并最终清空
- ✅ 计划满足自底向上逻辑，不违反依赖关系
- ✅ 可直接与文档定义的 `target_structure` 搭配使用
