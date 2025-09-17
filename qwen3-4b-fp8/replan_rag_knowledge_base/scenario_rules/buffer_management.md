# Buffer Management Scenario

**Query Intent**: buffer storage, temporary object placement, staging during reordering, clear-above operations

**CRITICAL COMPLIANCE**: Only use coordinate-free actions (`move_to_buffer`/`move_from_buffer`/`move_to_position` etc.) to manage buffer slots, ensuring final `target_structure` matches documentation.

## SCENARIO CHARACTERISTICS
- Current state may contain mixed sources like stack, buffer, scattered
- Need to temporarily store some objects to access blocked positions
- Buffer slot names are fixed as `B1`, `B2`, `B3`, each slot allows only one object at a time
- All buffer slots must be empty at plan completion (unless task explicitly allows residue)

## MANDATORY BUFFER PATTERNS

### Store to Buffer
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

### Retrieve from Buffer
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

### Use Buffer to Exchange Objects
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
- Check if buffer is already occupied before starting actions to avoid overwriting
- Only use buffer when truly needed, complete objectives with minimum steps
- If temporarily removing multiple layers, clear in top → bottom order, then restore in bottom → top order
- After completion, verify all buffer slots in `plan` have been released

## EXAMPLE PLAN
Target: Three-object stack bottom=blue, middle=green, top=red; Current bottom position has incorrect red cube, buffer B1 has blue cube, scattered has green cube.

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
- ✅ Use `move_to_buffer`/`move_from_buffer` actions with `object` field
- ✅ Buffer slot names limited to `B1/B2/B3`
- ✅ All buffer slots empty after plan completion
- ✅ `final_expected` consistent with authoritative JSON format
