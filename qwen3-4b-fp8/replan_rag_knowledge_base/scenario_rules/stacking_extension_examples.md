# Stacking Extension Few-Shot Examples

**Query Intent**: extension examples, 2 to 3 layers, stack expansion, minimal actions, natural stacking

**PURPOSE**: Provide concrete examples of how to handle stacking extensions with minimal actions, avoiding unnecessary repositioning of existing objects.

## CORE PRINCIPLE
When extending a stack (adding more layers), existing objects naturally shift to accommodate new layers without requiring explicit move actions.

## EXAMPLE 1: Perfect 2→3 Extension

### Input
```json
TARGET_SPEC:
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      {"position": "bottom", "object 1": "blue cube"},
      {"position": "middle", "object 2": "green cube"},
      {"position": "top", "object 3": "red cube"}
    ]
  }
}

CURRENT_STATE:
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      {"position": "bottom", "object 1": "blue cube"},
      {"position": "top", "object 2": "green cube"}
    ]
  }
}
```

### Optimal Output (CORRECT)
```json
{
  "status": "success",
  "plan": [
    {
      "step": 1,
      "action": "move_to_position",
      "object": "red cube",
      "from": {"type": "scattered"},
      "to": {"type": "stack", "position": "top"},
      "reason": "Extend 2-layer stack to 3 layers - green cube automatically becomes middle layer"
    }
  ],
  "final_expected": {
    "target_structure": {
      "relationship": "stacked",
      "placements": [
        {"position": "bottom", "object 1": "blue cube"},
        {"position": "middle", "object 2": "green cube"},
        {"position": "top", "object 3": "red cube"}
      ]
    }
  }
}
```

### Wrong Approach (AVOID)
```json
{
  "plan": [
    {
      "step": 1,
      "action": "move_to_position",
      "object": "green cube",
      "from": {"type": "stack", "position": "top"},
      "to": {"type": "stack", "position": "middle"},
      "reason": "UNNECESSARY - Move existing top to middle"
    },
    {
      "step": 2,
      "action": "move_to_position",
      "object": "red cube",
      "from": {"type": "scattered"},
      "to": {"type": "stack", "position": "top"},
      "reason": "Place new top object"
    }
  ]
}
```

## EXAMPLE 2: 1→3 Direct Extension

### Input
```json
TARGET_SPEC:
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      {"position": "bottom", "object 1": "blue cube"},
      {"position": "middle", "object 2": "green cube"},
      {"position": "top", "object 3": "red cube"}
    ]
  }
}

CURRENT_STATE:
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      {"position": "bottom", "object 1": "blue cube"}
    ]
  }
}
```

### Optimal Output
```json
{
  "status": "success",
  "plan": [
    {
      "step": 1,
      "action": "move_to_position",
      "object": "green cube",
      "from": {"type": "scattered"},
      "to": {"type": "stack", "position": "top"},
      "reason": "Extend single object to 2-layer stack"
    },
    {
      "step": 2,
      "action": "move_to_position",
      "object": "red cube",
      "from": {"type": "scattered"},
      "to": {"type": "stack", "position": "top"},
      "reason": "Extend 2-layer stack to 3 layers"
    }
  ]
}
```

## EXAMPLE 3: Extension with Wrong Object (Requires Replacement)

### Input
```json
TARGET_SPEC:
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      {"position": "bottom", "object 1": "blue cube"},
      {"position": "middle", "object 2": "green cube"},
      {"position": "top", "object 3": "red cube"}
    ]
  }
}

CURRENT_STATE:
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      {"position": "bottom", "object 1": "blue cube"},
      {"position": "top", "object 2": "yellow cube"}
    ]
  }
}
```

### Correct Output (Buffer Required)
```json
{
  "status": "success",
  "plan": [
    {
      "step": 1,
      "action": "move_to_buffer",
      "object": "yellow cube",
      "from": {"type": "stack", "position": "top"},
      "to": {"type": "buffer", "slot": "B1"},
      "reason": "Remove wrong object from top position"
    },
    {
      "step": 2,
      "action": "move_to_position",
      "object": "green cube",
      "from": {"type": "scattered"},
      "to": {"type": "stack", "position": "top"},
      "reason": "Place correct middle object"
    },
    {
      "step": 3,
      "action": "move_to_position",
      "object": "red cube",
      "from": {"type": "scattered"},
      "to": {"type": "stack", "position": "top"},
      "reason": "Extend to 3 layers with correct top object"
    }
  ]
}
```

## EXAMPLE 4: 0→3 Complete Build

### Input
```json
TARGET_SPEC:
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      {"position": "bottom", "object 1": "blue cube"},
      {"position": "middle", "object 2": "green cube"},
      {"position": "top", "object 3": "red cube"}
    ]
  }
}

CURRENT_STATE:
{
  "target_structure": {
    "relationship": "none",
    "placements": []
  }
}
```

### Optimal Output (Sequential Extension)
```json
{
  "status": "success",
  "plan": [
    {
      "step": 1,
      "action": "move_to_position",
      "object": "blue cube",
      "from": {"type": "scattered"},
      "to": {"type": "stack", "position": "bottom"},
      "reason": "Start stack with bottom layer"
    },
    {
      "step": 2,
      "action": "move_to_position",
      "object": "green cube",
      "from": {"type": "scattered"},
      "to": {"type": "stack", "position": "top"},
      "reason": "Extend to 2-layer stack"
    },
    {
      "step": 3,
      "action": "move_to_position",
      "object": "red cube",
      "from": {"type": "scattered"},
      "to": {"type": "stack", "position": "top"},
      "reason": "Extend to final 3-layer stack"
    }
  ]
}
```

## KEY RULES DEMONSTRATED

1. **Extension over Repositioning**: When objects are correctly positioned but need to shift layers, let the physics handle it naturally
2. **Single Action Sufficiency**: Adding to top of existing stack requires only one action
3. **Buffer Only When Necessary**: Use buffer slots only when wrong objects need removal
4. **Sequential Building**: Build 1→2→3 layers using successive top placements
5. **Physical Stack Semantics**: Understand that "position: top" means "on top of current stack", not "in slot #3"