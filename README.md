# CTk UI/UX Architect

A high-performance design system, performance auditing toolkit, and architecture skill for desktop applications built with **CustomTkinter (CTk)** and **Python 3.8.10+**.

Enforces CPU canvas budget limits, thread-safe asynchronous concurrency via queue batching, 3-level surface elevation, concentric corner radii, and zero-layout-shift UI components.

---

## Features

- **Strict Canvas Budgeting:** Enforces a hard threshold of under 200 alive widgets per view to eliminate CPU rendering bottlenecks.
- **Hybrid High-Volume Tables (`CTkThemedTreeview`):** Renders between 50 and 50,000 rows smoothly using a customized `ttk.Treeview` wrapped in a CTk frame with clam theming and DPI-aware scaling.
- **Thread-Safe Concurrency (`UIQueueBatcher`):** Offloads long-running I/O or database queries to daemon threads while batching UI updates (up to 25 items per cycle) to protect the Tk main loop.
- **Zero Layout Shift Inputs (`ValidatedEntry`):** Fixed-height error labels prevent UI jumping during validation.
- **3-Layer Adaptive Elevation:** Semantic color tokens using `(light, dark)` tuples ensuring proper contrast across modes.
- **Automated Geometry & Visual Inspector (`ctk_inspector.py`):** Traverses widget trees, identifies collapsed containers, detects clipped text labels, checks canvas loads, and exports structured reports with multimodal screenshots.

---

## Architecture Overview

```
.agent/
├── workflows/
│   ├── auditar-ui.md                 # Visual inspection and performance audit
│   └── mejorar-ui.md                 # Incremental UI modernization and refactoring
└── skills/
    └── ctk-ui-ux-architect/
        ├── SKILL.md                  # Core rules and fast decision tree
        ├── scripts/
        │   └── ctk_inspector.py      # Automated CLI widget inspector
        ├── references/
        │   ├── 01-design-tokens-and-surfaces.md
        │   ├── 02-layout-and-navigation-patterns.md
        │   ├── 03-performance-and-concurrency.md
        │   ├── 04-hybrid-treeview-and-tables.md
        │   └── 05-python38-memory-and-packaging.md
        └── templates/
            ├── base_app_mvc.py       # Production-ready MVC foundation
            └── ux_components.py      # MetricCard, ToastNotification, ValidatedEntry
```

---

## Installation

### 1. Google Antigravity

Install directly into your workspace or global environment:

```bash
agy plugin install https://github.com/Lu1s2556/ctk-ui-ux-architect
```

Or clone into your local configuration directory:

```bash
# Windows (PowerShell)
git clone https://github.com/Lu1s2556/ctk-ui-ux-architect.git "$HOME\.gemini\config\plugins\ctk-ui-ux-architect"

# Linux / macOS
git clone https://github.com/Lu1s2556/ctk-ui-ux-architect.git ~/.gemini/config/plugins/ctk-ui-ux-architect
```

---

### 2. Claude Code

Run inside your interactive session:

```text
/plugin marketplace add Lu1s2556/ctk-ui-ux-architect
/plugin install ctk-ui-ux-architect@ctk-ui-ux-architect
```

---

### 3. OpenAI Codex

Add using the Codex CLI:

```bash
codex plugin marketplace add Lu1s2556/ctk-ui-ux-architect
codex plugin add ctk-ui-ux-architect@ctk-ui-ux-architect
```

---

### 4. Per-Project Integration

To embed the skill directly into a specific repository:

```bash
git submodule add https://github.com/Lu1s2556/ctk-ui-ux-architect.git .agent/skills/ctk-ui-ux-architect
```

---

## Running the Automated UI Inspector

You can inspect existing CustomTkinter applications for geometry defects, color inconsistencies, and canvas overloads:

```bash
python .agent/skills/ctk-ui-ux-architect/scripts/ctk_inspector.py --target path/to/app.py --class MainApp --output-dir ./ui_audit
```

The tool produces:
- `audit_report.json`: Contains live widget counts, canvas load metrics, collapsed frame warnings, and color audits.
- Multimodal snapshots in Light mode, Dark mode, and compact window sizes (requires display server or local desktop).

---

## License

This project is licensed under the **MIT License**.

The MIT License is recommended because:
1. **Broad Developer Adoption:** Allows personal, educational, and commercial usage with minimal restriction.
2. **Ecosystem Standard:** Matches the licensing model of the CustomTkinter and agent skill ecosystems.
3. **Simplicity:** Requires only the preservation of the copyright notice and disclaimer.
