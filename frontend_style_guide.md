# Django 企业管理系统前端美化规范文档

## 文档说明

本规范文档基于项目现有代码及 Bootstrap 框架，旨在为企业管理系统提供统一、专业、简洁的前端视觉规范。所有规范均与项目已集成的 Bootstrap 框架兼容，不影响原有功能逻辑。

---

## 1. 色彩系统 (Colors)

### 1.1 品牌色系

| 颜色名称 | 色值 (HEX) | 色值 (RGB) | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **主色 (Primary)** | `#2563eb` | rgb(37, 99, 235) | `bg-blue-600`, `text-blue-600` | 主要按钮、导航栏、重点强调 |
| **主色浅 (Primary Light)** | `#3b82f6` | rgb(59, 130, 246) | `bg-blue-500`, `text-blue-500` | 悬浮状态、次要按钮 |
| **主色深 (Primary Dark)** | `#1d4ed8` | rgb(29, 78, 216) | `bg-blue-700`, `text-blue-700` | 选中状态、强调边框 |

### 1.2 功能色系

| 颜色名称 | 色值 (HEX) | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- |
| **成功色 (Success)** | `#10b981` | `bg-emerald-500`, `text-emerald-500` | 成功提示、操作成功状态 |
| **警告色 (Warning)** | `#f59e0b` | `bg-amber-500`, `text-amber-500` | 警告提示、待处理状态 |
| **危险色 (Danger)** | `#ef4444` | `bg-red-500`, `text-red-500` | 删除操作、错误提示、危险状态 |
| **信息色 (Info)** | `#06b6d4` | `bg-cyan-500`, `text-cyan-500` | 信息提示、帮助文本 |

### 1.3 背景色系

| 颜色名称 | 色值 (HEX) | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- |
| **页面背景** | `#f8fafc` | `bg-slate-50` | 全局页面背景 |
| **卡片背景** | `#ffffff` | `bg-white` | 卡片、面板背景 |
| **卡片悬浮背景** | `#f1f5f9` | `bg-slate-100` | 卡片悬浮状态 |
| **表单背景** | `#ffffff` | `bg-white` | 表单输入框背景 |

### 1.4 文字色系

| 文字类型 | 色值 (HEX) | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- |
| **标题文字** | `#1e293b` | `text-slate-800` | 页面标题、卡片标题 |
| **正文文字** | `#334155` | `text-slate-600` | 正文内容、表格数据 |
| **次要文字** | `#64748b` | `text-slate-500` | 辅助说明、次要信息 |
| **占位文字** | `#94a3b8` | `text-slate-400` | 输入框占位符、禁用状态 |
| **链接文字** | `#2563eb` | `text-blue-600` | 超链接、可点击文本 |

### 1.5 边框色系

| 边框类型 | 色值 (HEX) | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- |
| **表单边框** | `#e2e8f0` | `border-slate-200` | 输入框、选择框边框 |
| **表格边框** | `#e2e8f0` | `border-slate-200` | 表格单元格边框 |
| **卡片边框** | `#e2e8f0` | `border-slate-200` | 卡片容器边框 |
| **分割线** | `#e2e8f0` | `border-slate-200` | 模块分隔线 |
| **聚焦边框** | `#2563eb` | `border-blue-600` | 输入框聚焦状态 |

---

## 2. 排版系统 (Typography)

### 2.1 标题规范

| 标题层级 | 字号 | 行高 | 字重 | 颜色 | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **页面大标题** | 24px | 1.3 | 600 | `#1e293b` | `text-2xl font-semibold text-slate-800` | 页面顶部主标题 |
| **二级标题** | 20px | 1.3 | 600 | `#1e293b` | `text-xl font-semibold text-slate-800` | 模块标题、卡片组标题 |
| **三级标题** | 18px | 1.3 | 500 | `#334155` | `text-lg font-medium text-slate-600` | 卡片标题、区域标题 |
| **卡片标题** | 16px | 1.4 | 500 | `#334155` | `text-base font-medium text-slate-600` | 数据卡片标题 |

### 2.2 正文规范

| 文字类型 | 字号 | 行高 | 字重 | 颜色 | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **正文** | 14px | 1.5 | 400 | `#334155` | `text-sm text-slate-600` | 主要内容、表格数据 |
| **描述文字** | 14px | 1.5 | 400 | `#64748b` | `text-sm text-slate-500` | 辅助说明、提示文字 |
| **辅助小字** | 12px | 1.4 | 400 | `#94a3b8` | `text-xs text-slate-400` | 时间戳、状态标签 |
| **按钮文字** | 14px | 1.4 | 500 | 随按钮类型 | `text-sm font-medium` | 按钮文本 |

---

## 3. 组件质感 (Components)

### 3.1 圆角规范

| 圆角类型 | 数值 | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- |
| **大圆角** | 12px | `rounded-xl` | 卡片容器、模态框 |
| **中圆角** | 8px | `rounded-lg` | 按钮、输入框、图片 |
| **小圆角** | 4px | `rounded-md` | 标签、徽章、小按钮 |

### 3.2 阴影规范

| 阴影类型 | CSS 值 | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- |
| **卡片阴影** | `0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)` | `shadow-sm` | 默认卡片、面板 |
| **悬浮阴影** | `0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)` | `shadow-md` | 卡片悬浮、下拉菜单 |
| **按钮阴影** | `0 1px 2px 0 rgb(0 0 0 / 0.05)` | `shadow-sm` | 按钮默认状态 |
| **按钮悬浮阴影** | `0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)` | `shadow-md` | 按钮悬浮状态 |

### 3.3 边框规范

| 边框类型 | 厚度 | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- |
| **表单边框** | 1px | `border border-slate-200` | 输入框、选择框 |
| **表格边框** | 1px | `border border-slate-200` | 表格单元格 |
| **卡片边框** | 1px | `border border-slate-200` | 卡片容器 |
| **分割线** | 1px | `border-t border-slate-200` | 模块分隔线 |

### 3.4 按钮规范

#### 按钮样式表

| 按钮类型 | 背景色 | 文字色 | 边框 | 悬浮状态 | Tailwind CSS |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **默认按钮** | `#f1f5f9` | `#334155` | 无边框 | 背景 `#e2e8f0` | `bg-slate-100 text-slate-600 hover:bg-slate-200` |
| **主要按钮** | `#2563eb` | `#ffffff` | 无边框 | 背景 `#1d4ed8` | `bg-blue-600 text-white hover:bg-blue-700` |
| **成功按钮** | `#10b981` | `#ffffff` | 无边框 | 背景 `#059669` | `bg-emerald-500 text-white hover:bg-emerald-600` |
| **警告按钮** | `#f59e0b` | `#ffffff` | 无边框 | 背景 `#d97706` | `bg-amber-500 text-white hover:bg-amber-600` |
| **危险按钮** | `#ef4444` | `#ffffff` | 无边框 | 背景 `#dc2626` | `bg-red-500 text-white hover:bg-red-600` |

#### 按钮尺寸

| 尺寸 | 高度 | 内边距 | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **默认按钮** | 36px | px-4 | `h-9 px-4` | 常规操作按钮 |
| **小按钮** | 28px | px-3 | `h-7 px-3` | 表格操作、次要操作 |
| **大按钮** | 44px | px-6 | `h-11 px-6` | 主要操作、表单提交 |

---

## 4. 布局间距 (Spacing)

### 4.1 页面边距

| 间距类型 | 数值 | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- |
| **页面外边距** | 24px | `mx-6 my-6` | 页面内容与浏览器边缘 |
| **容器内边距** | 16px | `p-4` | 容器内部留白 |
| **卡片内边距** | 20px | `p-5` | 卡片内容区域 |

### 4.2 模块间距

| 间距类型 | 数值 | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- |
| **模块间距** | 24px | `mb-6` | 模块之间的垂直距离 |
| **区域间距** | 16px | `mb-4` | 同模块内区域之间 |
| **元素间隙** | 8px | `gap-2` | 按钮组、标签组 |
| **卡片间距** | 16px | `gap-4` | 卡片网格布局 |

### 4.3 表单间距

| 间距类型 | 数值 | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- |
| **标签与输入框间距** | 8px | `mb-2` | 表单标签下方 |
| **表单行间距** | 16px | `mb-4` | 表单字段之间 |
| **按钮组间距** | 8px | `gap-2` | 多个按钮之间 |
| **表单底部间距** | 24px | `mt-6` | 表单内容与按钮之间 |

### 4.4 表格间距

| 间距类型 | 数值 | Tailwind CSS | 应用场景 |
| :--- | :--- | :--- | :--- |
| **单元格内边距** | 12px | `px-3 py-2` | 表格单元格 |
| **表头背景** | `#f8fafc` | `bg-slate-50` | 表格表头行 |
| **奇偶行区分** | - | `striped` | 表格行交替背景 |

---

## 附录：Bootstrap 兼容性说明

### 类名映射表

| Bootstrap 类 | Tailwind CSS 等效类 | 说明 |
| :--- | :--- | :--- |
| `btn` | `px-4 py-2 rounded-lg font-medium shadow-sm` | 基础按钮样式 |
| `btn-primary` | `bg-blue-600 text-white hover:bg-blue-700` | 主要按钮 |
| `btn-success` | `bg-emerald-500 text-white hover:bg-emerald-600` | 成功按钮 |
| `btn-warning` | `bg-amber-500 text-white hover:bg-amber-600` | 警告按钮 |
| `btn-danger` | `bg-red-500 text-white hover:bg-red-600` | 危险按钮 |
| `panel` | `bg-white border border-slate-200 rounded-xl shadow-sm` | 面板容器 |
| `panel-heading` | `px-5 py-4 border-b border-slate-200` | 面板头部 |
| `panel-body` | `p-5` | 面板内容 |
| `form-control` | `w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent` | 表单控件 |
| `table` | `w-full text-sm` | 表格基础样式 |
| `table-striped` | `striped` | 条纹表格 |
| `container` | `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8` | 响应式容器 |

### 使用原则

1. **优先使用规范类名**：在新开发页面中优先使用本规范定义的 Tailwind CSS 类名
2. **渐进式美化**：对现有页面可逐步替换为规范类名，无需一次性改造
3. **保持兼容性**：保留 Bootstrap 类名支持，确保原有代码正常运行
4. **统一命名**：组件类名遵循 `[组件类型]-[状态]-[尺寸]` 命名规范

---

## 版本记录

| 版本 | 日期 | 更新内容 |
| :--- | :--- | :--- |
| v1.0 | 2026-04-29 | 初始版本，包含色彩、排版、组件、布局四大模块 |
