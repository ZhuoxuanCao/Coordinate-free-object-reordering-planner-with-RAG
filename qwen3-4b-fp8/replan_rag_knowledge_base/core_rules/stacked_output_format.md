# Stacked Relationship Target Format

**Query Intent**: stacked relationship json, bottom/middle/top definitions, single-object stack variants

**Authoritative Source**: Only allow structures defined in "Input JSON Types and Format Summary".

## 1. Single Object Stack Variants
When there is only one object, use one of the following relationships: `stacked_left`, `stacked_middle`, `stacked_right`. `placements` contains only a single object entry.

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

## 2. Two-Object Stacked
- relationship fixed as `stacked`
- `placements` contains only two entries, fields `object 1` / `object 2`
- Position fields only allow `bottom`, `top`

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

## 3. Three-Object Stacked
- relationship remains `stacked`
- `placements` must contain `bottom`, `middle`, `top`
- Object fields named as `object 1`, `object 2`, `object 3`

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

## 4. Constraints
- `placements` order can vary, but must completely cover required positions.
- Must not add extra fields like `object`, `color`, `pos` that don't appear in examples.
- Description strings maintain free format (color + type).
- Output must be pure JSON, must not mix in explanatory text or Markdown.
