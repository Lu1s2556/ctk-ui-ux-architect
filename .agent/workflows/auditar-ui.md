# Workflow: Auditar UI en CustomTkinter

Workflow para auditar el diseño visual, la geometría, la experiencia de usuario y el rendimiento de una interfaz de escritorio construida con CustomTkinter (CTk), asegurando el estricto cumplimiento de las 12 Leyes de la skill `ctk-ui-ux-architect`.

---

## Pasos del Workflow

### 1. Cargar Conocimiento de la Skill
- Lee y activa [.agent/skills/ctk-ui-ux-architect/SKILL.md](file:///.agent/skills/ctk-ui-ux-architect/SKILL.md).
- Ten presentes las 12 Leyes, el presupuesto de Canvas (máximo 200 widgets), el uso de `UIQueueBatcher` y la elevación cromática adaptativa.

### 2. Análisis Estático de Código Fuente
Revisa el código objetivo del usuario y verifica:
- **Concurrencia:** ¿Existen llamadas bloqueantes (`requests`, `sqlite3`, `time.sleep`) en el hilo principal?
- **Colores:** ¿Hay colores hexadecimales unitarios (`"#1e1e1e"`) en lugar de tuplas `(Light, Dark)`?
- **Ciclo de Vida:** ¿Se usa `.destroy()` en modales con scroll o en la navegación de pestañas/sidebars en lugar de `.withdraw()` y `.tkraise()`?
- **Debounce:** ¿Las búsquedas en vivo y eventos `<Configure>` se disparan en cada evento sin retardo?
- **Listas Densas:** ¿Se instancian más de 40 widgets dentro de un `CTkScrollableFrame`?

### 3. Inspección Dinámica Automática
Ejecuta el inspector dinámico sobre el archivo principal de la aplicación:
```bash
python .agent/skills/ctk-ui-ux-architect/scripts/ctk_inspector.py --target <archivo_usuario.py> [--class NombreClaseApp] --output-dir ./ui_audit
```
El script generará:
- `ui_audit/audit_report.json` con conteo exacto de widgets, dimensiones y colapsos.
- Capturas gráficas automáticas (`01_dark_default.png`, `02_light_default.png`, `03_responsive_small.png`).

### 4. Evaluación Visual y Fallback Multimodal
- Si se generaron las capturas, examina los archivos PNG y cruza las métricas del JSON.
- **Modo Fallback:** Si no hay servidor de despliegue gráfico disponible o la aplicación requiere credenciales de login antes de mostrar la pantalla, solicita al usuario que ejecute la app y te proporcione una captura de pantalla de la ventana abierta.

### 5. Entrega del Informe Estructurado
Genera un reporte con las siguientes 4 secciones concretas:
1. **Críticos de Rendimiento y Memoria:** Bloqueos de hilo, fugas por variables Tk o saturación de Canvas.
2. **Defectos Visuales y Geometría:** Textos truncados, falta de radios concéntricos, contenedores colapsados y colores no adaptativos.
3. **Mejoras de Micro-UX:** Empty states faltantes, saltos de layout en validación y ausencia de feedback de carga.
4. **Plan de Refactorización Paso a Paso:** Lista numerada con los archivos y componentes exactos a aplicar.
