# Workflow: Mejorar UI en CustomTkinter

Workflow para modernizar, acelerar y rediseñar interfaces existentes de CustomTkinter o Tkinter, aplicando arquitectura limpia MVC y las 12 Leyes de la skill `ctk-ui-ux-architect` sin alterar la lógica de negocio.

---

## Pasos del Workflow

### 1. Diagnóstico Inicial Previo
- Ejecuta primero el workflow `auditar-ui` sobre el código objetivo.
- Identifica la lista de alertas críticas (bloqueos de hilo, exceso de widgets en Canvas, colores no adaptativos).

### 2. Desacoplamiento de Lógica y Concurrencia
- Extrae toda llamada a bases de datos, APIs de red o cómputo pesado fuera de los widgets.
- Conecta las operaciones asíncronas con `UIQueueBatcher` (ver [references/03-performance-and-concurrency.md](file:///.agent/skills/ctk-ui-ux-architect/references/03-performance-and-concurrency.md)) usando un hilo secundario y despachando actualizaciones de estado seguras en el hilo principal.
- Envuelve los botones que disparan tareas pesadas con `AsyncActionButton`.

### 3. Aplicación de Tokens de Diseño y Geometría
- Importa `DesignTokens` (ver [references/01-design-tokens-and-surfaces.md](file:///.agent/skills/ctk-ui-ux-architect/references/01-design-tokens-and-surfaces.md)).
- Reemplaza colores fijos de un solo tema por tuplas semánticas `(Light, Dark)`.
- Sustituye tuplas de fuentes por instancias centralizadas de `CTkFont`.
- Ajusta paddings a la escala de 4/8 px (`4, 8, 12, 16, 24, 32`) y calcula radios concéntricos:
  $$R_{\text{hijo}} = \max(4, R_{\text{padre}} - P)$$

### 4. Optimización de Vistas y Componentes Clave
- **Navegación:** Reemplaza `.destroy()` o `.pack_forget()` continuos en barras laterales por un `ViewRouter` con `.tkraise()`.
- **Modales:** Convierte ventanas emergentes secundarias a `SafeModalToplevel` con `.withdraw()` y `.deiconify()`.
- **Listas Densas (> 50 filas):** Sustituye `CTkScrollableFrame` o `CTkTable` por `CTkThemedTreeview` con tema Clam.
- **Entradas y Formularios:** Sustituye `tkinter.messagebox.showerror` por `ValidatedEntry` con label de error de altura fija para garantizar Cero Salto de Layout (Zero Layout Shift).
- **Listas Vacías:** Implementa `EmptyState` gestionado con `grid_remove()`.

### 5. Verificación y Cierre
- Ejecuta nuevamente `ctk_inspector.py` sobre la versión refactorizada:
  ```bash
  python .agent/skills/ctk-ui-ux-architect/scripts/ctk_inspector.py --target <archivo_refactorizado.py>
  ```
- Comprueba que el veredicto sea `PASSED_PERFECT` o `PASSED_WITH_WARNINGS` con **0 alertas críticas**.
- Entrega al usuario el resumen de mejoras de rendimiento y calidad visual obtenidas.
