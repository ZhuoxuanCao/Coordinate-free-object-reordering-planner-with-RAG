# Stacked and Separated Left Rule

**Query Intent**: 2+1 arrangement, stacked pair with left-separated object

## Relationship Definition
- relationship is fixed as `stacked_and_separated_left`.
- Object count is 3, where two form a vertical stack and the other is independently placed on the left side.
- Allowed position values: `bottom`, `top`, `left`.
- Object field naming: `object 1`, `object 2`, `object 3`.

## Required JSON Format
```json
{
  "target_structure": {
    "relationship": "stacked_and_separated_left",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "top",    "object 2": "red cube" },
      { "position": "left",   "object 3": "green cube" }
    ]
  }
}
```

## Critical Constraints
- Do not add other positions or keys.
- `left` object is an independent object, without `position`=middle/right.
- Output must be pure JSON, without supplementary text.
- Order can be adjusted, but must include all three entries.

## Execution Guidance
- Use this relationship when determining the independent object is positioned on the left side; use `stacked_and_separated_right` if positioned on the right side.
- Do not mix with other relationships like `separate_horizontal` or `stacked`.
