---
name: subaru-skills public documentation
description: 白色阅读面、灰蓝导航与可检查案例组成的公开文档阅读桌。
colors:
  blue: "#175bc2"
  ink: "#183040"
  muted: "#526574"
  line: "#d5e0e8"
  rail: "#f0f4f7"
  paper: "#fff"
typography:
  headline:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans CJK SC", sans-serif'
    fontSize: "clamp(30px, 3.5vw, 46px)"
    fontWeight: 700
    lineHeight: 1.35
    letterSpacing: "-0.025em"
  title:
    fontSize: "27px"
    fontWeight: 700
    lineHeight: 1.4
  subheading:
    fontSize: "21px"
    fontWeight: 700
    lineHeight: 1.5
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans CJK SC", sans-serif'
    fontSize: "17px"
    lineHeight: 1.8
  lead:
    fontSize: "20px"
    lineHeight: 1.75
  label:
    fontSize: "15px"
  caption:
    fontSize: "14px"
  code:
    fontFamily: "ui-monospace, SFMono-Regular, Consolas, monospace"
    fontSize: "14px"
spacing:
  compact: "12px"
  text: "16px"
  panel: "20px"
  section: "24px"
  heading: "28px"
  major: "48px"
components:
  action-primary:
    backgroundColor: "{colors.blue}"
    textColor: "{colors.paper}"
    rounded: "5px"
    padding: "10px 18px"
  copy-button:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.blue}"
    rounded: "4px"
    padding: "5px 10px"
  navigation-item:
    textColor: "{colors.ink}"
    padding: "9px 10px"
  navigation-current:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.blue}"
    padding: "9px 10px"
  command-panel:
    backgroundColor: "{colors.rail}"
    padding: "20px"
---

# Design System: subaru-skills public documentation

## Overview

**Creative North Star: "The Reading Desk"**

以“阅读桌”为共同隐喻：白色正文供连续阅读，灰蓝导航轨道保持位置感，蓝色链接提供下一步。页面密度服务文档阅读与案例检查，中文优先，英文沿用同一套结构。

本系统仅覆盖公开文档网站，不覆盖 skill 风格、示例演示文稿或仓库工具。原生系统字体是已确认的 Read 模式选择；页面不加载外部字体。

**Key Characteristics:**
- 白色阅读面与灰蓝导航轨道。
- 蓝色承担链接、主要动作与键盘焦点。
- 正文限制行长，标题依靠字号与留白建立层级。
- 真实演示文稿预览配说明和可检查的下载入口。

## Colors

单一蓝色强调与偏灰蓝的中性色承担阅读、定位与行动职责；前置 token 是颜色的规范来源，名称与网站 CSS 变量一致。

### Primary

- **Link Blue (`blue`)**：正文链接、主要动作、当前导航和键盘焦点。

### Neutral

- **Slate Ink (`ink`)**：正文、标题与默认导航文字。
- **Quiet Slate (`muted`)**：图注、辅助说明和页脚。
- **Desk Edge (`line`)**：页眉页脚、表格、案例和预览的细边线。
- **Slate Rail (`rail`)**：导航轨道、命令、引用和表头。
- **Reading Paper (`paper`)**：页面正文、当前导航及复制按钮的表面。

**The Reading Desk Rule.** 正文保持白色阅读面；灰蓝底色用于导航、代码、引用和表头。

## Typography

**Display / Body Font:** 原生系统无衬线字体栈，共享中文后备字体。
**Label/Mono Font:** 命令与代码使用系统等宽字体栈。

阅读节奏来自行高、行长与间距。没有独立的展示字体角色，也不依赖远端字体加载。

### Hierarchy

- **Headline**：页面一级标题使用响应式字号、紧字距和均衡换行。
- **Title**：正文二级标题；章节前留大间距，窄屏字号降至（24px）。
- **Subheading**：三级标题；比正文更强而不成为新的展示层。
- **Body**：正文最大行长（70ch）；窄屏降至（16px），行高保持（1.8）。
- **Lead**：开头重点说明；窄屏降至（18px），行高保持（1.75）。
- **Label / Caption**：导航、表格与辅助说明以较小字号区别职责，不使用全大写标签。
- **Code**：保留命令的等宽结构，并允许长内容换行。

**The Read Mode Rule.** 网站标题和正文共享系统字体栈；等宽字体仅用于命令和代码。

## Layout

宽屏采用两列阅读桌：页面容器最大宽度（1440px），导航轨道宽（230px），正文列可收缩；主内容最大宽度（1080px）。导航贴住视口顶部（20px），保持文档位置感。页眉横向分布品牌与语言、仓库入口。

正文宽屏内边距为（48px clamp(24px, 5vw, 80px) 32px）。段落使用（18px）下间距，二级标题使用（48px）上间距；面板和动作组沿用紧凑的局部节奏，而不是统一卡片网格。

在（760px）及以下，页面变为单列，导航不再 sticky，改为可换行的横向链接，正文内边距为（30px 20px）。命令块为复制控件留出上方空间，表格在自己的横向滚动容器中保持列可读。动作组可换行。

## Elevation & Depth

当前实现没有盒阴影。辅助底色、细分隔线和真实预览的边框表达结构；不存在浮动卡片层级或玻璃效果。

**The Flat Surface Rule.** 用底色、细边线和间距区分内容，不给文档容器添加悬浮阴影。

## Shapes

阅读面、导航、命令与表格采用直角结构。小圆角仅出现在主要动作与复制按钮，分别按组件 token 定义；不将它们扩大成通用卡片圆角。分隔与预览边框保持（1px）。

## Components

### Buttons

主要动作是实心蓝色的链接，白字、紧凑圆角；悬停加深背景。复制按钮使用白面、蓝字和细边线，悬停时边线变蓝。键盘焦点为蓝色（3px）轮廓，外偏移（5px）。复制反馈分别为“已复制”或选择文本后的“请复制选中文本”，不依赖颜色单独传达状态。

仅在用户未要求减少动画时，主要动作使用背景色过渡（0.16s ease-out），页面允许平滑滚动。

### Navigation

灰蓝轨道内的链接默认使用正文色，无下划线；当前页以白色底、蓝字和粗体标记，并保留 `aria-current="page"`。移动端降低链接字号（13px），缩紧内边距（6px 9px），保留换行。正文链接则维持下划线，悬停加粗下划线。

### Command Panels

灰蓝直角容器托住等宽命令与右上角复制按钮；内容允许换行，宽屏为按钮保留右侧空间。JavaScript 缺失时仍可手动选中复制。

### Tables

表格使用灰蓝表头、底部分隔线、左对齐和 tabular numbers；列内容以阅读为主。

### Actual Deck Previews

实际导出幻灯片的（16:9）预览与说明组成可检查的材料。预览保持比例、细边框与自然高度；案例页限制到（720px）宽。图注说明来源，案例动作连接下载、逐页总览和记录。示例幻灯片自身的颜色与字体不是网站 token。

## Do's and Don'ts

### Do:

- **Do** 沿用白色正文、灰蓝辅助面和蓝色链接的角色分配。
- **Do** 为实际预览保留宽高、替代文本、图注与检查产物的入口。
- **Do** 保留键盘焦点、跳到正文入口以及无 JavaScript 时仍可阅读和手动复制的命令。
- **Do** 在窄屏将导航移入正常文档流，并让表格在自己的容器内滚动。

### Don't:

- **Don't** 把本站视觉规则扩展到演示文稿内页或 skill 风格库。
- **Don't** 用装饰性图片代替实际案例预览。
- **Don't** 给文档容器增加目前不存在的阴影、渐变或大面积强调色。
- **Don't** 把未验证的微小字号或一次性浏览器装饰推广为公共组件规范。
