# Stacked Building Scenario

**Query Intent**: build stack, create tower, arrange vertically, stacked building, bottom-up construction

**CRITICAL COMPLIANCE**: All stacking tasks (single or multi-object) must follow unified JSON structure format.

## SCENARIO CHARACTERISTICS

**INPUT PATTERN**:
- `target_structure.relationship` ∈ {`stacked_left`, `stacked_middle`, `stacked_right`, `stacked`}
- `target_structure.placements` uses `object` or `object 1/2/3` fields
- `current_state` may have partial stacking or all objects scattered

## REQUIRED ANALYSIS
1. Parse target relationship: single vs. dual vs. triple object stacking.
2. Identify correctly positioned layers and incorrect objects in current state.
3. **Determine scenario type**:
   - **EXTENSION**: current_layers < target_layers, bottom objects match → use stacking extension
   - **REPLACEMENT**: incorrect objects exist → require buffer operations
   - **MIXED**: both extension and replacement needed → hybrid strategy
4. Choose minimal action strategy: prioritize extension, use buffer when necessary.

## JSON EXAMPLES

### Single Object
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

### Three Object Stacking
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

## ACTION PATTERN
```json
{
  "step": N,
  "action": "move_to_position|move_to_buffer|move_from_buffer|place_from_supply",
  "object": "blue cube",
  "from": { "type": "scattered" | "stack" | "buffer" },
  "to": { "type": "stack", "position": "bottom|middle|top" },
  "reason": "Build stack in bottom-up order"
}
```

## CRITICAL EXECUTION RULES
- **Bottom layer priority**: Modifying `bottom` requires clearing all layers above it.
- **Single object target**: No position field needed, only output object.
- **Multi-object target**: Must completely cover required positions (bottom/middle/top).
- **Object consistency**: Maintain object descriptions consistent with target unless task explicitly requires replacement.
- **Extension preference**: When possible, extend existing correct stacks rather than rebuilding.

## STACKING EXTENSION EXAMPLES

### Example 1: 2→3 Layer Extension (PREFERRED)
**Current**: [bottom: blue cube, top: green cube]
**Target**: [bottom: blue cube, middle: green cube, top: red cube]
**Optimal Plan**: Single action to place red cube on top (green automatically becomes middle)

```json
{
  "status": "success",
  "plan": [
    {
      "step": 1,
      "action": "move_to_position",
      "object": "red cube",
      "from": { "type": "scattered" },
      "to": { "type": "stack", "position": "top" },
      "reason": "Extend 2-layer stack to 3 layers - existing top becomes middle naturally"
    }
  ]
}
```

## EXAMPLE PLAN (All Scattered → Three Object Stacking)
```json
{
  "status": "success",
  "plan": [
    {
      "step": 1,
      "action": "move_to_position",
      "object": "blue cube",
      "from": { "type": "scattered" },
      "to": { "type": "stack", "position": "bottom" },
      "reason": "Place bottom layer"
    },
    {
      "step": 2,
      "action": "move_to_position",
      "object": "green cube",
      "from": { "type": "scattered" },
      "to": { "type": "stack", "position": "middle" },
      "reason": "Place middle layer"
    },
    {
      "step": 3,
      "action": "move_to_position",
      "object": "red cube",
      "from": { "type": "scattered" },
      "to": { "type": "stack", "position": "top" },
      "reason": "Complete stack"
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

## FAILURE SCENARIOS
- **Missing required objects**: Output `status = "blocked"` with reason explaining missing objects.
- **Invalid target relationship or field naming**: Must correct format before execution.

## OPTIMIZATION NOTES
- **Prioritize existing objects**: Use current objects first, supplement from supply when necessary.
- **Buffer slots `B1/B2/B3`**: Use for temporary storage of upper layer objects during reconstruction.
- **Minimize action count**: Keep action steps minimal while maintaining format correctness.
- **Extension over reconstruction**: When current stack can be extended, prefer single extension action over multi-step rebuild.
