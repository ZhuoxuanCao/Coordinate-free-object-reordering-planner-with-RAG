# Task Definition - Object Relationship Planner

**Query Intent**: replan task, cube/object reordering, multi-relationship target configuration, JSON structure compliance

**CRITICAL TASK DEFINITION**: Plan current object state according to target `target_structure` (strictly follow "Input JSON Types and Format Summary"), generate executable action plan and provide final expected structure.

## MANDATORY Task Requirements

**INPUT ANALYSIS**:
- `target_structure`: Relationship types only from documented enumeration set (single object stack, stacked, separated_left_right, separated_front_back, pyramid, stacked_and_separated_left/right, separate_horizontal, separate_vertical).
- `current_state`: Describes current relationship (possibly `none`), existing stacks, scattered objects, buffer occupation, etc.
- Object count ≤ 3, consistent with `target_structure.placements` count.

**OUTPUT REQUIREMENTS**:
- Three-part JSON: `status` + `plan` + `final_expected` (refer to `json_structure` rules).
- `final_expected.target_structure` must be completely consistent with target relationship format, using same field naming (`object` or `object 1/2/3`).
- Action list `plan` uses coordinate-free action types and maintains top-level `object` field.

## CORE OBJECTIVE
- Under premise of following document format, convert current configuration to target relationship structure.
- Handle all document-supported relationship types, not limited to single stacking.

## CRITICAL COMPLIANCE
- When encountering stack-type targets, follow bottom-up sequence; for separation-type targets ensure correct left/right/front/back order.
- Use standard buffer slots `B1/B2/B3` for temporary storage (if needed).
- Maintain object descriptions consistent with input, unless task explicitly requires replacement.
- If target structure is already satisfied, output empty plan but still provide `final_expected`.

## SCOPE CONSTRAINTS
- Support all document-defined relationships for 1~3 objects.
- Control action steps within executable range (recommended ≤ 8).
- Do not use coordinates, angles, or other additional numerical information.

## SUCCESS CRITERIA
1. `final_expected.target_structure` completely consistent with target (relationship, fields, object descriptions).
2. Each action in `plan` executable and follows action schema.
3. No fields or additional output conflicting with documentation.
4. Execute correct sequence and buffer strategy for specific relationship types.

## FAILURE CONDITIONS
- Field naming in `target_structure` doesn't meet documentation requirements.
- Actions or final structure inconsistent with target.
- Introduction of undefined relationships or additional fields.
- Missing required action fields or illegal buffer slots.
