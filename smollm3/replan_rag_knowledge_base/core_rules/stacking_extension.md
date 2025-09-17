# Stacking Extension Rules

**Query Intent**: stacking extension, layer expansion, natural stacking, physical stacking semantics, 2 to 3 layers, incremental stacking

**CRITICAL PRINCIPLE**: Stacking follows physical semantics where adding objects on top naturally extends the stack height without requiring explicit repositioning of existing objects.

## STACKING EXTENSION vs REPLACEMENT

### Extension Scenarios (Preferred - Minimal Actions)
- **0→1 layer**: Place first object at bottom
- **1→2 layers**: Add second object on top (first becomes bottom, second becomes top)
- **2→3 layers**: Add third object on top (bottom stays, top becomes middle, new becomes top)
- **Bottom objects match**: Existing bottom layer objects are correctly positioned

### Replacement Scenarios (Requires Buffer)
- **Wrong object at any layer**: Current object doesn't match target specification
- **Layer content mismatch**: Need to change objects in existing positions
- **Complete rebuild**: Multiple objects in wrong positions

## EXTENSION ACTION PATTERNS

### 2→3 Layer Extension (Most Common)
**Current State**: [bottom: correct_object, top: should_be_middle_object]
**Target**: [bottom: correct_object, middle: should_be_middle_object, top: new_object]

**CORRECT APPROACH** (Single Action):
```json
{
  "step": 1,
  "action": "move_to_position",
  "object": "new_object",
  "from": {"type": "scattered"},
  "to": {"type": "stack", "position": "top"},
  "reason": "Extend stack to 3 layers - existing top automatically becomes middle"
}
```

**INCORRECT APPROACH** (Unnecessary Double Action):
```json
[
  {"action": "move_to_position", "object": "existing_top", "from": {"type": "stack", "position": "top"}, "to": {"type": "stack", "position": "middle"}},
  {"action": "move_to_position", "object": "new_object", "from": {"type": "scattered"}, "to": {"type": "stack", "position": "top"}}
]
```

### 1→2 Layer Extension
**Current State**: [bottom: correct_object]
**Target**: [bottom: correct_object, top: new_object]

```json
{
  "action": "move_to_position",
  "object": "new_object",
  "from": {"type": "scattered"},
  "to": {"type": "stack", "position": "top"},
  "reason": "Extend single object to 2-layer stack"
}
```

## PHYSICAL STACKING SEMANTICS

### Natural Layer Relabeling
- When placing object on "top" of existing stack, previous layers automatically adjust
- **2-layer stack**: bottom + top
- **Add new top**: bottom + middle + top (previous top becomes middle)
- **No explicit move required** for existing objects

### Extension Detection Criteria
1. **Layer count increase**: current_layers < target_layers
2. **Bottom alignment**: bottom objects match between current and target
3. **Correct sequence**: existing objects will be in correct relative positions after extension

## VALIDATION ADJUSTMENTS

### Allow Extension Operations
- **"Overwrite" top position** is allowed when extending stack height
- **Same position multiple actions** allowed for extension (not replacement)
- **Skip validation** for objects that will be correctly positioned after extension

### Maintain Restrictions for True Conflicts
- **Buffer required** when changing content of bottom/middle layers
- **No simultaneous placement** of different objects at same final position
- **Preserve bottom-up building** for complete reconstructions

## EXAMPLES

### Example 1: Perfect Extension
```
Current: [blue(bottom), green(top)]
Target:  [blue(bottom), green(middle), red(top)]
Action:  place red → top
Result:  Natural 3-layer stack without moving green
```

### Example 2: Extension with Wrong Middle
```
Current: [blue(bottom), wrong_object(top)]
Target:  [blue(bottom), green(middle), red(top)]
Actions: 1) move wrong_object → buffer
         2) place green → middle
         3) place red → top
```

### Example 3: Pure Extension Chain
```
Current: []
Target:  [blue(bottom), green(middle), red(top)]
Actions: 1) place blue → bottom
         2) place green → top    (creates 2-layer)
         3) place red → top      (extends to 3-layer)
```

## INTEGRATION WITH EXISTING RULES

### Modified NO OVERWRITE Rule
- **Original**: "Never place object onto occupied position"
- **Updated**: "Never overwrite incorrect objects; extension of stack height via top placement is preferred"

### Modified Uniqueness Rule
- **Original**: "Each position addressed exactly once"
- **Updated**: "Each final position filled exactly once; intermediate extensions allowed"

### Bottom-Up Building Compatibility
- Extension approach is compatible with bottom-up principle
- Extensions naturally follow layer dependency (can't add top without bottom)
- Preserves structural integrity of lower layers