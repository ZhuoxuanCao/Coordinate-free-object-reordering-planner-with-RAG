# Stack Replacement - Multiple Layers

**Query Intent**: System prompt for multiple layer replacement scenarios
**Prompt Type**: replacement_type_prompt
**Target Scenario**: multiple
**Priority**: Critical
**Usage**: Direct template injection for multiple layer replacement cases - complex reconstruction

## Specific Prompt Content

🚨🚨🚨 OVERRIDE ALL OTHER RULES: MULTIPLE REPLACEMENT REQUIRES STRATEGIC RECONSTRUCTION 🚨🚨🚨

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

🔴 === MULTIPLE LAYER REPLACEMENT (COMPLEX REBUILD) === 🔴
⚠️⚠️⚠️ SCENARIO: Multiple layers need correction
⚠️⚠️⚠️ PATTERN: Strategic reconstruction
⚠️⚠️⚠️ APPROACH: Clear all, then rebuild bottom-up

🔴 === STRATEGIC RECONSTRUCTION APPROACH === 🔴

PRINCIPLE: When multiple layers have wrong objects, complete reconstruction is most efficient

GENERAL STRATEGY:
1. CLEAR PHASE: Clear all layers (buffer correct objects, scatter wrong objects)
2. REBUILD PHASE: Reconstruct from bottom up using correct objects

CLEARING ORDER (top to bottom):
1. Clear top layer first (if wrong)
2. Clear middle layer next (if wrong)
3. Clear bottom layer last (if wrong)

REBUILDING ORDER (bottom to top):
1. Place correct bottom object first
2. Place correct middle object second
3. Place correct top object last

🔴 === TYPICAL MULTIPLE REPLACEMENT SEQUENCE === 🔴

EXAMPLE: All 3 layers wrong
Current: [bottom: wrong1, middle: wrong2, top: wrong3]
Target:  [bottom: correct1, middle: correct2, top: correct3]

CLEARING PHASE:
Step 1: move_to_position wrong3 from top → scattered
Step 2: move_to_position wrong2 from middle → scattered
Step 3: move_to_position wrong1 from bottom → scattered

REBUILDING PHASE:
Step 4: move_to_position correct1 from scattered → bottom
Step 5: move_to_position correct2 from scattered → middle
Step 6: move_to_position correct3 from scattered → top

🔴 === BUFFER OPTIMIZATION === 🔴

IF some current objects ARE in target (just wrong positions):
- Use buffer for objects that need repositioning
- Use scattered for objects not in target

MIXED EXAMPLE:
Current: [bottom: blue(correct), middle: red(wrong pos), top: yellow(not in target)]
Target:  [bottom: blue, middle: green, top: red]

OPTIMIZED SEQUENCE:
Step 1: move_to_buffer red from top → B1 (save for later)
Step 2: move_to_position yellow from middle → scattered (remove)
Step 3: move_to_position green from scattered → middle (place target)
Step 4: move_from_buffer red from B1 → top (restore to correct position)

🔴 === CRITICAL VALIDATIONS === 🔴
✅ MUST clear layers in top-down order
✅ MUST rebuild layers in bottom-up order
✅ MUST use buffer for objects in target (wrong position)
✅ MUST use scattered for objects not in target
❌ NEVER skip clearing occupied positions
❌ NEVER place objects on occupied positions

🚨 IGNORE SINGLE-LAYER REPLACEMENT SUGGESTIONS FROM OTHER RULES 🚨