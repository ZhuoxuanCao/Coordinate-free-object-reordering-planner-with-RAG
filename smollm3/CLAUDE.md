# CLAUDE.md

This file guides Claude Code when working on the replan/smollm3 repository.

## Project Overview

A coordinate-free object reordering planner using SmolLM3 with RAG (Retrieval-Augmented Generation) architecture. The system transforms current object arrangements into target relationship structures without spatial coordinates, focusing on logical relationships and using predefined buffer slots for temporary storage.

## Core Architecture

### Coordinate-Free Design Philosophy
- **Input/Output**: Pure relationship descriptions without coordinates
- **Object Representation**: Complete object descriptors with flexible field naming (`object`, `object 1`, `object 2`, `object 3`)
- **Spatial Abstraction**: Position relationships (bottom/middle/top, left/middle/right, front/back)
- **Buffer Management**: Predefined slots B1/B2/B3 with internal coordinate handling

### RAG System Components
- **Knowledge Base**: External rules in `replan_rag_knowledge_base/`
- **Embedding Model**: all-MiniLM-L6-v2 for semantic similarity
- **Language Model**: HuggingFaceTB/SmolLM3-3B for plan generation
- **Retrieval**: Dynamic rule selection based on scenario classification

### Enhanced Validation System
- **Object Extraction**: Flexible object field parsing with `extract_object_value()` function
- **Position Mapping**: Automatic conversion from placements to position-object maps
- **Plan Consistency**: Enhanced validation including buffer slot checks and redundancy detection
- **Target Structure Validation**: Comprehensive relationship-specific position requirements
- **Bottom-up Order Enforcement**: Automatic validation of stacking sequence in plans

## Supported Relationship Types

### 1. Single Object Stacked
```json
{
  "target_structure": {
    "relationship": "stacked_left|stacked_middle|stacked_right",
    "placements": [
      {"object": "red cube"}
    ]
  }
}
```

### 2. Two Object Relationships

#### Stacked (2 objects)
```json
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      {"position": "bottom", "object 1": "blue cube"},
      {"position": "top", "object 2": "red cube"}
    ]
  }
}
```

#### Separated Left-Right (2 objects)
```json
{
  "target_structure": {
    "relationship": "separated_left_right",
    "placements": [
      {"position": "left", "object 1": "green cube"},
      {"position": "right", "object 2": "red cube"}
    ]
  }
}
```

#### Separated Front-Back (2 objects)
```json
{
  "target_structure": {
    "relationship": "separated_front_back",
    "placements": [
      {"position": "front", "object 1": "green cube"},
      {"position": "back", "object 2": "blue cube"}
    ]
  }
}
```

### 3. Three Object Relationships

#### Stacked (3 objects)
```json
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
```

#### Pyramid
```json
{
  "target_structure": {
    "relationship": "pyramid",
    "placements": [
      {"position": "bottom left", "object 1": "green cube"},
      {"position": "bottom right", "object 2": "red cube"},
      {"position": "top", "object 3": "blue cube"}
    ]
  }
}
```

#### Stacked + Separated Combinations
```json
{
  "target_structure": {
    "relationship": "stacked_and_separated_left",
    "placements": [
      {"position": "bottom", "object 1": "blue cube"},
      {"position": "top", "object 2": "red cube"},
      {"position": "left", "object 3": "green cube"}
    ]
  }
}
```

#### Three Object Horizontal/Vertical Separation
```json
{
  "target_structure": {
    "relationship": "separate_horizontal",
    "placements": [
      {"position": "left", "object 1": "blue cube"},
      {"position": "middle", "object 2": "red cube"},
      {"position": "right", "object 3": "green cube"}
    ]
  }
}
```

## Input Format

### Target Specification (New Format)
The target specification uses the unified format with flexible object field naming:

```json
{
  "target_structure": {
    "relationship": "relationship_type",
    "placements": [
      {"position": "position_name", "object 1": "object_descriptor"},
      {"position": "position_name", "object 2": "object_descriptor"},
      {"position": "position_name", "object 3": "object_descriptor"}
    ]
  }
}
```

**Key Changes from Previous Format:**
- Object fields now use `"object 1"`, `"object 2"`, `"object 3"` instead of `"object"`
- Single objects use just `"object"` without position field
- Supports extended relationship types including pyramids and combinations

### Current State (New Format)
Current state now uses the same target_structure format:

```json
{
  "target_structure": {
    "relationship": "relationship_type",
    "placements": [
      {"position": "position_name", "object 1": "object_descriptor"},
      {"position": "position_name", "object 2": "object_descriptor"}
    ]
  }
}
```

**Legacy Current State Format (Still Supported):**
```json
{
  "relationship": "stacked|separated_left_right|separated_front_back|none",
  "stack": [  // for stacked relationships
    {"position": "bottom", "object": "blue cube"}
  ],
  "placements": [  // for separated relationships
    {"position": "left", "object": "red cube"}
  ],
  "scattered": [  // objects without fixed positions
    {"object": "green cube"},
    {"object": "yellow ball"}
  ]
}
```

## Output Format

### Action Plan Output
```json
{
  "status": "success|blocked",
  "plan": [
    {
      "step": 1,
      "action": "move_to_buffer|move_from_buffer|move_to_position|place_from_supply",
      "from": {"type": "stack|arrangement|scattered|buffer", "position": "optional", "slot": "optional"},
      "to": {"type": "stack|arrangement|buffer", "position": "optional", "slot": "optional"},
      "object": "pure_object_name",
      "reason": "explanation"
    }
  ],
  "final_expected": {
    "relationship": "target_relationship",
    "placements": [...]
  }
}
```

### Pure Relationship Output
```json
{
  "target_structure": {
    "relationship": "relationship_type",
    "placements": [
      {"position": "position_name", "object": "object_descriptor"}
    ]
  }
}
```

## System Configuration

### Predefined Buffer Slots
```python
BUFFER_SLOTS = {
    "B1": [180, 300, 150],
    "B2": [280, 300, 150],
    "B3": [180, 340, 150]
}
```

### Supported Relationships
```python
SUPPORTED_RELATIONSHIPS = [
    "stacked",                        # 2 or 3 objects vertically
    "stacked_left",                  # Single object positioned left
    "stacked_middle",                # Single object positioned middle
    "stacked_right",                 # Single object positioned right
    "separated_left_right",          # 2 objects: left/right
    "separated_front_back",          # 2 objects: front/back
    "separate_horizontal",           # 3 objects: left/middle/right
    "separate_vertical",             # 3 objects: bottom/middle/top
    "stacked_and_separated_left",    # 2-stack + 1 left: bottom/top/left
    "stacked_and_separated_right",   # 2-stack + 1 right: bottom/top/right
    "pyramid",                       # 3 objects: bottom left/bottom right/top
    "none"                           # no structure state
]
```

## Knowledge Base Structure

### Core Rules (`core_rules/`)
- `unified_output_format.md`: Comprehensive JSON structure requirements for all object counts
- `coordinate_free_actions.md`: Action type definitions and validation requirements
- `stacked_output_format.md`: Stacked relationship specifics
- `execution_order.md`: Action sequencing and timing rules
- `task_definition.md`: Core task and constraint definitions

### Relationship Rules (`relationship_rules/`)
- `stacked.md`: All stacked relationship variants (single, dual, triple objects)
- `separated_left_right.md`: Horizontal left-right arrangements
- `separated_front_back.md`: Horizontal front-back arrangements
- `pyramid.md`: Pyramid arrangement structures
- `stacked_and_separated_left.md` / `stacked_and_separated_right.md`: Combined arrangements

### Scenario Rules (`scenario_rules/`)
- `stacked_building.md`: Stack construction scenarios with new format examples
- `buffer_management.md`: Buffer slot usage and temporary storage strategies

### Output Format (`output_format/`)
- `json_structure.md`: JSON formatting and validation rules

### Pattern Rules (`pattern_rules/`)
- `bottom_up_building.md`: Construction sequence patterns

## Key Design Principles

### 1. Coordinate-Free Operation
- **NO spatial coordinates** in input/output (except internal buffer management)
- Focus on **logical relationships** between objects
- **Position-based** rather than coordinate-based planning

### 2. Flexible Object Field Naming
- Support multiple object field formats: `"object"`, `"object 1"`, `"object 2"`, `"object 3"`
- **Automatic extraction** with `extract_object_value()` function
- **NO descriptive prefixes**: ❌ "correct_blue_cube", "wrong_red_ball"
- Support **any object vocabulary**: cube, ball, sphere, cylinder, cup, pyramid

### 3. Enhanced Buffer Management
- **Predefined slots**: B1, B2, B3 with fixed coordinates `[x, y, z]`
- **Validation enforcement**: Buffer slot references must be valid (B1/B2/B3)
- **Temporary storage**: For complex reordering operations
- **Consistency checks**: Prevent redundant buffer operations

### 4. Comprehensive Validation System
- **Target structure validation**: Relationship-specific position requirements
- **Plan consistency checks**: Prevent object conflicts and redundant actions
- **Position completeness**: Ensure all required positions are filled
- **Bottom-up enforcement**: Automatic validation of stacking sequence
- **Object uniqueness**: Prevent duplicate object placements

## Action Types

### Core Actions
- `move_to_buffer`: Store object temporarily in buffer slot
- `move_from_buffer`: Retrieve object from buffer slot
- `move_to_position`: Direct placement at target position
- `place_from_supply`: Add new object from supply (if available)

### Enhanced Action Parameters
- `step`: Integer sequence number (required)
- `action`: Specific action type (required)
- `object`: Pure object name at **TOP LEVEL** (required, no prefixes)
- `from`: Source location specification (required)
- `to`: Target location specification (required)
- `reason`: Human-readable explanation (required)

### Validation Requirements
- **Top-level object field**: Object must be specified at action level, not inside from/to
- **Buffer slot validation**: B1/B2/B3 slots must be valid and referenced correctly
- **Redundancy prevention**: Actions cannot have identical from/to specifications
- **Position uniqueness**: Same position cannot be assigned to multiple objects
- **Object uniqueness**: Same object cannot be placed in multiple positions

## Scenario Classification

### Template-Based Classification
The system uses embedding similarity with predefined templates:

```python
templates = {
    "stacked_building": [
        "stacked arrangement vertical tower building",
        "all objects scattered need stacking bottom up",
        "partial stack need completion"
    ],
    "separated_arrangement": [
        "separated_left_right arrangement horizontal separation",
        "all objects scattered need separation",
        "partial separation need completion"
    ],
    # ... more scenarios
}
```

### RAG Retrieval Process
1. **Scenario Classification**: Embedding-based similarity matching
2. **Rule Retrieval**: Semantic search in knowledge base
3. **Rule Filtering**: Context-aware filtering based on relationship type
4. **Prompt Construction**: Dynamic assembly of relevant rules

## Testing

### Current Test Cases
```bash
python replan_rag_system.py
```

**Test 1**: Stacked Relationship - Missing Middle Layer
- **Target**: 3-object vertical stack (bottom: blue cube, middle: green cube, top: red cube)
- **Current State**: Partial stack with bottom: blue cube, top: green cube (missing middle, wrong top)
- **Expected**: Complete reordering with proper middle layer insertion
- **Challenge**: Requires moving top object to make room for middle layer

**Test 2**: Stacked Relationship - Wrong Top Object
- **Target**: Same 3-object vertical stack specification
- **Current State**: Complete stack but with green cube at top instead of red cube
- **Expected**: Buffer-based correction to replace wrong top object
- **Challenge**: Requires buffer usage to swap objects without disturbing lower layers

**Key Format Updates:**
- Both current state and target use `target_structure` wrapper format
- Consistent `"object 1"`, `"object 2"`, `"object 3"` field naming throughout
- Enhanced validation ensures position completeness and object correctness
- Automatic detection of missing positions and object mismatches

## Dependencies

### Core Dependencies
```bash
pip install torch transformers sentence-transformers scikit-learn numpy
```

### Model Requirements
- **Language Model**: HuggingFaceTB/SmolLM3-3B
- **Embedding Model**: all-MiniLM-L6-v2
- **Hardware**: CUDA-compatible GPU recommended

## Usage Examples

### Basic Stacked Arrangement (New Format)
```python
target_spec = {
    "target_structure": {
        "relationship": "stacked",
        "placements": [
            {"position": "bottom", "object 1": "blue cube"},
            {"position": "middle", "object 2": "green cube"},
            {"position": "top", "object 3": "red cube"}
        ]
    }
}

# New current state format (using target_structure)
current_state = {
    "target_structure": {
        "relationship": "stacked",
        "placements": [
            {"position": "bottom", "object 1": "blue cube"},
            {"position": "top", "object 2": "green cube"},
        ]
    }
}

result = generate_replan(target_spec, current_state)
```

### Complex Reordering with Buffer (New Format)
```python
# When objects are in wrong positions - new format
current_state = {
    "target_structure": {
        "relationship": "stacked",
        "placements": [
            {"position": "bottom", "object 1": "blue cube"},
            {"position": "middle", "object 2": "green cube"},
            {"position": "top", "object 3": "green cube"}  # wrong object
        ]
    }
}
# System will use buffer for temporary storage during reordering
```

### Legacy Format Support
```python
# Legacy current state format (still supported)
current_state = {
    "relationship": "none",
    "scattered": [
        {"object": "red cube"},
        {"object": "green cube"},
        {"object": "blue cube"}
    ]
}
```

## Object Vocabulary Support

### Supported Object Types
- **Geometric Shapes**: cube, ball, sphere, cylinder, pyramid
- **Colors**: red, blue, green, yellow, orange, purple, black, white
- **Containers**: cup, bowl, box
- **Free-form**: Any descriptive combination

### Object Naming Rules
- **Complete descriptors**: "blue cube", "red ball", "green cylinder"
- **Consistent formatting**: "[color] [type]" pattern
- **No abbreviations**: Use full color and type names
- **Case sensitivity**: Lowercase preferred for consistency

## Enhanced Error Handling & Validation

### Core Validation Functions
- `extract_object_value()`: Flexible object field extraction from placements
- `build_position_object_map()`: Convert placements to position-object mapping
- `collect_objects_list()`: Extract all objects from placements in order
- `validate_target_structure_payload()`: Comprehensive target structure validation
- `enforce_plan_consistency()`: Plan-level consistency and conflict detection

### Validation Rules
- **Object field requirements**: Must use supported field names (`object`, `object 1/2/3`)
- **Buffer slot validation**: Must reference valid B1/B2/B3 slots
- **Position completeness**: All relationship-required positions must be present
- **Object uniqueness**: No duplicate object assignments within same plan
- **Action consistency**: No redundant or conflicting actions

### Common Error Scenarios
- **Missing object fields**: Placement missing valid object description
- **Invalid positions**: Position names not matching relationship requirements
- **Buffer slot errors**: Invalid slot references or missing slot specifications
- **Plan conflicts**: Same object placed multiple times or redundant actions
- **Relationship mismatches**: Positions don't match relationship type requirements

## Performance Considerations

### Optimization Strategies
- **Minimal actions**: Prefer direct placement over buffer usage
- **Sequential efficiency**: Logical ordering of construction steps
- **Context length**: Dynamic rule selection to stay within model limits
- **Caching**: Embedding cache for repeated queries

### Memory Management
- **Rule filtering**: Remove irrelevant rules before prompt construction
- **Context truncation**: Limit rule content to essential information
- **Batch processing**: Handle multiple scenarios efficiently

## Future Enhancements

### Planned Features
- **Pyramid relationships**: 3D hierarchical arrangements
- **Multi-step planning**: Complex sequences requiring multiple phases
- **Dynamic object creation**: Support for adding new objects
- **Constraint satisfaction**: Advanced positioning requirements

### Research Directions
- **Few-shot learning**: Adaptation to new relationship types
- **Multimodal integration**: Visual perception input
- **Real-time planning**: Streaming plan generation
- **Collaborative arrangements**: Multi-agent coordination

## Troubleshooting

### Common Issues
1. **JSON parsing errors**: Check output format compliance
2. **Buffer slot errors**: Verify B1/B2/B3 usage
3. **Object naming issues**: Ensure pure object names without prefixes
4. **Relationship mismatches**: Verify input format consistency

### Debug Features
- **Scenario classification logging**: View similarity scores
- **Rule retrieval details**: See which rules were selected
- **Prompt inspection**: Examine generated system/user prompts
- **Validation feedback**: Detailed error messages for format issues

### Development Tools
```bash
# Run current test suite
python replan_rag_system.py

# Test specific scenarios
python -c "from replan_rag_system import generate_replan; ..."

# Inspect knowledge base structure
find replan_rag_knowledge_base -name "*.md" | head -10

# Check model loading and validation functions
python -c "from replan_rag_system import ReplanRAGSystem, extract_object_value; ReplanRAGSystem()"

# Test object extraction function
python -c "from replan_rag_system import extract_object_value; print(extract_object_value({'position': 'bottom', 'object 1': 'blue cube'}))"

# Test position mapping function
python -c "from replan_rag_system import build_position_object_map; print(build_position_object_map([{'position': 'bottom', 'object 1': 'blue cube'}]))"
```

### Validation Testing
```bash
# Test target structure validation
python -c "
from replan_rag_system import validate_target_structure_payload
validate_target_structure_payload({
    'relationship': 'stacked',
    'placements': [
        {'position': 'bottom', 'object 1': 'blue cube'},
        {'position': 'middle', 'object 2': 'green cube'},
        {'position': 'top', 'object 3': 'red cube'}
    ]
})
print('Validation passed')
"
```