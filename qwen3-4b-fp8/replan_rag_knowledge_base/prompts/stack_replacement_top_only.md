# Stack Replacement - Top Layer Only

**Query Intent**: System prompt for top_only stack replacement scenarios
**Prompt Type**: replacement_type_prompt
**Target Scenario**: top_only
**Priority**: High
**Usage**: Direct template injection for top layer replacement cases

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

🔴 === TOP LAYER REPLACEMENT (SIMPLE) === 🔴
✅ SCENARIO: Only top layer needs correction - SIMPLEST case
✅ PATTERN: Remove-then-Place (exactly 2 steps)
✅ NO BLOCKING: Top layer is directly accessible

🚨🚨🚨 OVERRIDE ALL OTHER RULES: TOP_ONLY REPLACEMENT REQUIRES EXACTLY 2 STEPS 🚨🚨🚨

⚠️⚠️⚠️ CRITICAL PHYSICAL CONSTRAINT: POSITION MUST BE EMPTY BEFORE PLACEMENT ⚠️⚠️⚠️
❌ ABSOLUTE PROHIBITION: NEVER place object on occupied position
❌ ABSOLUTE PROHIBITION: Must clear existing object FIRST, then place new object SECOND
✅ MANDATORY: Two separate actions - one to clear, one to place
🚨 IGNORE ALL SINGLE-STEP SUGGESTIONS FROM OTHER RULES 🚨

🔴 REPLACEMENT SEQUENCE (MANDATORY ORDER):
  1. move_to_position: wrong_top_object → scattered (FIRST: remove current occupant)
  2. move_to_position: correct_top_object → top (SECOND: place target object)

🔴 CRITICAL RULES:
- Step 1 MUST clear the position (wrong object → scattered)
- Step 2 MUST place target object (correct object → position)
- NO buffer needed (wrong object goes to scattered permanently)
- NO skipping: even simple replacement needs both steps
- NO single-step placement: ALWAYS use 2-step clear-then-place sequence

EXAMPLE - Current: yellow cube at top, Target: red cube at top:
  Step 1: move_to_position yellow cube from top → scattered (clear position)
  Step 2: move_to_position red cube from scattered → top (place target)

❌ WRONG (violates physical constraints):
  Step 1: move_to_position red cube from scattered → top (position occupied!)

✅ CORRECT (follows physical constraints):
  Step 1: move_to_position yellow cube from top → scattered (clear first)
  Step 2: move_to_position red cube from scattered → top (place second)