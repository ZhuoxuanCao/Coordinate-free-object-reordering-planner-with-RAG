# Unified Target Structure Format

**Query Intent**: target structure json, relationship schema, object arrangement definitions, perception output compatibility

**Authoritative Source**: All input/output object relationship JSON must comply with unified format specifications. This rule document is authoritative and must not be deviated from.

## 1. Single Object
- Treated as special stack with only one object
- Use relationship = `stacked_left` / `stacked_middle` / `stacked_right`
- `placements` contains only one object entry, without position field

```json
{
  "target_structure": {
    "relationship": "stacked_left",
    "placements": [
      { "object": "red cube" }
    ]
  }
}
```

## 2. 两个物体 (Two Objects)
仅允许三种关系：`stacked`、`separated_left_right`、`separated_front_back`。

### 2.1 垂直堆叠 stacked
```json
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "top",    "object 2": "red cube" }
    ]
  }
}
```

### 2.2 左右分开 separated_left_right
```json
{
  "target_structure": {
    "relationship": "separated_left_right",
    "placements": [
      { "position": "left",  "object 1": "green cube" },
      { "position": "right", "object 2": "red cube" }
    ]
  }
}
```

### 2.3 前后分开 separated_front_back
```json
{
  "target_structure": {
    "relationship": "separated_front_back",
    "placements": [
      { "position": "front", "object 1": "green cube" },
      { "position": "back",  "object 2": "blue cube" }
    ]
  }
}
```

## 3. 三个物体 (Three Objects)
支持四大类：`stacked`、`pyramid`、`stacked_and_separated_left|right`、`separate_horizontal|vertical`。

### 3.1 垂直堆叠 stacked
```json
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "middle", "object 2": "green cube" },
      { "position": "top",    "object 3": "red cube" }
    ]
  }
}
```

### 3.2 金字塔 pyramid
```json
{
  "target_structure": {
    "relationship": "pyramid",
    "placements": [
      { "position": "bottom left",  "object 1": "green cube" },
      { "position": "bottom right", "object 2": "red cube" },
      { "position": "top",          "object 3": "blue cube" }
    ]
  }
}
```

### 3.3 2+1 组合
- `stacked_and_separated_left`：独立方块位于左侧
- `stacked_and_separated_right`：独立方块位于右侧

```json
{
  "target_structure": {
    "relationship": "stacked_and_separated_left",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "top",    "object 2": "red cube" },
      { "position": "left",   "object 3": "green cube" }
    ]
  }
}
```

### 3.4 三物体分开
- `separate_horizontal`：按 left / middle / right 排列
- `separate_vertical`：按 bottom / middle / top （对应前后分层）

```json
{
  "target_structure": {
    "relationship": "separate_horizontal",
    "placements": [
      { "position": "left",   "object 1": "blue cube" },
      { "position": "middle", "object 2": "red cube" },
      { "position": "right",  "object 3": "green cube" }
    ]
  }
}
```

```json
{
  "target_structure": {
    "relationship": "separate_vertical",
    "placements": [
      { "position": "bottom", "object 1": "blue cube" },
      { "position": "middle", "object 2": "red cube" },
      { "position": "top",    "object 3": "green cube" }
    ]
  }
}
```

## 4. 通用约束
- 字段名必须与以上示例严格一致（`object` 或 `object 1/2/3`）。
- `placements` 数组长度与物体数量完全一致，不允许附加条目。
- 不得引入坐标、额外描述字段或英文注释。
- 颜色 + 物体类型的描述完全自由，但需为字符串。
- 如果产生 `plan` 行为输出，必须在单独规则中定义；本文件仅约束 `target_structure` 格式。
