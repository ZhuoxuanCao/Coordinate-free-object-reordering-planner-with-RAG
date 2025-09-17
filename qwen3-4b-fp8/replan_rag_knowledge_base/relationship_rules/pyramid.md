# Pyramid Relationship Rule

**Query Intent**: pyramid arrangement, triangular stack, two-bottom-one-top structure

## Relationship Definition
- Applicable to pyramid formed by three objects: two at bottom level (left and right), one at top level.
- relationship is fixed as `pyramid`.
- Position fields use `bottom left`, `bottom right`, `top`.
- Object field naming: `object 1`, `object 2`, `object 3`.

## Required JSON Format
```json
{
  "target_structure": {
    "relationship": "pyramid",
    "placements": [
      { "position": "bottom left",  "object 1": "green cube" },
      { "position": "bottom right", "object 2": "red cube" },
      { "position": "top",          "object 3": "blue cube" }
    ]
  }
}
```

## Critical Constraints
- Must completely specify all three positions; cannot list only bottom level or top.
- Do not split position into multiple fields; must maintain single string (e.g., `"bottom left"`).
- Output must not contain additional keys, coordinates, or explanatory text.
- Color and object type descriptions are flexible, but must be strings.

## Execution Guidance
- When input describes "pyramid", "pyramid", or "two at bottom level, one at top level", forcibly use this structure.
- If detection results do not match the examples, need to correct upstream first before processing.
