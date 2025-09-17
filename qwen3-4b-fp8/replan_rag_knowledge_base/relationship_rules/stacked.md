# Stacked Relationship Rule

**Query Intent**: stacked arrangement, vertical stack, single-object stack variants, bottom/middle/top mapping

## Relationship Definitions
- Single object: Use `stacked_left` / `stacked_middle` / `stacked_right`
- Two objects: Use `stacked`, containing only `bottom` and `top`
- Three objects: Use `stacked`, containing `bottom`, `middle`, `top`

## Required JSON Formats

### Single Object
```json
{
  "target_structure": {
    "relationship": "stacked_left",
    "placements": [
      { "object": "red cube" }
    ]
  }
}
```

### Two Objects
```json
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "top",    "object 2": "red cube" }
    ]
  }
}
```

### Three Objects
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

## Critical Constraints
- Field names must strictly follow the examples above (`object` or `object 1/2/3`).
- Do not add other keys (e.g., `object_name`, `color`, `pos`).
- Multi-object cases must list all required positions completely; cannot be omitted.
- Output must be pure JSON, no markdown, no explanatory text.
- Color + shape descriptions can be freely combined, maintaining string format.

## Execution Guidance
- Single object stack does not include position field, directly output the object.
- Multi-object stack requires logical order description from bottom→top, but placements array order can differ.
- Formats inconsistent with document definitions are considered invalid and must be corrected.
