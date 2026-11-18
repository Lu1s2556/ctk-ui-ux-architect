<div align="center">

<img src="./assets/banner.jpg" alt="CTk UI/UX Architect Banner" width="100%" />

# ⚡ CTk UI/UX Architect

**Enterprise-Grade Design System, Automated Performance Auditor & Architecture Skill for CustomTkinter**

*Transform Python + CustomTkinter desktop apps into 60 FPS, zero-flicker, thread-safe interfaces.*

<p>
  <a href="#-whats-new-in-v110"><img src="[https://img.shields.io/badge/Release-v1.1.0-10B981?style=for-the-badge&logo=semver&logoColor=white](https://img.shields.io/badge/Release-v1.1.0-10B981?style=for-the-badge&logo=semver&logoColor=white)" alt="Release v1.1.0" /></a>
  <a href="[https://www.python.org/](https://www.python.org/)"><img src="[https://img.shields.io/badge/Python-3.8.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white](https://img.shields.io/badge/Python-3.8.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)" alt="Python 3.8.10+" /></a>
  <a href="[https://github.com/TomSchimansky/CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)"><img src="[https://img.shields.io/badge/CustomTkinter-5.2%2B-00B4D8?style=for-the-badge&logo=windows-terminal&logoColor=white](https://img.shields.io/badge/CustomTkinter-5.2%2B-00B4D8?style=for-the-badge&logo=windows-terminal&logoColor=white)" alt="CustomTkinter" /></a>
  <a href="#-installation"><img src="[https://img.shields.io/badge/Antigravity-Ready-10B981?style=for-the-badge&logo=google-gemini&logoColor=white](https://img.shields.io/badge/Antigravity-Ready-10B981?style=for-the-badge&logo=google-gemini&logoColor=white)" alt="Antigravity Ready" /></a>
  <a href="#-installation"><img src="[https://img.shields.io/badge/Claude_Code-Plugin-D97757?style=for-the-badge&logo=anthropic&logoColor=white](https://img.shields.io/badge/Claude_Code-Plugin-D97757?style=for-the-badge&logo=anthropic&logoColor=white)" alt="Claude Code" /></a>
  <a href="#-installation"><img src="[https://img.shields.io/badge/OpenAI_Codex-Skill-412991?style=for-the-badge&logo=openai&logoColor=white](https://img.shields.io/badge/OpenAI_Codex-Skill-412991?style=for-the-badge&logo=openai&logoColor=white)" alt="OpenAI Codex" /></a>
  <a href="#-license"><img src="[https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)" alt="MIT License" /></a>
</p>

<p>
  <a href="#-why-ctk-uiux-architect">Why This Skill?</a> •
  <a href="#-whats-new-in-v110">What's New (v1.1.0)</a> •
  <a href="#-core-pillars">Core Pillars</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-smart-ui-inspector">Smart Inspector</a> •
  <a href="#-agent-workflows">Workflows</a> •
  <a href="#-architecture--knowledge-base">Architecture</a>
</p>

</div>

---

## 🎯 Why CTk UI/UX Architect?

Building complex desktop software in Python with CustomTkinter often hits hard technical ceilings: sluggish CPU-bound rendering when widget counts climb, frozen windows during database/API calls, layout jitter on form validation, and broken contrast when toggling Dark/Light modes.

**CTk UI/UX Architect** equips your AI coding agent with deterministic UI engineering rules, production-tested MVC templates, and a **zero-config static & runtime inspector** that catches performance and visual regressions before shipping.

| Engineering Challenge | Default CustomTkinter App | With **CTk UI/UX Architect** |
| :--- | :--- | :--- |
| **Canvas Rendering Load** | Unbounded widget trees (`400+` widgets) causing laggy resizing | **Strict `< 200` alive widget budget** enforced per view |
| **Large Data Grids** | Frame-based rows freeze UI past `~150` records | **`CTkThemedTreeview`** renders **50 to 50,000+ rows** smoothly |
| **Background I/O & APIs** | Direct thread updates crash Tk or freeze `mainloop` | **`UIQueueBatcher`** batches **25 UI events/cycle** safely |
| **Form Validation UX** | Dynamic error labels shift widgets and jump windows | **`ValidatedEntry`** reserves fixed-height slots (**0px shift**) |
| **Theme Consistency** | Hardcoded hex strings break Light/Dark transitions | **3-Layer Surface Elevation** with adaptive `(light, dark)` tokens |
| **Quality Assurance** | Manual visual inspection across resolutions | **Automated CLI & Runtime Inspector** with JSON & traffic-light reports |

---

## 🆕 What's New in v1.1.0

### 🚀 Features & Enhancements
- **Zero-Config Target Discovery**: Automatically scans project trees up to 4 directory levels deep (supporting `src/`, `app/`, or root structures) without requiring `--target`.
- **Interactive Multi-Target Menu**: Presents an intuitive prompt to choose the target application when multiple CustomTkinter windows exist in a repository.
- **One-Line In-Code Audit Hook**: Integrated `from ctk_inspector import audit; audit(app)` to evaluate UI metrics dynamically without freezing the event loop.
- **Traffic-Light Status Summary**: Formatted terminal output with clean visual indicators (`🟢 PASSED_PERFECT`, `🟡 PASSED_WITH_WARNINGS`, `🔴 FAILED_CRITICAL`).
- **Comprehensive Documentation**: Complete English `README.md` with multi-agent installation guides (Antigravity, Claude Code, OpenAI Codex).

### 🛠️ Maintenance & Compatibility
- Added automated directory pruning (`.git`, `venv`, `build`, etc.) during discovery for sub-second execution.
- Added MIT license declaration and cleaned repository tracking via `.gitignore`.

---

## 🧩 Core Pillars

### 1. 🚦 Strict Canvas Budgeting (`< 200` Widgets)
Eliminates Tcl/Tk CPU rendering bottlenecks by auditing live widget trees in real time, flagging bloated containers, and enforcing view virtualization or lazy mounting.

### 2. 📊 Hybrid High-Volume Tables (`CTkThemedTreeview`)
Combines the native C-level speed of `ttk.Treeview` (`clam` theme engine + automatic DPI scaling) inside a seamless CustomTkinter surface container—handling **50 to 50,000 rows** without frame drops.

### 3. ⚙️ Thread-Safe Concurrency (`UIQueueBatcher`)
Decouples heavy network requests, file I/O, and SQLite/PostgreSQL queries into worker threads while draining up to **25 UI mutations per `mainloop` tick** to guarantee a responsive interface.

### 4. 🎯 Zero-Layout-Shift Components (`ux_components.py`)
Drop-in, production-ready building blocks engineered with concentric corner radii and deterministic spacing:
- **`ValidatedEntry`**: Inline validation with pre-allocated error slots so forms never jump.
- **`MetricCard`**: High-contrast KPI cards with semantic trend indicators.
- **`ToastNotification`**: Non-blocking, auto-dismissing overlay alerts.

### 5. 🎨 3-Layer Adaptive Elevation System
Structured semantic color tokens defined as `(light_mode, dark_mode)` tuples across three visual depth tiers:
- **Layer 0 (`Canvas Base`):** Primary window backdrop.
- **Layer 1 (`Elevated Card`):** Content panels, sidebars, and data containers.
- **Layer 2 (`Interactive Surface`):** Inputs, modals, hover states, and active controls.

---

## 🚀 Installation

Install **CTk UI/UX Architect** across your favorite AI agent CLI in seconds:

### 1. Google Antigravity *(Recommended)*

```bash
agy plugin install https://github.com/Lu1s2556/ctk-ui-ux-architect
```

<details>
<summary><b>Manual local clone for Antigravity (Windows / Linux / macOS)</b></summary>

```bash
# Windows (PowerShell)
git clone https://github.com/Lu1s2556/ctk-ui-ux-architect.git "$HOME\.gemini\config\plugins\ctk-ui-ux-architect"

# Linux / macOS
git clone https://github.com/Lu1s2556/ctk-ui-ux-architect.git ~/.gemini/config/plugins/ctk-ui-ux-architect
```
</details>

### 2. Claude Code

Run inside your interactive Claude Code session:

```text
/plugin marketplace add Lu1s2556/ctk-ui-ux-architect
/plugin install ctk-ui-ux-architect@ctk-ui-ux-architect
```

### 3. OpenAI Codex

Add directly via the Codex CLI:

```bash
codex plugin marketplace add Lu1s2556/ctk-ui-ux-architect
codex plugin add ctk-ui-ux-architect@ctk-ui-ux-architect
```

### 4. Per-Project Git Submodule

Embed the skill directly into a team repository:

```bash
git submodule add https://github.com/Lu1s2556/ctk-ui-ux-architect.git .agent/skills/ctk-ui-ux-architect
```

---

## 🔍 Smart UI Inspector (`ctk_inspector.py`)

Audit any CustomTkinter codebase with **zero manual configuration**. The inspector recursively scans your project (up to 4 levels deep across `src/`, `app/`, etc.), mounts views safely, inspects geometry & color tokens, and outputs actionable diagnostics.

### Option A: Zero-Config CLI Auto-Discovery

Run from your project root:

```bash
python .agent/skills/ctk-ui-ux-architect/scripts/ctk_inspector.py
```

- **Single app detected:** Audits immediately and outputs the report.
- **Multiple entrypoints detected:** Launches an interactive selector:
  ```text
  🔍 CustomTkinter applications detected in project:
    [1] src/client/main.py
    [2] src/admin/dashboard.py
  👉 Choose target [1-2] (Enter for [1]):
  ```
- **Direct targeting:** Pass `--target path/to/app.py` for CI/CD pipelines or scripts.

### Option B: One-Line In-Code Runtime Audit

Inspect your live widget tree asynchronously without blocking `mainloop()`:

```python
import customtkinter as ctk
from ctk_inspector import audit

app = ctk.CTk()
# ... build your views & widgets ...

audit(app)  # 🔍 Traverses widget tree in the background
app.mainloop()
```

### 🚦 Visual Traffic-Light Report & JSON Telemetry

Every audit prints a crisp terminal verdict (`🟢 PASSED_PERFECT`, `🟡 PASSED_WITH_WARNINGS`, `🔴 FAILED_CRITICAL`) and exports full diagnostics to `./ui_audit/audit_report.json`:

```text
================= 🔍 CTK UI AUDIT =================
Verdict: 🟢 PASSED_PERFECT
Total alive widgets: 34 (Canvas Limit: 200)
Collapsed containers: 0
Clipped/truncated texts: 0
Hardcoded non-adaptive colors: 0
Report saved to: ./ui_audit/audit_report.json
===================================================
```

---

## 🤖 Agent Workflows

This skill ships with two turnkey agentic workflows under `.agent/workflows/` so your AI assistant can audit and refactor legacy interfaces autonomously:

| Workflow | Purpose | What the Agent Executes |
| :--- | :--- | :--- |
| **`auditar-ui.md`** | **Full Performance & Visual Audit** | Runs `ctk_inspector.py`, parses `audit_report.json`, pinpoints widget bloat, clipped labels, and non-adaptive hex colors, and delivers a prioritized fix plan. |
| **`mejorar-ui.md`** | **Step-by-Step UI Modernization** | Refactors monolithic scripts into `base_app_mvc.py`, migrates heavy lists to `CTkThemedTreeview`, wraps async tasks in `UIQueueBatcher`, and applies 3-layer elevation tokens. |

---

## 🏗️ Architecture & Knowledge Base

```text
.agent/
├── workflows/
│   ├── auditar-ui.md                        # Automated performance & visual audit workflow
│   └── mejorar-ui.md                        # Step-by-step UI refactoring & modernization
└── skills/
    └── ctk-ui-ux-architect/
        ├── SKILL.md                         # Core architectural rules & fast decision tree
        ├── scripts/
        │   └── ctk_inspector.py             # Zero-config CLI & runtime UI auditor
        ├── references/
        │   ├── 01-design-tokens-and-surfaces.md      # 3-layer elevation & concentric radii
        │   ├── 02-layout-and-navigation-patterns.md  # Responsive grids, sidebars & routing
        │   ├── 03-performance-and-concurrency.md     # <200 widget budget & UIQueueBatcher
        │   ├── 04-hybrid-treeview-and-tables.md      # High-volume ttk.Treeview styling
        │   └── 05-python38-memory-and-packaging.md   # Legacy OS compatibility & PyInstaller
        └── templates/
            ├── base_app_mvc.py              # Production-ready MVC desktop foundation
            └── ux_components.py             # MetricCard, ToastNotification, ValidatedEntry
```

### 📚 Included Reference Guides & Templates

- **`01-design-tokens-and-surfaces.md`** — Contrast ratios, typography hierarchy, concentric radius math ($R_{outer} = R_{inner} + Padding$), and adaptive color pairs.
- **`02-layout-and-navigation-patterns.md`** — Grid weight discipline, collapsible navigation rails, and multi-view swapping without widget leaks.
- **`03-performance-and-concurrency.md`** — Thread-safe `queue.Queue` batching patterns and main-thread protection.
- **`04-hybrid-treeview-and-tables.md`** — High-DPI scaling, alternating row striping, sorting, and virtualized data loading for 50k+ rows.
- **`05-python38-memory-and-packaging.md`** — Memory footprint optimization for Python `3.8.10+` and clean single-binary packaging.

---

## 🤝 Contributing & License

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request at [Lu1s2556/ctk-ui-ux-architect](https://github.com/Lu1s2556/ctk-ui-ux-architect).

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">
  <sub>Built with precision for Python desktop engineers & AI-assisted workflows.</sub>
</div>