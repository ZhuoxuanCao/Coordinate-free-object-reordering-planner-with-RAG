# Stack Replacement Pattern

**Query Intent**: stack object replacement, wrong object correction, clear-before-place operations, position-specific replacement

**CRITICAL COMPLIANCE**: When replacing objects in existing stack positions, ALWAYS clear above layers first, then place correct object, then restore cleared layers. NEVER directly place object on occupied position.

## PHYSICAL ACCESS RULES

**FUNDAMENTAL CONSTRAINT**: Cannot access middle/bottom objects when upper layers exist.

- ❌ **FORBIDDEN**: Direct access to blocked positions (move middle when top exists)
- ✅ **REQUIRED**: Clear above layers first using top→middle→bottom sequence
- ✅ **REQUIRED**: Restore preserved objects using bottom→middle→top sequence

## OBJECT LIFECYCLE CLASSIFICATION

### **Critical Distinction**: Keep vs Remove
- **Keep Objects**: Objects that appear in target structure but currently in wrong positions
  - Use `move_to_buffer` for temporary storage
  - Must be restored to correct target position later
  - Example: red cube in target but currently at wrong position

- **Remove Objects**: Objects that do NOT appear anywhere in target structure
  - Use `move_to_position` to `scattered` for permanent removal
  - Do NOT use buffer (buffer implies restoration)
  - Do NOT restore to stack - they are unwanted objects
  - Example: yellow cube not present in target structure

## SCENARIO CLASSIFICATION

### **Extension vs Replacement**
- **Extension**: Adding new layer to existing stack (2→3 layers) - use `stack_extension.md`
- **Replacement**: Correcting wrong object in existing position - use this rule
- **Mixed**: Both extension and replacement needed - combine both patterns

### **Replacement Types by Physical Complexity**
- **Top Replacement**: Direct replacement (simplest case)
- **Middle Replacement**: Clear top → Replace middle → Restore top
- **Bottom Replacement**: Clear entire stack → Replace bottom → Rebuild stack

## MANDATORY REPLACEMENT PATTERNS

### Pattern A - Top Position Replacement
When only top object is wrong:
```json
[
  {
    "step": 1,
    "action": "move_to_position",
    "object": "wrong top object",
    "from": { "type": "stack", "position": "top" },
    "to": { "type": "scattered" },
    "reason": "Remove incorrect top object not needed in target"
  },
  {
    "step": 2,
    "action": "move_to_position",
    "object": "correct top object",
    "from": { "type": "scattered" },
    "to": { "type": "stack", "position": "top" },
    "reason": "Place correct top object"
  }
]
```

### Pattern B - Middle Position Replacement
When middle object is wrong (most common case):

**Physical Constraint**: Must clear top layer first to access middle.

```json
[
  {
    "step": 1,
    "action": "move_to_buffer",
    "object": "red cube",
    "from": { "type": "stack", "position": "top" },
    "to": { "type": "buffer", "slot": "B1" },
    "reason": "Clear top to access middle layer"
  },
  {
    "step": 2,
    "action": "move_to_position",
    "object": "yellow cube",
    "from": { "type": "stack", "position": "middle" },
    "to": { "type": "scattered" },
    "reason": "Remove incorrect middle object not present in target"
  },
  {
    "step": 3,
    "action": "move_to_position",
    "object": "green cube",
    "from": { "type": "scattered" },
    "to": { "type": "stack", "position": "middle" },
    "reason": "Place correct middle object"
  },
  {
    "step": 4,
    "action": "move_from_buffer",
    "object": "red cube",
    "from": { "type": "buffer", "slot": "B1" },
    "to": { "type": "stack", "position": "top" },
    "reason": "Restore top object"
  }
]
```

**Key Points**:
- Step 1: Clear blocking layer (red cube → buffer for restoration)
- Step 2: Remove unwanted object (yellow cube → scattered, NOT buffer)
- Step 3: Place target object (green cube → middle position)
- Step 4: Restore preserved object (red cube → top position)

### Pattern C - Bottom Position Replacement
When bottom object is wrong (most complex case):
```json
[
  {
    "step": 1,
    "action": "move_to_buffer",
    "object": "red cube",
    "from": { "type": "stack", "position": "top" },
    "to": { "type": "buffer", "slot": "B1" },
    "reason": "Clear top to access lower layers"
  },
  {
    "step": 2,
    "action": "move_to_buffer",
    "object": "green cube",
    "from": { "type": "stack", "position": "middle" },
    "to": { "type": "buffer", "slot": "B2" },
    "reason": "Clear middle to access bottom layer"
  },
  {
    "step": 3,
    "action": "move_to_position",
    "object": "wrong bottom object",
    "from": { "type": "stack", "position": "bottom" },
    "to": { "type": "scattered" },
    "reason": "Remove incorrect bottom object not needed in target"
  },
  {
    "step": 4,
    "action": "move_to_position",
    "object": "blue cube",
    "from": { "type": "scattered" },
    "to": { "type": "stack", "position": "bottom" },
    "reason": "Place correct bottom foundation"
  },
  {
    "step": 5,
    "action": "move_from_buffer",
    "object": "green cube",
    "from": { "type": "buffer", "slot": "B2" },
    "to": { "type": "stack", "position": "middle" },
    "reason": "Restore middle layer"
  },
  {
    "step": 6,
    "action": "move_from_buffer",
    "object": "red cube",
    "from": { "type": "buffer", "slot": "B1" },
    "to": { "type": "stack", "position": "top" },
    "reason": "Restore top layer"
  }
]
```

## OBJECT LIFECYCLE MANAGEMENT

### **Objects to Keep (Use Buffer)**
- Objects that appear in target structure but are currently in wrong positions
- Must be temporarily stored and later restored
- Use `move_to_buffer` → `move_from_buffer` pattern

### **Objects to Remove (Use Scattered)**
- Objects that do NOT appear anywhere in target structure
- Should be permanently removed from stack
- Use `move_to_position` to `scattered` (no restoration needed)

## CRITICAL REPLACEMENT RULES

### **Access Constraints**
- ❌ NEVER directly place object on occupied position
- ✅ ALWAYS clear above layers before accessing below layers
- ✅ Follow top→middle→bottom clearing order
- ✅ Follow bottom→middle→top restoration order

### **Buffer Management**
- Use different buffer slots (B1, B2, B3) for multiple objects
- Clear buffers in reverse order of filling
- Ensure all buffers are empty at plan completion

### **Position Validation**
- Before each `move_to_position` to stack, verify target position is empty
- Account for stack height changes during replacement process
- Maintain proper layer dependencies

## COMPLETE REAL-WORLD EXAMPLE

**Scenario**: Middle layer replacement with physical constraints

**Current State**:
- Stack: bottom=blue cube, middle=yellow cube, top=red cube
- Scattered: green cube

**Target State**:
- Stack: bottom=blue cube, middle=green cube, top=red cube

**Analysis**:
- blue cube: ✅ correct position (keep)
- yellow cube: ❌ wrong object, not in target (remove to scattered)
- red cube: ✅ correct object, correct position (temporarily move to access middle)
- green cube: ✅ target object, needs placement at middle

**Correct Plan (Pattern B)**:
```json
[
  {
    "step": 1,
    "action": "move_to_buffer",
    "object": "red cube",
    "from": { "type": "stack", "position": "top" },
    "to": { "type": "buffer", "slot": "B1" },
    "reason": "Clear top to access middle layer"
  },
  {
    "step": 2,
    "action": "move_to_position",
    "object": "yellow cube",
    "from": { "type": "stack", "position": "middle" },
    "to": { "type": "scattered" },
    "reason": "Remove incorrect object not present in target"
  },
  {
    "step": 3,
    "action": "move_to_position",
    "object": "green cube",
    "from": { "type": "scattered" },
    "to": { "type": "stack", "position": "middle" },
    "reason": "Place correct middle object"
  },
  {
    "step": 4,
    "action": "move_from_buffer",
    "object": "red cube",
    "from": { "type": "buffer", "slot": "B1" },
    "to": { "type": "stack", "position": "top" },
    "reason": "Restore top object to complete target structure"
  }
]
```

**Final Result**: bottom=blue cube, middle=green cube, top=red cube ✅

## VALIDATION CHECKLIST
- ✅ No direct placement on occupied positions
- ✅ Proper clear-above-first sequence followed
- ✅ Objects not in target moved to scattered, not buffer
- ✅ Objects in target but wrong position moved through buffer
- ✅ All buffer slots empty at completion
- ✅ Final structure matches target exactly

## FORBIDDEN PATTERNS

### **Physical Violations**
- ❌ Direct access to blocked positions: `move_to_position yellow cube from middle` when top exists
- ❌ Placing objects on occupied positions: `move_to_position green cube to middle` when yellow occupies it
- ❌ Skipping clear-above-first sequence: accessing middle without clearing top

### **Object Lifecycle Violations**
- ❌ Buffering objects for removal: `move_to_buffer yellow cube` when yellow not in target
- ❌ Restoring unwanted objects: `move_from_buffer yellow cube to stack` when yellow not needed
- ❌ Using scattered for temporary storage: should use buffer for objects that need restoration

### **Common Error Examples**
```json
// ❌ WRONG: Direct middle access while top exists
{"action": "move_to_buffer", "object": "yellow cube", "from": {"type": "stack", "position": "middle"}}

// ❌ WRONG: Restoring unwanted object
{"action": "move_from_buffer", "object": "yellow cube", "to": {"type": "stack", "position": "middle"}}

// ✅ CORRECT: Clear top first, then access middle
[
  {"action": "move_to_buffer", "object": "red cube", "from": {"type": "stack", "position": "top"}},
  {"action": "move_to_position", "object": "yellow cube", "to": {"type": "scattered"}}
]
```