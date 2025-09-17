# 输入的json类型与格式总结

## 一个物体

一个物体只有一种情况，就是单独放在桌面上，为了方便命名，我们也叫他stack，但是只有一个object，以下是相关的代码和示例

```
def format_single_cube_json(result):
    """单个方块的JSON格式"""
    # 根据位置确定relationship类型
    position = result.get('position', 'middle')  # 默认中间
    relationship_map = {
        'left': 'stacked_left',
        'middle': 'stacked_middle', 
        'right': 'stacked_right'
    }
    
    relationship = relationship_map.get(position, 'stacked_middle')
    
    # 组合object和color字段
    object_type = result.get('object', 'cube')  # 默认cube
    color = result.get('color', 'unknown')      # 默认unknown
    combined_object = f"{color} {object_type}"
    
    return {
        "target_structure": {
            "relationship": relationship,
            "placements": [
                {"object": combined_object}
            ]
        }
    }
    
    #例子，一个在左边的红色方块
    {
  "target_structure": {
    "relationship": "stacked_left",
    "placements": [
      {
        "object": "red cube"
      }
    ]
  }
}
```

## 2个物体

两个物体有两种情况，即堆叠（stack）和分开（separate），其中分开又被分为左右和前后分开。以下是示例。

```
# 堆叠
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      {"position": "bottom", "object 1": "<color + type>"},
      {"position": "top", "object 2": "<color + type>"}
    ]
  }
}

# 左右分开
{
  "target_structure": {
    "relationship": "separated_left_right",
    "placements": [
      {"position": "left", "object 1": "<color + type>"},
      {"position": "right", "object 2": "<color + type>"}
    ]
  }
}

# 前后分开
{
  "target_structure": {
    "relationship": "separated_front_back",
    "placements": [
      {"position": "front", "object 1": "<color + type>"},
      {"position": "back", "object 2": "<color + type>"}
    ]
  }
}
```

## 3个物体

3个物体我们分为4种情况，堆叠（即垂直从下到上的一个柱子），金字塔（底层左右各一个方块然后第二层中间一个），2+1（一个两个方块上下堆叠的柱子以及一个独立的方块），separate（三个方块分开摆放）。其中2+1分为2+1左和2+1右，取决于独立的方块的位置；separate也分为左右分开和前后分开。以下是示例。

```
# 堆叠
{
  "target_structure": {
    "relationship": "stacked",
    "placements": [
      {"position": "bottom", "object 1": "<color + type>"},
      {"position": "middle", "object 2": "<color + type>"},
      {"position": "top", "object 3": "<color + type>"}
    ]
  }
}

# 金字塔
{
  "target_structure": {
    "relationship": "pyramid",
    "placements": [
      { "position": "bottom left", "object 1": "<color + type>" },
      { "position": "bottom right", "object 2": "<color + type>" },
      { "position": "top", "object 3": "<color + type>" }
    ]
  }
}

# 2+1左
{
  "target_structure": {
    "relationship": "stacked_and_separated_left",
    "placements": [
      { "position": "bottom", "object 1": "<color + type>" },
      { "position": "top", "object 2": "<color + type>" },
      { "position": "left", "object 3": "<color + type>" }
    ]
  }
}

# 2+1右
{
  "target_structure": {
    "relationship": "stacked_and_separated_right",
    "placements": [
      { "position": "bottom", "object 1": "<color + type>" },
      { "position": "top", "object 2": "<color + type>" },
      { "position": "right", "object 3": "<color + type>" }
    ]
  }
}

# 左右分开
{
  "target_structure": {
    "relationship": "separate_horizontal",
    "placements": [
      {
        "position": "left",
        "object 1": "blue cube"
      },
      {
        "position": "middle",
        "object 2": "red block"
      },
      {
        "position": "right",
        "object 3": "green cube"
      }
    ]
  }
}

# 前后分开
{
  "target_structure": {
    "relationship": "separate_vertical",
    "placements": [
      {
        "position": "bottom",
        "object 1": "blue cube"
      },
      {
        "position": "middle",
        "object 2": "red cube"
      },
      {
        "position": "top",
        "object 3": "green cube"
      }
    ]
  }
}
```

