# Stack Replacement — Bottom Position

**Query Intent**: bottom replacement, clear upper layers first, remove unwanted bottom to scattered, rebuild stack in order

**CRITICAL POLICY**:
- Physical access: You CANNOT access bottom while middle/top exist.
- Clear sequence: Clear top → buffer, then clear middle → buffer BEFORE changing bottom. As layers are cleared, the remaining stack shifts upward; treat bottom as empty only after both upper layers are removed.
- Unwanted objects: If current bottom object is NOT in target, move it to `scattered` (do NOT restore).
- Placement: Place the target bottom object, then restore middle and top from buffers.

## Minimal Correct Pattern
```json
[
  {"step": 1, "action": "move_to_buffer", "object": "<top object>",    "from": {"type": "stack", "position": "top"},    "to": {"type": "buffer", "slot": "B1"}, "reason": "Clear top"},
  {"step": 2, "action": "move_to_buffer", "object": "<middle object>", "from": {"type": "stack", "position": "middle"}, "to": {"type": "buffer", "slot": "B2"}, "reason": "Clear middle"},
  {"step": 3, "action": "move_to_position", "object": "<wrong bottom>", "from": {"type": "stack", "position": "bottom"}, "to": {"type": "scattered"},            "reason": "Remove unwanted bottom"},
  {"step": 4, "action": "move_to_position", "object": "<target bottom>", "from": {"type": "scattered"},                 "to": {"type": "stack", "position": "bottom"}, "reason": "Place correct bottom"},
  {"step": 5, "action": "move_from_buffer", "object": "<middle object>", "from": {"type": "buffer", "slot": "B2"},     "to": {"type": "stack", "position": "middle"}, "reason": "Restore middle"},
  {"step": 6, "action": "move_from_buffer", "object": "<top object>",    "from": {"type": "buffer", "slot": "B1"},     "to": {"type": "stack", "position": "top"},    "reason": "Restore top"}
]
```

## Forbidden Examples
```json
// ❌ Direct bottom access while middle/top exist
{"action": "move_to_position", "object": "<wrong bottom>", "from": {"type": "stack", "position": "bottom"}}

// ❌ Restoring unwanted bottom back to stack
{"action": "move_from_buffer", "object": "<wrong bottom>", "to": {"type": "stack", "position": "bottom"}}
```

## Checklist
- Clear top then middle before operating on bottom; once cleared, treat exposed layers as temporarily empty until final restoration.
- Unwanted objects go to scattered and must NOT return to stack
- Use buffer only for objects that remain in target; restore in bottom→middle→top order
