# Stack Replacement - Bottom Layer Only

**Query Intent**: System prompt for bottom_only stack replacement scenarios
**Prompt Type**: replacement_type_prompt
**Target Scenario**: bottom_only
**Priority**: Critical
**Usage**: Direct template injection for bottom layer replacement cases - most complex scenario

## Specific Prompt Content

🚨🚨🚨 CRITICAL: BOTTOM_ONLY REPLACEMENT REQUIRES EXACTLY 6 STEPS - NO EXCEPTIONS 🚨🚨🚨
🚨🚨🚨 IGNORE ALL OTHER RULES: THIS TEMPLATE OVERRIDES EVERYTHING ELSE 🚨🚨🚨

❌❌❌ ABSOLUTE PROHIBITION: NEVER ACCESS BOTTOM DIRECTLY WHILE UPPER LAYERS EXIST ❌❌❌
❌❌❌ ABSOLUTE PROHIBITION: NEVER SKIP CLEARING UPPER LAYERS FIRST ❌❌❌

🔴 === FUNDAMENTAL PHYSICAL CONSTRAINTS === 🔴
❌ ABSOLUTE PROHIBITION: NEVER place object on occupied position
❌ ABSOLUTE PROHIBITION: Position must be completely EMPTY before placing new object
❌ ABSOLUTE PROHIBITION: NEVER touch bottom layer while ANY upper layer exists
✅ MANDATORY SEQUENCE: Remove existing object FIRST, then place new object SECOND
✅ ALWAYS use separate actions: one to clear, one to place

🔴 === OBJECT LIFECYCLE MANAGEMENT === 🔴
📦 BUFFER (Temporary Storage): Objects that EXIST in target but are currently misplaced
  - Use move_to_buffer → move_from_buffer pattern
  - These objects MUST be restored to correct positions

🗑️ SCATTERED (Permanent Removal): Objects that DO NOT exist anywhere in target
  - Use move_to_position → scattered (no restoration)
  - These objects are permanently removed from stack

🔴 === BOTTOM REPLACEMENT CRITICAL CONSTRAINTS === 🔴
⚠️⚠️⚠️ BOTTOM LAYER IS COMPLETELY INACCESSIBLE WHILE UPPER LAYERS EXIST
⚠️⚠️⚠️ YOU MUST CLEAR EVERY SINGLE UPPER LAYER BEFORE TOUCHING BOTTOM
⚠️⚠️⚠️ NO EXCEPTIONS - NO SHORTCUTS - NO DIRECT ACCESS

❌ ABSOLUTE PROHIBITIONS:
❌ NEVER access bottom while middle layer exists (even if middle is correct)
❌ NEVER access bottom while top layer exists (even if top is correct)
❌ NEVER skip clearing middle layer - it BLOCKS bottom access
❌ NEVER think 'middle is correct so I don't need to move it'

✅ MANDATORY PHYSICS:
✅ Middle layer PHYSICALLY BLOCKS bottom access - must be cleared
✅ Top layer PHYSICALLY BLOCKS middle access - must be cleared first
✅ EXACT sequence: Clear top → Clear middle → Access bottom → Rebuild all
✅ ALL upper layers to buffer (for restoration), wrong bottom to scattered

🔴 === MANDATORY 6-STEP SEQUENCE - FOLLOW EXACTLY === 🔴
🚨 WARNING: ANY DEVIATION FROM THIS SEQUENCE VIOLATES PHYSICS 🚨

❌ WRONG APPROACH (VIOLATES PHYSICS):
- Accessing bottom directly: {"action": "move_to_buffer", "object": "wrong_bottom", "from": {"type": "stack", "position": "bottom"}}
- Skipping upper layer clearing
- Using fewer than 6 steps

✅ CORRECT APPROACH (MANDATORY 6-STEP SEQUENCE):

STEP 1: CLEAR TOP LAYER FIRST (MANDATORY - BLOCKS EVERYTHING BELOW)
{"step": 1, "action": "move_to_buffer", "object": "red cube", "from": {"type": "stack", "position": "top"}, "to": {"type": "buffer", "slot": "B1"}, "reason": "Clear top to access middle - PHYSICS CONSTRAINT"}

STEP 2: CLEAR MIDDLE LAYER SECOND (MANDATORY - BLOCKS BOTTOM)
{"step": 2, "action": "move_to_buffer", "object": "green cube", "from": {"type": "stack", "position": "middle"}, "to": {"type": "buffer", "slot": "B2"}, "reason": "Clear middle to access bottom - PHYSICS CONSTRAINT"}

STEP 3: REMOVE WRONG BOTTOM (NOW ACCESSIBLE AFTER CLEARING ABOVE)
{"step": 3, "action": "move_to_position", "object": "yellow cube", "from": {"type": "stack", "position": "bottom"}, "to": {"type": "scattered"}, "reason": "Remove incorrect bottom object"}

STEP 4: PLACE CORRECT BOTTOM (FOUNDATION FOR REBUILD)
{"step": 4, "action": "move_to_position", "object": "blue cube", "from": {"type": "scattered"}, "to": {"type": "stack", "position": "bottom"}, "reason": "Place correct bottom foundation"}

STEP 5: RESTORE MIDDLE LAYER (REBUILD FROM BOTTOM UP)
{"step": 5, "action": "move_from_buffer", "object": "green cube", "from": {"type": "buffer", "slot": "B2"}, "to": {"type": "stack", "position": "middle"}, "reason": "Restore middle layer"}

STEP 6: RESTORE TOP LAYER (COMPLETE STACK RECONSTRUCTION)
{"step": 6, "action": "move_from_buffer", "object": "red cube", "from": {"type": "buffer", "slot": "B1"}, "to": {"type": "stack", "position": "top"}, "reason": "Restore top layer"}

🚨 MANDATORY VALIDATION: MUST GENERATE EXACTLY THESE 6 STEPS IN THIS EXACT ORDER 🚨

🔴 CRITICAL VALIDATIONS:
❌ NEVER skip any step - ALL 6 STEPS ARE MANDATORY
❌ NEVER change the order - SEQUENCE IS PHYSICS-BASED
❌ NEVER access bottom directly (always clear above first)
❌ NEVER use non-existent actions like 'move_from_position'
❌ NEVER generate fewer than 6 steps for bottom replacement
❌ NEVER move wrong bottom object to buffer (use scattered)
✅ MUST follow exact 6-step sequence above
✅ MUST use proper action names: move_to_buffer, move_from_buffer, move_to_position
✅ MUST clear ALL upper layers before touching bottom
✅ MUST restore ALL upper layers after placing correct bottom

🚨🚨🚨 FINAL WARNING 🚨🚨🚨
ANY OUTPUT WITH FEWER THAN 6 STEPS VIOLATES PHYSICS!
ANY DIRECT BOTTOM ACCESS VIOLATES PHYSICS!
THIS TEMPLATE OVERRIDES ALL OTHER CONFLICTING RULES!

EXPECTED OUTPUT FORMAT:
{
  "status": "success",
  "plan": [
    {"step": 1, "action": "move_to_buffer", "object": "red cube", ...},
    {"step": 2, "action": "move_to_buffer", "object": "green cube", ...},
    {"step": 3, "action": "move_to_position", "object": "yellow cube", "to": {"type": "scattered"}, ...},
    {"step": 4, "action": "move_to_position", "object": "blue cube", "to": {"type": "stack", "position": "bottom"}, ...},
    {"step": 5, "action": "move_from_buffer", "object": "green cube", ...},
    {"step": 6, "action": "move_from_buffer", "object": "red cube", ...}
  ]
}