# Stack Replacement — Middle Position

**Query Intent**: middle replacement, clear top first, remove unwanted object to scattered, buffer temporary restore, forbidden direct access to blocked layer

**CRITICAL POLICY**:
- Physical access: You CANNOT access middle while top exists.
- Clear sequence: Clear top → buffer (temporary) BEFORE changing middle. Once the top is removed, the previous middle behaves as the exposed top until you place the new object—treat the slot as temporarily empty.
- Unwanted objects: If the current middle object does NOT appear in target, move it to `scattered` (do NOT restore).
- Placement: After clearing, place the target object into middle.
- Restore: Restore only objects that still appear in target (e.g., top from buffer).

## Minimal Correct Pattern
```json
[
  {"step": 1, "action": "move_to_buffer", "object": "<top object>",   "from": {"type": "stack", "position": "top"},    "to": {"type": "buffer", "slot": "B1"}, "reason": "Clear top to access middle"},
  {"step": 2, "action": "move_to_position", "object": "<wrong middle>", "from": {"type": "stack", "position": "middle"}, "to": {"type": "scattered"},            "reason": "Remove unwanted middle (not in target)"},
  {"step": 3, "action": "move_to_position", "object": "<target middle>", "from": {"type": "scattered"},                 "to": {"type": "stack", "position": "middle"}, "reason": "Place correct middle"},
  {"step": 4, "action": "move_from_buffer", "object": "<top object>",   "from": {"type": "buffer", "slot": "B1"},     "to": {"type": "stack", "position": "top"},    "reason": "Restore top"}
]
```

## Forbidden Examples
```json
// ❌ Direct middle access while top exists
{"action": "move_to_position", "object": "<wrong middle>", "from": {"type": "stack", "position": "middle"}}

// ❌ Restoring unwanted object back to stack
{"action": "move_from_buffer", "object": "<wrong middle>", "to": {"type": "stack", "position": "middle"}}
```

## Checklist
- Clear top first (buffer) → then operate on middle; after clearing, treat the exposed middle as empty top-layer space.
- Unwanted objects go to scattered and must NOT return to stack
- Use buffer only for objects that remain in target
