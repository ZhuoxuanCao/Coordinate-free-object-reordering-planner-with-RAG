# Execution Order Rules

**Query Intent**: execution order, bottom-up building, layer dependencies, buffer clearing sequence

**CRITICAL COMPLIANCE**: All actions must follow bottom-up construction order and use coordinate-free buffer actions when clearing upper layers.

## MANDATORY EXECUTION SEQUENCE

**RULE R2 - BOTTOM-UP ORDER**
- In `stacked` targets, bottom layer must be positioned first
- Middle layer can only be placed after bottom layer is correct
- Top layer can only be placed after both bottom and middle layers are correct

**RULE R3 - CLEAR-ABOVE-FIRST**
When needing to correct a stacking layer L (such as bottom/middle):
1. Use `move_to_buffer` to remove layers above L from top to bottom
2. Correct layer L (usually `move_to_position`)
3. Use `move_from_buffer` to restore buffered objects from bottom to top

## APPROVED ACTION PATTERNS

### Direct Construction (No Conflicts)
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

### Clear and Rebuild (Wrong Objects Exist)
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
- Step numbers must increment consecutively starting from 1
- Any `move_to_position` action should confirm target position dependencies are satisfied
- Clearing order strictly follows top → middle → bottom; restoration order strictly follows bottom → middle → top
- Forbidden to have missing `object` fields or old action names (like `move`) in `plan`

## VIOLATION EXAMPLES
```json
// ❌ middle before bottom
{
  "step": 1,
  "action": "move_to_position",
  "object": "green cube",
  "to": { "type": "stack", "position": "middle" }
}

// ❌ directly modify bottom without clearing
{
  "step": 1,
  "action": "move_to_position",
  "object": "blue cube",
  "to": { "type": "stack", "position": "bottom" }
}
```

## SUCCESS CHECKLIST
- ✅ Each action uses standard action names with top-level `object`
- ✅ Clear-then-build sequences use buffer slots and are eventually cleared
- ✅ Plan satisfies bottom-up logic without violating dependencies
- ✅ Can be directly used with document-defined `target_structure`
