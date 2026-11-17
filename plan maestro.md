Actúa como un Arquitecto Senior de Software Desktop en Python especializado en CustomTkinter (CTk), Tcl/Tk y Diseño de Sistemas UI/UX. Tu objetivo es construir una Skill completa y dos Workflows para Antigravity que permitan diseñar, auditar y refactorizar interfaces gráficas profesionales en CustomTkinter con soporte estricto para **Python 3.8.10+**.

---

## ⚠️ REGLAS DE EJECUCIÓN PARA TU MODELO (OBLIGATORIAS)

1. **EJECUCIÓN SECUENCIAL POR FASES:** No intentes crear todos los archivos en una sola respuesta si eso recorta el contenido. Ejecuta el trabajo siguiendo el orden exacto de los **Pasos 1 al 9** detallados más abajo, escribiendo cada archivo completo en disco antes de pasar al siguiente.
2. **PROHIBIDO EL CÓDIGO INCOMPLETO:** Nunca escribas `# TODO`, `# implementar aquí`, `pass` ni `...` dentro de los archivos de referencias, scripts o plantillas. Todo código debe ser 100% funcional.
3. **COMPATIBILIDAD ESTRICTA CON PYTHON 3.8.10:**
   - Prohibido usar el operador de unión de tipos `X | Y` (introducido en Python 3.10) o genéricos nativos como `list[str]` / `dict[str, Any]` (introducidos en Python 3.9) sin importar `from __future__ import annotations`.
   - Usa siempre `from typing import Optional, List, Dict, Tuple, Callable, Any, Union`.
   - No utilices sentencias `match / case` (introducidas en Python 3.10).

---

## 📁 ESTRUCTURA EXACTA DE DIRECTORIOS Y ARCHIVOS A CREAR

Debes crear exactamente este árbol de directorios en el proyecto:

```text
.agent/
├── workflows/
│   ├── auditar-ui.md
│   └── mejorar-ui.md
└── skills/
    └── ctk-ui-ux-architect/
        ├── SKILL.md
        ├── scripts/
        │   └── ctk_inspector.py
        ├── references/
        │   ├── 01-design-tokens-and-surfaces.md
        │   ├── 02-layout-and-navigation-patterns.md
        │   ├── 03-performance-and-concurrency.md
        │   ├── 04-hybrid-treeview-and-tables.md
        │   └── 05-python38-memory-and-packaging.md
        └── templates/
            ├── base_app_mvc.py
            └── ux_components.py
```

---

## ⚖️ LAS 12 LEYES INQUEBRANTABLES DE CUSTOMTKINTER (NÚCLEO DE LA SKILL)

Toda la documentación, código y auditorías que generes en los archivos deben hacer cumplir estas 12 leyes:

### Ley 1: Presupuesto de `Canvas` y Renderizado por CPU
CustomTkinter no tiene aceleración por GPU; dibuja cada borde redondeado, fondo y texto sobre widgets `tk.Canvas` usando la CPU en el hilo principal.
- **Límite duro:** Prohibido instanciar más de **200 widgets vivos** simultáneamente en una misma vista o más de **40 a 50 filas** dentro de un `CTkScrollableFrame`.
- **Optimización de hover:** En listas, grillas densas o botones secundarios repetitivos, configurar `hover=False` para evitar saturar el hilo principal con listeners de eventos de ratón.

### Ley 2: Construcción Bajo Demanda, Time-Slicing y Virtualización
- **Prohibido crear miles de objetos Tk de golpe:** Solo deben existir en memoria los widgets necesarios para la interacción inmediata del usuario.
- **Time-Slicing (Franjas de 12 ms):** Cuando una vista deba renderizar entre 15 y 50 tarjetas (`CTkFrame`), renderiza las primeras 6 de forma síncrona para que la ventana aparezca al instante y encola el resto en lotes usando `.after(12, callback)`.
- **Tablas densas (>50 filas):** Prohibido usar `CTkScrollableFrame` o `CTkTable` para grandes volúmenes. Es obligatorio usar un `ttk.Treeview` estilizado con `ttk.Style("clam")` sincronizado con los colores de CustomTkinter.

### Ley 3: Ciclo de Vida de Vistas (`tkraise()` vs `destroy()` vs `withdraw()`)
- **Navegación frecuente (Sidebar / Pestañas):** Prohibido usar `.destroy()` y recrear vistas en cada clic, y prohibido usar `.pack_forget()` en bucle (fuerza recálculos costosos de geometría). Apila todas las vistas frecuentes en la misma celda `grid(row=0, column=0, sticky="nsew")` del contenedor principal y alterna entre ellas usando **`vista.tkraise()`** (cambio instantáneo en el eje Z sin recalcular layout).
- **Bug crítico de `CTkToplevel` + `CTkScrollableFrame`:** Destruir (`.destroy()`) un `CTkToplevel` que contiene un `CTkScrollableFrame` corrompe el estado interno de CTk y hace que el siguiente `Toplevel` tarde entre **4 y 15 segundos** en crearse. Solución obligatoria: instanciar el modal una vez y ocultarlo/mostrarlo con **`.withdraw()`** y **`.deiconify()`**, usando `.grab_set()` y `.focus()`.
- **Patrón Maestro-Detalle:** Al seleccionar un ítem en la lista Maestro, está prohibido destruir y recrear el panel de Detalle. El panel de Detalle se instancia una sola vez y sus widgets hijos se actualizan quirúrgicamente mediante **`.configure(text=...)`**.

### Ley 4: Gestión de Memoria en Python 3.8.10 (Imágenes y Variables)
- **Recolección de basura en `CTkImage`:** Crear un `CTkImage` en una variable local dentro de una función hace que el Garbage Collector de Python 3.8.10 borre la imagen de la RAM, dejando el widget en blanco sin lanzar excepción. Siempre guarda la referencia en `self._img_name = ctk.CTkImage(...)` y además asígnala al widget (`boton._image_ref = self._img_name`).
- **Limpieza de Variables Tk:** Cuando un componente dinámico se destruya definitivamente, elimina los *traces* activos de `ctk.StringVar()` o `ctk.IntVar()` (`var.trace_remove(...)`) para evitar fugas de memoria (*memory leaks*) por callbacks fantasma que apuntan a widgets destruidos.

### Ley 5: Concurrencia Segura (`UIQueue` con Batching y Shared State)
Tkinter **no es thread-safe**. Tocar cualquier propiedad de un widget desde un `threading.Thread` secundario causa bloqueos o *segmentation faults*.
- **Regla de los 50 ms:** Cualquier tarea que tarde más de 50 ms (consultas SQLite/API, lectura de disco, envío de correos, procesamiento de datos) va a un hilo secundario (`daemon=True`).
- **Patrón `UIQueue` por lotes (Batching):** Los hilos secundarios depositan eventos en una `queue.Queue()`. El hilo principal ejecuta un consumidor cada 50-100 ms con `.after()` que extrae **hasta 25 mensajes de golpe** (`get_nowait()`) y aplica una única actualización visual agrupada, evitando que 200 mensajes disparen 200 redibujados del `Canvas`.
- **Capa de Estado Compartido (Snapshot):** Para telemetría o progreso continuo, el hilo secundario escribe en un diccionario protegido por `threading.Lock()`, y la UI lee un *snapshot* periódico con `.after(100)` actualizando solo los widgets cuyo valor haya cambiado.

### Ley 6: Política Obligatoria de Debouncing (Teclado y `<Configure>`)
- **Búsqueda en tiempo real:** Prohibido filtrar o redibujar widgets en cada pulsación de tecla. Vincula `<KeyRelease>` a un *debounce* de **300 ms** usando `self.after_cancel(self._debounce_id)` y `self.after(300, self._ejecutar_filtro)`.
- **Redimensionado de ventana (`<Configure>`):** Arrastrar el borde de la ventana dispara decenas de eventos `<Configure>` por segundo, obligando a la CPU a recalcular las matemáticas de todos los `corner_radius`. Si la interfaz ajusta elementos dinámicamente al redimensionar, envuelve el manejador en un *debounce* de **400-500 ms** o bloquea el redimensionamiento (`app.resizable(False, False)`) en utilidades de tamaño fijo.

### Ley 7: Arquitectura MVC / Component-Based y StateManager
- Ningún archivo de vista puede contener consultas a bases de datos, llamadas HTTP ni lógica de negocio.
- Cada sección visual (Sidebar, Tarjeta, Formulario, Encabezado) debe ser una clase independiente que herede de `ctk.CTkFrame`.
- Las vistas no se comunican directamente entre sí; utilizan un `StateManager` observable (patrón Observer) donde se suscriben a claves de estado y actualizan sus widgets con `.configure()`.

### Ley 8: Sistema de Elevación Cromática en 3 Capas (Tuplas Adaptativas)
Prohibido usar colores hexadecimales fijos de un solo modo (ej. `"#1e1e1e"`). Todo color personalizado debe ser una tupla `("color_modo_claro", "color_modo_oscuro")` o `"transparent"`:
- **Nivel 0 (Fondo Raíz de Ventana):** `("#F8FAFC", "#0F172A")`
- **Nivel 1 (Superficie Primaria / Sidebar / Tarjetas):** `("#FFFFFF", "#1E293B")` con borde sutil `border_width=1`, `border_color=("#E2E8F0", "#334155")`.
- **Nivel 2 (Superficie Elevada / Inputs / Elementos Activos):** `("#F1F5F9", "#334155")`.
- **Contenedores de Layout Puro:** Cualquier `CTkFrame` usado solo para agrupar o alinear otros widgets debe llevar `fg_color="transparent"` y `border_width=0` para ahorrar operaciones de dibujo en el `Canvas` y evitar recuadros grises anidados.

### Ley 9: Geometría Espacial, Grilla de 8px y Radios Concéntricos
- **Gestor de geometría:** Usa `.grid()` con `grid_columnconfigure` y `grid_rowconfigure` explícitos para toda estructura principal. Reserva `.pack()` únicamente para apilar elementos lineales simples dentro de una tarjeta o barra de botones.
- **Ritmo de espaciado (Escala de 4/8px):** Usa exclusivamente `padx` y `pady` en valores de la escala: `4, 8, 12, 16, 24, 32`.
- **Fórmula de Radios Concéntricos:** Cuando un widget con bordes redondeados está dentro de un `CTkFrame` con padding $P$, el radio del hijo nunca debe ser igual al del padre. Aplica siempre:
  $$R_{\text{hijo}} = \max(4, R_{\text{padre}} - P)$$
  *(Ejemplo: Tarjeta con `corner_radius=12` y `padx=6` -> Botón o Input hijo con `corner_radius=6`)*.

### Ley 10: Jerarquía Tipográfica con `CTkFont` y Escalado HiDPI
Prohibido usar tuplas `font=("Arial", 12)` sueltas en cada widget. Centraliza instancias de `ctk.CTkFont` en un objeto de Tokens:
- **H1 (Título de Vista):** `CTkFont(size=24, weight="bold")`, `text_color=("#0F172A", "#F8FAFC")`
- **H2 (Título de Tarjeta/Sección):** `CTkFont(size=16, weight="bold")`, `text_color=("#0F172A", "#F8FAFC")`
- **Body (Texto estándar y Controles):** `CTkFont(size=13, weight="normal")`, `text_color=("#1E293B", "#E2E8F0")`
- **Meta / Notas / Labels de campo:** `CTkFont(size=12, weight="normal")`, `text_color=("#64748B", "#94A3B8")`
- **Wraplength dinámico:** En textos largos (`CTkLabel`), actualiza `wraplength` dentro de un manejador con debounce para que el texto no se corte al achicar la ventana.

### Ley 11: Estados UX Obligatorios (Empty States, Botones y Formularios sin Saltos)
- **Jerarquía de Botones (Call to Action):**
  1. *Primario:* Color de acento sólido (`("#2563EB", "#3B82F6")`), `hover_color=("#1D4ED8", "#2563EB")`, texto blanco. Máximo uno por grupo de acción.
  2. *Secundario (Ghost Button):* `fg_color="transparent"`, `border_width=1` o `2`, `border_color=("#CBD5E1", "#475569")`, `text_color=("#334155", "#E2E8F0")`, `hover_color=("#F1F5F9", "#334155")`.
  3. *Destructivo:* `fg_color=("#DC2626", "#EF4444")`, `hover_color=("#B91C1C", "#DC2626")`.
- **Feedback Instantáneo en Acciones Asíncronas:** En el milisegundo en que el usuario hace clic en un botón que lanza un hilo, cambia a `state="disabled"`, guarda el texto original y muestra `"Procesando..."` (más una `CTkProgressBar(mode="indeterminate")` si supera 1 segundo). Restaura el botón desde la `UIQueue` al terminar.
- **Empty State (Estado Vacío):** Ninguna lista o tabla vacía puede mostrarse como un hueco en blanco. Muestra un `CTkFrame` centrado con icono `CTkImage`, título amigable, subtítulo en color tenue y botón de acción. Ocúltalo con **`grid_remove()`** (recuerda las coordenadas de grid) cuando lleguen datos; nunca uses `.destroy()`.
- **Validación Inline con Cero Layout Shift:** Prohibido usar `tkinter.messagebox.showerror` para campos vacíos o formatos inválidos. Crea debajo de cada `CTkEntry` un `CTkLabel` de error con `text=""` y altura fija (`height=16`) desde el inicio. Si falla la validación, cambia el `border_color` del `CTkEntry` a `("#DC2626", "#EF4444")` y escribe el motivo en el label. Al no insertar ni destruir widgets, la interfaz nunca da saltos bruscos.
- **Artefacto de Esquinas en `.place()` (Notificaciones Toast):** Al superponer un `CTkFrame` con `.place()` sobre otro contenedor, pásale explícitamente `bg_color` igual al `fg_color` del contenedor padre donde descansa para evitar que las 4 esquinas del `Canvas` muestren píxeles de otro color.

### Ley 12: Auditoría Híbrida (Geométrica + Visual Multimodal)
Toda interfaz creada o modificada debe verificarse de dos formas:
1. **Vía Automática (`scripts/ctk_inspector.py`):** Inspecciona el árbol de widgets en vivo (`winfo_children()`), verifica el presupuesto de `Canvas`, detecta textos truncados (`winfo_reqwidth() > winfo_width()`), contenedores colapsados (`width <= 1` o `height <= 1`), colores hardcodeados sin tupla adaptativa, y genera capturas automáticas en modos Light/Dark y dos tamaños de ventana.
2. **Vía Manual Guiada (Fallback):** Si no hay entorno gráfico X11/Windows disponible o la vista requiere autenticación/interacción previa, el agente solicita al usuario una captura de pantalla de la ventana y audita la imagen junto con el código fuente.

---

## 🛠️ PLAN DE IMPLEMENTACIÓN PASO A PASO (ARCHIVO POR ARCHIVO)

Ejecuta cada paso en orden y escribe el contenido completo de cada archivo:

### PASO 1: Crear `.agent/skills/ctk-ui-ux-architect/SKILL.md`
Escribe el archivo principal de la skill (máximo 350 líneas) con:
1. **Frontmatter YAML:**
   ```yaml
   ---
   name: ctk-ui-ux-architect
   description: Diseña, construye, audita y refactoriza interfaces gráficas de escritorio en Python con CustomTkinter (CTk) aplicando arquitectura MVC de alto rendimiento, presupuesto de Canvas, concurrencia con UIQueue, sistema de diseño de 3 niveles de elevación y excelente UX. Úsala siempre que el usuario mencione CustomTkinter, CTk, modernizar Tkinter, crear ventanas desktop en Python, mejorar una UI existente o auditar el diseño/rendimiento de una app CTk.
   ---
   ```
2. **Resumen Ejecutivo y Cuándo Usarla.**
3. **Árbol de Decisión Rápida (Tabla Markdown):**
   - Si va a cambiar entre vistas del menú principal -> `BaseView` + `.tkraise()` (ver `references/02-layout-and-navigation-patterns.md`).
   - Si va a abrir un modal con scroll -> `CTkToplevel` + `.withdraw()` / `.deiconify()` (ver `references/05-python38-memory-and-packaging.md`).
   - Si va a mostrar <40 ítems -> `CTkScrollableFrame` con Time-Slicing de 12 ms (ver `references/03-performance-and-concurrency.md`).
   - Si va a mostrar >50 filas tabulares -> `ttk.Treeview` camuflado con tema CTk (ver `references/04-hybrid-treeview-and-tables.md`).
   - Si va a ejecutar tareas >50 ms -> `UIQueue` con Batching en hilo daemon (ver `references/03-performance-and-concurrency.md`).
4. **Resumen de las 12 Leyes Inquebrantables.**
5. **Flujo de Trabajo para Crear Nueva UI vs Auditar/Mejorar UI Existente** (explicando cómo invocar `scripts/ctk_inspector.py` o pedir captura al usuario).
6. **Checklist de Autoverificación antes de entregar código** (10 puntos verificables).

---

### PASO 2: Crear `.agent/skills/ctk-ui-ux-architect/references/01-design-tokens-and-surfaces.md`
Documenta con código Python completo (compatible con Python 3.8.10) una clase estática o módulo `DesignTokens` lista para copiar y usar que incluya:
- **Paleta Semántica en Tuplas `(Light, Dark)`:**
  - `BG_ROOT = ("#F8FAFC", "#0F172A")`
  - `BG_SURFACE = ("#FFFFFF", "#1E293B")`
  - `BG_ELEVATED = ("#F1F5F9", "#334155")`
  - `BORDER_SUBTLE = ("#E2E8F0", "#334155")`
  - `BORDER_FOCUS = ("#2563EB", "#3B82F6")`
  - `TEXT_PRIMARY = ("#0F172A", "#F8FAFC")`
  - `TEXT_SECONDARY = ("#475569", "#94A3B8")`
  - `TEXT_MUTED = ("#94A3B8", "#64748B")`
  - `ACCENT_PRIMARY = ("#2563EB", "#3B82F6")`
  - `ACCENT_HOVER = ("#1D4ED8", "#2563EB")`
  - `STATUS_SUCCESS = ("#16A34A", "#22C55E")`
  - `STATUS_WARNING = ("#D97706", "#F59E0B")`
  - `STATUS_DANGER = ("#DC2626", "#EF4444")`
- **Fábrica de Tipografía (`CTkFont`):** Métodos o atributos inicializados después de crear la raíz `CTk()` para `H1`, `H2`, `H3`, `BODY`, `BODY_BOLD`, `META`, `MONO`.
- **Constantes de Geometría y Radios Concéntricos:** `SPACE_XS = 4`, `SPACE_SM = 8`, `SPACE_MD = 12`, `SPACE_LG = 16`, `SPACE_XL = 24`, `SPACE_2XL = 32`, `RADIUS_CARD = 12`, `RADIUS_CONTROL = 6`, más una función auxiliar `concentric_radius(parent_radius: int, padding: int) -> int`.
- **Fábrica de Botones Estándar:** Funciones helper `create_primary_button`, `create_ghost_button`, `create_danger_button` que aplican todos los tokens automáticamente.

---

### PASO 3: Crear `.agent/skills/ctk-ui-ux-architect/references/02-layout-and-navigation-patterns.md`
Escribe las guías y patrones de código completos para:
1. **Patrón 1: Sidebar Dashboard + ViewRouter con `tkraise()`:**
   - Sidebar fijo en `column=0` con `width=220`, `grid_propagate(False)`, indicador visual de vista activa (cambiando el `fg_color` del botón seleccionado a `BG_ELEVATED` y el resto a `"transparent"`), y selector de tema Light/Dark/System en el pie del sidebar.
   - Contenedor de vistas en `column=1` (`weight=1`), apilando instancias de `BaseView` en `row=0, column=0, sticky="nsew"` y cambiando con `.tkraise()` y un hook `on_show()`.
2. **Patrón 2: Card Grid Responsivo + Construcción Time-Sliced:**
   - Cómo distribuir tarjetas en N columnas usando `.grid( sticky="nsew")` con `uniform="cols"` en `grid_columnconfigure`.
3. **Patrón 3: Vista Maestro-Detalle Quirúrgica:**
   - Panel izquierdo (Maestro) y panel derecho (Detalle). Demostración exacta de cómo el método `load_record(record_dict)` del Detalle solo llama a `.configure()` sobre los widgets ya creados, alternando con un `EmptyStateFrame` cuando no hay selección.
4. **Patrón 4: Componente `EmptyState` Reutilizable:**
   - Cómo mostrarlo con `.grid()` y ocultarlo con `.grid_remove()` sin destruir sus objetos Tk.

---

### PASO 4: Crear `.agent/skills/ctk-ui-ux-architect/references/03-performance-and-concurrency.md`
Escribe la implementación completa y comentada en Python 3.8.10 de los 4 motores de fluidez:
1. **Clase `UIQueueBatcher`:**
   - Usa `queue.Queue()` y un bucle `.after(60, self._process_batch)` que extrae hasta `max_batch_size=25` tareas `(callback, args, kwargs)` por ciclo usando `get_nowait()`, ejecutándolas en un solo turno del mainloop.
   - Incluye un método `run_async(worker_fn, on_success, on_error, on_progress)` que lanza un `threading.Thread(daemon=True)` y encola los callbacks de vuelta al hilo principal de forma segura.
2. **Clase `SharedStateSnapshot`:**
   - Estado protegido con `threading.Lock()` para productores de alta frecuencia y lector periódico en UI que solo llama a `.configure()` si el valor nuevo difiere del último valor renderizado (`self._last_rendered_state`).
3. **Clase `TimeSlicedBuilder`:**
   - Recibe una lista de datos y un `item_factory(parent, item_data)`. Renderiza los primeros 6 ítems inmediatamente y programa el resto en porciones que no superen **12 ms** (`time.perf_counter()`) por ciclo de `.after(15, ...)`. Incluye método `.cancel()` por si el usuario cambia de vista o filtra antes de terminar.
4. **Decorador / Mixin `Debouncer`:**
   - Implementación limpia usando un diccionario `self._debounce_timers: Dict[str, str] = {}` con `widget.after_cancel()` y `widget.after(wait_ms, fn)`, mostrando cómo aplicarlo a un `CTkEntry` de búsqueda (300 ms) y al evento `<Configure>` de la ventana principal (450 ms) evitando llamadas recursivas cuando el evento proviene de widgets hijos (`if event.widget is not self: return`).

---

### PASO 5: Crear `.agent/skills/ctk-ui-ux-architect/references/04-hybrid-treeview-and-tables.md`
Documenta la solución definitiva para mostrar tablas de 100 a 50.000 filas en CustomTkinter sin congelar la CPU:
- **Clase `CTkThemedTreeview(ctk.CTkFrame)`:**
  - Envuelve un `ttk.Treeview` + `ctk.CTkScrollbar` vertical y horizontal dentro de un `CTkFrame` con bordes redondeados.
  - Configura `ttk.Style()` con el tema `"clam"` (ya que los temas `"vista"` o `"aqua"` ignoran los colores de fondo personalizados).
  - Detecta el modo actual (`ctk.get_appearance_mode()`) y el factor de escalado DPI (`self._get_widget_scaling()`) para ajustar automáticamente:
    - `background`, `fieldbackground`, `foreground` y `rowheight = int(32 * scaling)` en `"Treeview"`.
    - Colores de cabecera, fuente en negrita y `relief="flat"` en `"Treeview.Heading"`.
    - Color de fila seleccionada (`selected`) usando `ACCENT_PRIMARY`.
    - Tags para filas alternas (`evenrow`, `oddrow`) que se actualizan automáticamente cuando el usuario cambia entre modo Claro y Oscuro.

---

### PASO 6: Crear `.agent/skills/ctk-ui-ux-architect/references/05-python38-memory-and-packaging.md`
Documenta los errores silenciosos y soluciones de producción para Python 3.8.10:
1. **Gestor de Imágenes Seguro (`ImageCache`):**
   - Clase singleton que carga iconos con `PIL.Image`, instancia `ctk.CTkImage(light_image=..., dark_image=..., size=...)` y los retiene en un diccionario en memoria para evitar tanto la recolección de basura de Python 3.8 como la lectura repetida de disco. Incluye generador de iconos de respaldo con `PIL.ImageDraw` por si falta un archivo físico.
2. **Gestor de Ventanas Modales (`SafeModalToplevel`):**
   - Clase base que hereda de `ctk.CTkToplevel`, intercepta el botón de cerrar ventana (`WM_DELETE_WINDOW`) para llamar a `self.hide()` (`.grab_release()` + `.withdraw()`) en lugar de `.destroy()`, evitando el bug de 4 a 15 segundos de `CTkScrollableFrame`.
3. **Limpieza de `StringVar` / `IntVar`:**
   - Mixin `CleanableWidgetMixin` que registra cada `trace_add` y ejecuta `trace_remove` automáticamente en el evento `<Destroy>`.
4. **Empaquetado con PyInstaller y Rutas de Recursos:**
   - Función `resource_path(relative_path: str) -> str` compatible con `sys._MEIPASS`.
   - Comando exacto de compilación: `pyinstaller --noconsole --onefile --collect-all customtkinter main.py`.

---

### PASO 7: Crear `.agent/skills/ctk-ui-ux-architect/scripts/ctk_inspector.py`
Escribe un script de Python 3.8+ completo, ejecutable por CLI y también importable, que sirva como motor de auditoría automática de la skill:
- **Funcionalidad CLI:** `python ctk_inspector.py --target ruta/al/archivo.py [--class NombreClaseApp] [--output-dir ./ui_audit]`
- **Qué debe hacer el script cuando se acopla a una instancia de `ctk.CTk`:**
  1. Programar la inspección con `app.after(600, ...)` para permitir que el `Canvas` termine de renderizar.
  2. **Auditoría del Árbol de Widgets (`audit_widget_tree`):** Recorrer recursivamente `winfo_children()` y generar un reporte JSON (`audit_report.json`) que contabilice y detecte:
     - `total_widgets`: Número total de widgets vivos (Alerta `WARNING` si > 150, `CRITICAL` si > 250).
     - `scrollable_frame_loads`: Cantidad de hijos dentro de cada `CTkScrollableFrame` (Alerta `CRITICAL` si > 45 filas).
     - `collapsed_containers`: Contenedores `CTkFrame` visibles con `winfo_width() <= 2` o `winfo_height() <= 2` (suele ocurrir por olvidar `grid_columnconfigure(weight=1)`).
     - `truncated_texts`: Widgets `CTkLabel` o `CTkButton` donde `winfo_reqwidth() > winfo_width() + 4` (texto cortado).
     - `hardcoded_single_colors`: Widgets cuyo `fg_color` o `text_color` es un string hexadecimal único `"#..."` en lugar de una tupla `(claro, oscuro)` o `"transparent"`.
     - `overlapping_siblings`: Widgets hermanos en el mismo padre cuyas cajas delimitadoras `(winfo_x, winfo_y, winfo_width, winfo_height)` se solapan involuntariamente.
  3. **Capturas Multimodales Automáticas (si `PIL.ImageGrab` está disponible):**
     - Elevar la ventana (`app.lift()`, `app.focus_force()`, `app.update_idletasks()`).
     - Capturar `01_dark_default.png` en modo `"Dark"`.
     - Cambiar a `ctk.set_appearance_mode("Light")`, esperar 300 ms, capturar `02_light_default.png`.
     - Redimensionar la ventana a un tamaño compacto (`820x540`), esperar 400 ms, capturar `03_responsive_small.png`.
  4. Cerrar la aplicación limpiamente (`app.quit()`, `app.destroy()`) e imprimir en consola un resumen legible para el agente con la ruta de las capturas y las violaciones detectadas.

---

### PASO 8: Crear las Plantillas en `.agent/skills/ctk-ui-ux-architect/templates/`
1. **`templates/ux_components.py`:**
   Código completo y reutilizable de 4 componentes esenciales que no existen de serie en CustomTkinter:
   - `ValidatedEntry(ctk.CTkFrame)`: Incluye Label superior, `CTkEntry`, y Label inferior de error pre-reservado (`height=16`) para validación en vivo sin *layout shift*, con método `.set_error(msg: Optional[str])` y `.get()`.
   - `MetricCard(ctk.CTkFrame)`: Tarjeta de KPI con título secundario, valor grande en fuente `H1`, badge de tendencia e icono opcional, actualizable vía `.update_metric(value, trend)`.
   - `ToastNotification`: Notificación flotante no bloqueante posicionada en la esquina inferior derecha con `.place(relx=0.98, rely=0.96, anchor="se")`, configurando correctamente `bg_color` para evitar artefactos en las esquinas redondeadas y desapareciendo sola tras 3.5 segundos con `.after()`.
   - `AsyncActionButton(ctk.CTkButton)`: Botón que al hacer clic se deshabilita automáticamente, cambia su texto a `"Procesando..."`, ejecuta una función en segundo plano mediante `UIQueueBatcher` y se restaura solo al terminar.
2. **`templates/base_app_mvc.py`:**
   Esqueleto completo y funcional de una aplicación CustomTkinter que integra `DesignTokens`, `StateManager`, `UIQueueBatcher`, `Sidebar` con indicador activo, `ViewRouter` con `tkraise()`, una vista con `CTkThemedTreeview` + búsqueda con debounce de 300 ms + `EmptyState`, y soporte para el flag `--inspect` conectado a `ctk_inspector.py`.

---

### PASO 9: Crear los Workflows en `.agent/workflows/`
1. **`.agent/workflows/auditar-ui.md`:**
   - **Descripción:** Audita el diseño visual, la geometría, la UX y el rendimiento de una interfaz CustomTkinter.
   - **Pasos del Workflow:**
     1. Activar y leer `.agent/skills/ctk-ui-ux-architect/SKILL.md`.
     2. Analizar estáticamente el código fuente del usuario buscando violaciones a las 12 Leyes (hilos bloqueantes, falta de tuplas de color, exceso de widgets en `CTkScrollableFrame`, uso de `.destroy()` en navegación o modales, falta de debounce).
     3. Ejecutar `python .agent/skills/ctk-ui-ux-architect/scripts/ctk_inspector.py --target <archivo_usuario.py>`.
     4. Si el script genera las capturas y el `audit_report.json`, inspeccionar visualmente las imágenes PNG (`01_dark_default.png`, `02_light_default.png`, `03_responsive_small.png`) y cruzar los datos geométricos. Si la vista requiere login previo o falla la captura en el entorno actual, pedir al usuario que adjunte una captura de pantalla de la ventana abierta.
     5. Entregar un **Informe de Auditoría UI/UX** estructurado en: *Críticos de Rendimiento/Memoria*, *Defectos Visuales y de Geometría*, *Mejoras de Micro-UX* y *Plan de Refactorización Exacto*.
2. **`.agent/workflows/mejorar-ui.md`:**
   - **Descripción:** Refactoriza y moderniza una interfaz CustomTkinter o Tkinter existente aplicando las 12 Leyes de la skill `ctk-ui-ux-architect` sin romper la lógica de negocio.
   - **Pasos del Workflow:**
     1. Ejecutar primero el diagnóstico del workflow `/auditar-ui` (análisis de código + `ctk_inspector.py` o captura del usuario).
     2. Separar cualquier lógica de negocio incrustada en la UI hacia un controlador o servicio aislado y conectar las operaciones lentas mediante `UIQueueBatcher`.
     3. Aplicar el sistema de 3 capas de elevación (`DesignTokens`), tipografía `CTkFont`, radios concéntricos, validación sin *layout shift* y navegación por `tkraise()`.
     4. Reemplazar listas pesadas por `CTkThemedTreeview` o `TimeSlicedBuilder`.
     5. Volver a ejecutar `ctk_inspector.py` sobre el código refactorizado para comprobar que hay **0 alertas críticas** y que las capturas en modo Light, Dark y tamaño reducido se ven limpias y bien distribuidas antes de finalizar.

---

Comienza ahora mismo con el **PASO 1** (`SKILL.md`) y avanza secuencialmente hasta completar el **PASO 9**.