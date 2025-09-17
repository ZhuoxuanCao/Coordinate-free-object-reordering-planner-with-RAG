# Separated Front-Back Relationship Rule

**Query Intent**: separated front back arrangement, depth separation, two-object vs three-object layouts

## Relationship Definition
- Two objects: `relationship = "separated_front_back"`, positions are only `front`, `back`.
- Three objects: If front-back layering is needed with three objects, use `relationship = "separate_vertical"`, positions are `bottom`, `middle`, `top` (corresponding to front→middle→back).

## Required JSON Formats

### Two Objects
```json
{
  "target_structure": {
    "relationship": "separated_front_back",
    "placements": [
      { "position": "front", "object 1": "green cube" },
      { "position": "back",  "object 2": "blue cube" }
    ]
  }
}
```

### Three Objects (Front-Back Layering)
```json
{
  "target_structure": {
    "relationship": "separate_vertical",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "middle", "object 2": "red cube" },
      { "position": "top",    "object 3": "green cube" }
    ]
  }
}
```

## Critical Constraints
- Object keys use `object 1/2/3`.
- Position values are strictly limited to vocabulary in examples; must not introduce mixed descriptions like `front-left`.
- Must not add extra keys or coordinates.
- Output must be pure JSON, without comments or Markdown.

## Execution Guidance
- Current document maps three-object front-back layout to bottom/middle/top, maintaining consistency with summary document.
- If input has only two objects described as front/back, must use `separated_front_back`.
- Any input inconsistent with above format should be corrected upstream before entering planning steps.
