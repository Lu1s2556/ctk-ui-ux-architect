# Guía de Instalación - CTk UI/UX Architect

Selecciona tu agente o entorno de desarrollo:

## 1. Google Antigravity

### Vía CLI (Recomendado)
```bash
agy plugin install https://github.com/Lu1s2556/ctk-ui-ux-architect
```

### Vía Git Clone Global
- **Windows (PowerShell):**
  ```powershell
  git clone https://github.com/Lu1s2556/ctk-ui-ux-architect.git "$HOME\.gemini\config\plugins\ctk-ui-ux-architect"
  ```
- **Linux / macOS:**
  ```bash
  git clone https://github.com/Lu1s2556/ctk-ui-ux-architect.git ~/.gemini/config/plugins/ctk-ui-ux-architect
  ```

---

## 2. Claude Code

En el chat interactivo de Claude Code:

```text
/plugin marketplace add Lu1s2556/ctk-ui-ux-architect
```
```text
/plugin install ctk-ui-ux-architect@ctk-ui-ux-architect
```
*(Envía los dos comandos en turnos separados)*.

---

## 3. OpenAI Codex

Desde tu terminal con Codex CLI:

```bash
codex plugin marketplace add Lu1s2556/ctk-ui-ux-architect
codex plugin add ctk-ui-ux-architect@ctk-ui-ux-architect
```

---

## 4. Instalación por Proyecto (Cualquier Agente)

Para usar las reglas y plantillas en un proyecto de software específico sin instalar globalmente:

```bash
git submodule add https://github.com/Lu1s2556/ctk-ui-ux-architect.git .agent/skills/ctk-ui-ux-architect
```
O simplemente copia la carpeta `.agent/` en la raíz de tu proyecto.
