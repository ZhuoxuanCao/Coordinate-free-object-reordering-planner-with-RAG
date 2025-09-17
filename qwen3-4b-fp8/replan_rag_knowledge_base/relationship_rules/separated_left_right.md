# Separated Left-Right Relationship Rule

**Query Intent**: separated left right arrangement, horizontal separation, side-by-side layout

## Relationship Definition
- Two objects: Contains only `left` and `right` positions.
- Three objects: Arranged as `left`, `middle`, `right`, corresponding to `relationship = "separate_horizontal"`.

## Required JSON Formats

### Two Objects (relationship = `separated_left_right`)
```json
{
  "target_structure": {
    "relationship": "separated_left_right",
    "placements": [
      { "position": "left",  "object 1": "green cube" },
      { "position": "right", "object 2": "red cube" }
    ]
  }
}
```

### Three Objects (relationship = `separate_horizontal`)
```json
{
  "target_structure": {
    "relationship": "separate_horizontal",
    "placements": [
      { "position": "left",   "object 1": "blue cube" },
      { "position": "middle", "object 2": "red block" },
      { "position": "right",  "object 3": "green cube" }
    ]
  }
}
```

## Critical Constraints
- Object field naming in `placements` follows `object 1/2/3`.
- Do not add additional keys like `object`, `color`, etc.
- Position values are limited to `left` / `middle` / `right`.
- Output must be pure JSON, without explanations or Markdown.
- Formats from other relationships must not be mixed; if target is 3 objects but positions are not left/middle/right, consider as invalid input.

## Execution Guidance
- When handling two objects, only return the two positions shown; no need for middle.
- Three objects must follow logical description of left → middle → right, but array order can be adjusted.
- Keep object descriptions consistent with input, unless upstream explicitly requires modification.
