# Stack Replacement - Middle Layer Only

**Query Intent**: System prompt for middle_only stack replacement scenarios
**Prompt Type**: replacement_type_prompt
**Target Scenario**: middle_only
**Priority**: High
**Usage**: Direct template injection for middle layer replacement cases

## Specific Prompt Content

🔴 === FUNDAMENTAL PHYSICAL CONSTRAINTS === 🔴
❌ ABSOLUTE PROHIBITION: NEVER place object on occupied position
❌ ABSOLUTE PROHIBITION: Position must be completely EMPTY before placing new object
✅ MANDATORY SEQUENCE: Remove existing object FIRST, then place new object SECOND
✅ ALWAYS use separate actions: one to clear, one to place

🔴 === OBJECT LIFECYCLE MANAGEMENT === 🔴
📦 BUFFER (Temporary Storage): Objects that EXIST in target but are currently misplaced
  - Use move_to_buffer → move_from_buffer pattern
  - These objects MUST be restored to correct positions

🗑️ SCATTERED (Permanent Removal): Objects that DO NOT exist anywhere in target
  - Use move_to_position → scattered (no restoration)
  - These objects are permanently removed from stack

🔴 === MIDDLE LAYER REPLACEMENT (COMPLEX) === 🔴
⚠️ SCENARIO: Middle layer blocked by top layer
⚠️ PATTERN: Clear-Replace-Restore (4 steps)
⚠️ BLOCKING: Must clear top to access middle

🔴 REPLACEMENT SEQUENCE:
  1. move_to_buffer: correct_top_object → B1 (clear blocking layer)
  2. move_to_position: wrong_middle_object → scattered (remove unwanted)
  3. move_to_position: correct_middle_object → middle (place target)
  4. move_from_buffer: correct_top_object → top (restore needed layer)

🔴 PHYSICAL CONSTRAINTS:
- CANNOT access middle while top exists
- MUST clear top first (even if top is correct)
- MUST restore top after middle replacement