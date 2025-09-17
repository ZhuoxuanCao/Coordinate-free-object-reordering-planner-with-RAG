# Stacked and Separated Right Rule

**Query Intent**: 2+1 arrangement, stacked pair with right-separated object

## Relationship Definition
- relationship is fixed as `stacked_and_separated_right`.
- Two objects form a vertical stack, the third object is independently placed on the right side.
- Allowed position values: `bottom`, `top`, `right`.
- Object field naming: `object 1`, `object 2`, `object 3`.

## Required JSON Format
```json
{
  "target_structure": {
    "relationship": "stacked_and_separated_right",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "top",    "object 2": "red cube" },
      { "position": "right",  "object 3": "green cube" }
    ]
  }
}
```

## Critical Constraints
- Do not add `left` or other positions.
- Output must be pure JSON, without explanatory text.
- `placements` array must contain all three entries.

## Execution Guidance
- Use this relationship only when the independent object is indeed positioned on the right side.
- If the independent object is on the left side, please use `stacked_and_separated_left` instead.
