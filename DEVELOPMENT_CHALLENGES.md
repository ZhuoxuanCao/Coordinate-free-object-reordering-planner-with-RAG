# Replan RAG System - 开发挑战与解决方案

## 项目概述

基于Qwen3-4B-FP8模型的坐标无关对象重新排序规划器，使用RAG（检索增强生成）架构，具备分层系统提示词和复杂度感知的场景分类能力。

## 主要挑战与解决方案

### 🔴 挑战1: 中层替换的复杂逻辑实现

**问题描述:**
- 初始系统无法正确处理中层对象替换场景
- 模型生成错误的对象生命周期管理（将需要移除的对象放入缓冲区）
- 没有遵循"清除上层访问下层"的物理约束

**错误示例:**
```json
// ❌ 错误的中层替换计划
[
  {"action": "move_to_buffer", "object": "yellow cube"},  // 应该直接移除
  {"action": "move_to_position", "object": "green cube"}, // 没有先清除上层
  {"action": "move_from_buffer", "object": "yellow cube"} // 恢复不需要的对象
]
```

**解决方案:**
1. **场景细分类**: 创建 `stack_replacement_middle` 专门场景
2. **强化物理约束**: 明确"必须先清除上层才能访问中层"
3. **对象生命周期区分**:
   - 缓冲区（临时存储）: 目标中存在但位置错误的对象
   - 散布（永久移除）: 目标中不存在的对象

**成功输出:**
```json
// ✅ 正确的4步中层替换
[
  {"step": 1, "action": "move_to_buffer", "object": "red cube", "to": "B1"},
  {"step": 2, "action": "move_to_position", "object": "yellow cube", "to": "scattered"},
  {"step": 3, "action": "move_to_position", "object": "green cube", "to": "middle"},
  {"step": 4, "action": "move_from_buffer", "object": "red cube", "to": "top"}
]
```

### 🔴 挑战2: 简单顶层替换被过度复杂化

**问题描述:**
- 在优化中层替换后，简单的顶层替换反而出现问题
- 模型试图直接覆盖占用位置，违反基本物理约束
- 只生成1步而非必要的2步（移除→放置）

**错误示例:**
```json
// ❌ 错误的顶层替换（试图直接覆盖）
[
  {"action": "move_to_position", "object": "red cube", "to": {"type": "stack", "position": "top"}}
]
// 位置被yellow cube占用！
```

**解决方案:**
1. **创建独立的简单提示词**: `stack_replacement_top` 场景
2. **强调2步强制性**: 必须先清除再放置
3. **避免过度复杂化**: 顶层不需要缓冲区操作

**成功输出:**
```json
// ✅ 正确的2步顶层替换
[
  {"step": 1, "action": "move_to_position", "object": "yellow cube", "to": "scattered"},
  {"step": 2, "action": "move_to_position", "object": "red cube", "to": "top"}
]
```

### 🔴 挑战3: 底层替换的物理约束理解

**问题描述:**
- 模型完全忽略中层存在，试图跳过中层直接访问底层
- 没有理解"物理阻挡"概念 - 即使中层对象是正确的，仍然阻挡底层访问
- 生成不存在的动作名称（如 `move_from_position`）

**错误示例:**
```json
// ❌ 错误的底层替换（忽略中层阻挡）
[
  {"step": 1, "action": "move_to_buffer", "object": "red cube"},      // 只清除顶层
  {"step": 2, "action": "move_to_position", "object": "yellow cube"}, // ❌ 中层仍存在
  {"step": 3, "action": "move_from_position", "object": "blue cube"}  // ❌ 不存在的动作
]
```

**解决方案:**
1. **强化物理约束理解**: 明确"即使正确的对象也会阻挡访问"
2. **强制6步序列**: 提供完整的JSON示例模板
3. **动作名称验证**: 明确禁止不存在的动作

**正确输出:**
```json
// ✅ 正确的6步底层替换
[
  {"step": 1, "action": "move_to_buffer", "object": "red cube", "to": "B1"},
  {"step": 2, "action": "move_to_buffer", "object": "green cube", "to": "B2"},
  {"step": 3, "action": "move_to_position", "object": "yellow cube", "to": "scattered"},
  {"step": 4, "action": "move_to_position", "object": "blue cube", "to": "bottom"},
  {"step": 5, "action": "move_from_buffer", "object": "green cube", "to": "middle"},
  {"step": 6, "action": "move_from_buffer", "object": "red cube", "to": "top"}
]
```

### 🔴 挑战4: 全局提示词修改的副作用

**问题描述:**
- 为修复底层替换而修改全局基础提示词
- 导致已经工作的顶层和中层替换受到意外影响
- 出现功能交互干扰和回归问题

**解决方案:**
**采用完全独立的提示词架构:**

```python
# ✅ 安全的架构设计
基础提示词 (最小化)
├── JSON格式要求
└── 基本动作规范

每种类型独立提示词
├── top_only: 完整2步指导
├── middle_only: 完整4步指导
├── bottom_only: 完整6步指导
└── extension: 简单扩展指导
```

**优势:**
- **零交互影响**: 修改一种类型不影响其他
- **功能隔离**: 每种类型有完整的独立指导
- **易于维护**: 问题排查和修复范围明确

### 🔴 挑战5: 场景分类准确性

**问题描述:**
- 初始场景分类过于粗糙，无法区分不同复杂度的替换场景
- embedding相似度匹配不够精确
- 错误分类导致使用错误的处理逻辑

**解决方案:**
1. **细分场景类别**:
   ```python
   "stack_replacement_top"     → 简单2步直接替换
   "stack_replacement_middle"  → 中等4步清除-恢复
   "stack_replacement_bottom"  → 复杂6步完整重建
   "stack_replacement_multiple"→ 多层混合替换
   ```

2. **智能分类逻辑**:
   ```python
   def _analyze_replacement_complexity():
       # 检测具体哪些位置需要替换
       # 返回 top_only/middle_only/bottom_only/multiple
   ```

3. **强制分类回退**:
   ```python
   if replacement_type != "none" and max_similarity < 0.7:
       # 基于分析结果强制使用正确分类
   ```

## 核心架构设计

### 分层系统提示词架构

```
ReplanRAGSystem
├── 场景分类层
│   ├── embedding相似度匹配
│   ├── 复杂度分析
│   └── 强制分类回退
├── 规则检索层
│   ├── RAG语义检索
│   ├── 关键词过滤
│   └── 优先级排序
└── 提示词构建层
    ├── 基础提示词（最小化）
    ├── 独立特定提示词
    └── 规则内容注入
```

### 对象生命周期管理

```python
# 关键区分逻辑
📦 BUFFER (临时存储)
- 对象在目标结构中存在
- 当前位置错误，需要重新定位
- 使用 move_to_buffer → move_from_buffer

🗑️ SCATTERED (永久移除)
- 对象不在目标结构中
- 需要从堆栈中移除
- 使用 move_to_position → scattered
```

### 物理约束分层

```python
# 复杂度递增的约束
TOP_ONLY: 直接访问，2步替换
MIDDLE_ONLY: 需清除上层，4步替换
BOTTOM_ONLY: 需清除所有上层，6步替换
```

## 测试验证策略

### 分类测试用例

```python
# 顶层替换测试
current: [blue(bottom), green(middle), yellow(top)]
target:  [blue(bottom), green(middle), red(top)]
expect:  stack_replacement_top + 2步

# 中层替换测试
current: [blue(bottom), yellow(middle), red(top)]
target:  [blue(bottom), green(middle), red(top)]
expect:  stack_replacement_middle + 4步

# 底层替换测试
current: [yellow(bottom), green(middle), red(top)]
target:  [blue(bottom), green(middle), red(top)]
expect:  stack_replacement_bottom + 6步
```

### 验证检查点

1. **场景分类准确性**: 正确识别替换类型
2. **动作序列正确性**: 步骤数量和顺序
3. **物理约束遵循**: 清除顺序和访问限制
4. **对象生命周期**: buffer vs scattered 使用
5. **最终状态一致性**: 与目标规范匹配

## 经验总结

### ✅ 成功实践

1. **分层架构设计**: 场景分类 → 规则检索 → 提示词构建
2. **功能完全隔离**: 避免全局修改影响其他功能
3. **复杂度感知处理**: 根据替换复杂度提供不同指导
4. **强制性示例**: 提供具体JSON格式模板
5. **物理约束强化**: 明确阻挡关系和访问顺序

### ❌ 避免的陷阱

1. **全局提示词修改**: 容易产生意外交互影响
2. **过度复杂化简单场景**: 顶层替换不需要复杂逻辑
3. **忽略物理约束**: 必须理解层级阻挡关系
4. **场景分类粗糙**: 需要精确区分不同复杂度
5. **对象生命周期混淆**: buffer和scattered的正确使用

### 🔧 调试策略

1. **分步验证**: 场景分类 → 规则检索 → 提示词 → 生成结果
2. **独立测试**: 每种替换类型单独验证
3. **回归测试**: 修改后确保其他功能不受影响
4. **日志分析**: 输出详细的分类和检索信息
5. **模板对比**: 对比生成结果与预期模板

## 未来扩展方向

### 支持更多关系类型
- `separated_left_right`, `separated_front_back`
- `pyramid`, `stacked_and_separated_*`
- 非堆栈类型的替换逻辑

### 优化策略
- 更精确的embedding模型
- 动态规则权重调整
- 多轮对话式规划修正

### 性能提升
- 规则缓存机制
- 并行处理优化
- 提示词压缩技术

---

**文档创建时间**: 2025-01-17
**当前系统状态**: 顶层、中层替换已验证成功，底层替换优化中
**测试环境**: Qwen3-4B-FP8, 20规则知识库, 分层提示词架构