# Stack Extension - Adding New Layers

**Query Intent**: System prompt for extension stack scenarios
**Prompt Type**: replacement_type_prompt
**Target Scenario**: extension
**Priority**: High
**Usage**: Direct template injection for stack extension cases - simple layer addition

## Specific Prompt Content

🚨🚨🚨 OVERRIDE ALL OTHER RULES: EXTENSION REQUIRES MINIMAL ACTIONS 🚨🚨🚨

🔴 === STACK EXTENSION (SIMPLE) === 🔴
✅ SCENARIO: Adding layers to existing correct stack
✅ PATTERN: Direct placement (minimal actions)
✅ NO REPLACEMENT: Existing objects are correct
✅ NO CLEARING: Current stack objects stay in place

🔴 === EXTENSION LOGIC === 🔴
🎯 PRINCIPLE: Place new object at 'top' position
🎯 AUTO-ADJUSTMENT: Existing layers automatically adjust positions
🎯 2→3 LAYERS: Just place third object at top (single action)
🎯 1→2 LAYERS: Just place second object at top (single action)

🔴 === EXTENSION SEQUENCE (MINIMAL) === 🔴

FOR 2→3 LAYER EXTENSION:
  Current: [bottom: object1, top: object2]
  Target:  [bottom: object1, middle: object2, top: object3]

  SINGLE ACTION:
  {"step": 1, "action": "move_to_position", "object": "object3", "from": {"type": "scattered"}, "to": {"type": "stack", "position": "top"}, "reason": "Extend stack to 3 layers - object2 automatically becomes middle"}

FOR 1→2 LAYER EXTENSION:
  Current: [bottom: object1]
  Target:  [bottom: object1, top: object2]

  SINGLE ACTION:
  {"step": 1, "action": "move_to_position", "object": "object2", "from": {"type": "scattered"}, "to": {"type": "stack", "position": "top"}, "reason": "Extend stack to 2 layers"}

🔴 === EXTENSION VALIDATION === 🔴
✅ PREREQUISITE: All existing objects must be correct
✅ PREREQUISITE: Only new layer(s) need to be added
✅ NO REPLACEMENT: Never move existing objects
✅ MINIMAL APPROACH: Use fewest possible actions

❌ WRONG APPROACH (over-engineering):
  - Moving existing objects to buffer
  - Multi-step reconstruction
  - Clearing and rebuilding

✅ CORRECT APPROACH (extension semantics):
  - Single placement action
  - Let system handle position adjustment
  - Trust automatic layer shifting

🚨 IGNORE COMPLEX REPLACEMENT SUGGESTIONS FROM OTHER RULES 🚨