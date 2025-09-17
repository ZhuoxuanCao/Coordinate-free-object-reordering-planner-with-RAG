# JSON Structure Requirements

**Query Intent**: action plan format, success/blocked schema, final target structure alignment

**Authoritative Source**: `final_expected` and `target_structure` must comply with field naming and relationship definitions in the "Input JSON Type and Format Summary".

## 1. Success Output (status = "success")
```json
{
  "status": "success",
  "plan": [
    {
      "step": 1,
      "action": "move_to_position|move_to_buffer|move_from_buffer|place_from_supply",
      "object": "blue cube",
      "from": { "type": "scattered" | "stack" | "arrangement" | "buffer", "position": "..."?, "slot": "B1|B2|B3"? },
      "to": { "type": "stack" | "arrangement" | "buffer", "position": "..."?, "slot": "B1|B2|B3"? },
      "reason": "Brief factual explanation"
    }
  ],
  "final_expected": {
    "target_structure": {
      "relationship": "...",
      "placements": [
        { "position": "...", "object 1": "..." }
      ]
    }
  }
}
```
- `plan` array can be empty (when target is already satisfied), but must still be included in JSON.
- `object` field must be at top level of action object, consistent with "coordinate_free_actions" rules.
- `from` / `to` should only include `position` or `slot` when needed, other fields must not appear.
- `final_expected.target_structure` structure must be consistent with unified target structure format (refer to `unified_target_structure_format`). For single objects, only include `object`; multiple objects must use `object 1/2/3`.

## 2. Blocked Output (status = "blocked")
```json
{
  "status": "blocked",
  "reason": "Specific explanation of why task cannot be completed"
}
```
- No additional fields allowed.
- `reason` is a required string.

## 3. General Constraints
- Output must be strict JSON, cannot contain Markdown, comments, or extra text.
- Field order can vary, but key names must exactly match examples.
- Must not include coordinates, cosines, or other structures inconsistent with documentation.
- If model outputs multiple JSONs, only keep the first complete object.

## 4. Validation Checklist
- ✅ `status` is `success` or `blocked`.
- ✅ Each action in `plan` contains `step`, `action`, `object`, `from`, `to`, `reason`.
- ✅ `final_expected.target_structure.relationship` exactly matches one of the values listed in documentation.
- ✅ `final_expected.target_structure.placements` field naming conforms to `object` or `object 1/2/3` specification.
- ✅ No extra fields, no coordinates, no explanatory text.
