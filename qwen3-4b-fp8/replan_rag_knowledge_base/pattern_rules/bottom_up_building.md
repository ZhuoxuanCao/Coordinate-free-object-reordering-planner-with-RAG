# Bottom-Up Building Pattern

**Query Intent**: bottom-up construction, layer ordering, stack dependency pattern

**CRITICAL COMPLIANCE**: In all stacking-related tasks, action sequence must follow bottom → middle → top, using coordinate-free actions and maintaining top-level `object` field.

## POSITION DEPENDENCY
```
TOP    ← depends on MIDDLE
MIDDLE ← depends on BOTTOM
BOTTOM ← foundation
```

## STANDARD PATTERNS

### Pattern A – Direct Construction
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

### Pattern B – Clear and Rebuild
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
- `move_to_position` can only be executed when dependent layers are correct
- Clearing order: top → middle → bottom; Restoration order: bottom → middle → top
- Ensure buffer slots are empty at plan completion
- Any steps missing `object` field or using old action names are considered illegal

## QUICK CHECK
- ✅ Bottom layer is placed or corrected first
- ✅ Middle layer actions appear after bottom layer completion
- ✅ Top layer actions appear after middle layer completion
- ✅ If clearing is needed, buffer actions appear in pairs (`move_to_buffer` + `move_from_buffer`)
