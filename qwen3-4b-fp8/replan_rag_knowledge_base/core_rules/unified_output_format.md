# Unified Target Structure Format

**Query Intent**: target structure json, relationship schema, object arrangement definitions, perception output compatibility

**Authoritative Source**: All input/output object relationship JSON must comply with unified format specifications. This rule document is authoritative and must not be deviated from.

## 1. Single Object
- Treated as special stack with only one object
- Use relationship = `stacked_left` / `stacked_middle` / `stacked_right`
- `placements` contains only one object entry, without position field

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

## 2. Two Objects
Only three relationships allowed: `stacked`, `separated_left_right`, `separated_front_back`.

### 2.1 Vertical Stacking (stacked)
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

### 2.2 Left-Right Separation (separated_left_right)
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

### 2.3 Front-Back Separation (separated_front_back)
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

## 3. Three Objects
Supports four major categories: `stacked`, `pyramid`, `stacked_and_separated_left|right`, `separate_horizontal|vertical`.

### 3.1 Vertical Stacking (stacked)
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

### 3.2 Pyramid
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

### 3.3 2+1 Combination
- `stacked_and_separated_left`: Independent block positioned on the left
- `stacked_and_separated_right`: Independent block positioned on the right

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

### 3.4 Three Object Separation
- `separate_horizontal`: Arranged by left / middle / right
- `separate_vertical`: Arranged by bottom / middle / top (corresponding to front-back layering)

```json
{
  "target_structure": {
    "relationship": "separate_horizontal",
    "placements": [
      { "position": "left",   "object 1": "blue cube" },
      { "position": "middle", "object 2": "red cube" },
      { "position": "right",  "object 3": "green cube" }
    ]
  }
}
```

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

## 4. General Constraints
- Field names must strictly match the above examples (`object` or `object 1/2/3`).
- `placements` array length must exactly match object count, no additional entries allowed.
- Must not introduce coordinates, extra descriptive fields, or English comments.
- Color + object type descriptions are completely free, but must be strings.
- If `plan` behavior output is generated, it must be defined in separate rules; this file only constrains `target_structure` format.
