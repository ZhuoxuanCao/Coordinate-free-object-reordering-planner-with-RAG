# Coordinate-Free Action Types

**Query Intent**: action types, coordinate free actions, move actions, buffer actions, object placement

**CRITICAL COMPLIANCE**: Use coordinate-free action types with mandatory top-level object field.

## MANDATORY ACTION SCHEMA

**🔴 CRITICAL REQUIREMENT**: Every action MUST have "object" field at TOP LEVEL
```json
{
  "step": N,
  "action": "action_name",
  "object": "pure_object_name",  // MANDATORY: Top-level object field
  "from": {...},
  "to": {...},
  "reason": "explanation"
}
```

## SUPPORTED ACTION TYPES

### 1. move_to_position
**Purpose**: Move object directly to target position
```json
{
  "step": 1,
  "action": "move_to_position",
  "object": "blue cube",
  "from": {"type": "scattered"},
  "to": {"type": "stack", "position": "bottom"},
  "reason": "Place object at target position"
}
```

### 2. move_to_buffer
**Purpose**: Store object temporarily in buffer
```json
{
  "step": 1,
  "action": "move_to_buffer",
  "object": "red cube",
  "from": {"type": "stack", "position": "top"},
  "to": {"type": "buffer", "slot": "B1"},
  "reason": "Temporarily store for reordering"
}
```

### 3. move_from_buffer
**Purpose**: Retrieve object from buffer to target
```json
{
  "step": 1,
  "action": "move_from_buffer",
  "object": "green cube",
  "from": {"type": "buffer", "slot": "B2"},
  "to": {"type": "stack", "position": "middle"},
  "reason": "Move from temporary storage to final position"
}
```

### 4. place_from_supply
**Purpose**: Add new object from supply (if available)
```json
{
  "step": 1,
  "action": "place_from_supply",
  "object": "yellow cube",
  "from": {"type": "supply"},
  "to": {"type": "stack", "position": "top"},
  "reason": "Add missing object from supply"
}
```

## FROM/TO FIELD SPECIFICATIONS

### From Types
```json
// Scattered objects
{"type": "scattered"}

// Stack positions
{"type": "stack", "position": "bottom|middle|top"}

// Arrangement positions
{"type": "arrangement", "position": "left|middle|right|front|back"}

// Buffer slots
{"type": "buffer", "slot": "B1|B2|B3"}

// Supply source
{"type": "supply"}
```

### To Types
```json
// Stack positions
{"type": "stack", "position": "bottom|middle|top"}

// Arrangement positions
{"type": "arrangement", "position": "left|middle|right|front|back"}

// Buffer slots
{"type": "buffer", "slot": "B1|B2|B3"}
```

## CRITICAL VALIDATION RULES

**🔴 MANDATORY FIELDS**:
- `step`: Integer sequence number
- `action`: One of the supported action types
- `object`: Pure object name (NO prefixes like "correct_", "wrong_")
- `from`: Source specification
- `to`: Target specification
- `reason`: Human-readable explanation

**🔴 FORBIDDEN PATTERNS**:
❌ `"from": {"object": "blue cube", "type": "scattered"}` // object in from
❌ `"from": {"position": "scattered"}` // wrong key name
❌ `"action": "move"` // use specific action names
❌ `"object": "correct_blue_cube"` // no descriptive prefixes

**🔴 CORRECT PATTERNS**:
✅ `"object": "blue cube"` // top-level object
✅ `"from": {"type": "scattered"}` // correct key name
✅ `"action": "move_to_position"` // specific action name
✅ `"to": {"type": "buffer", "slot": "B1"}` // buffer slot reference

## OBJECT NAMING REQUIREMENTS

**Pure Object Names Only**:
- "blue cube", "red ball", "green sphere"
- "yellow cylinder", "purple cup", "orange pyramid"
- NO prefixes: "correct_", "wrong_", "target_", "current_"

**Free Vocabulary Support**:
- Any color + object type combination
- Support for: cube, ball, sphere, cylinder, cup, pyramid, box, etc.
- Consistent lowercase formatting preferred