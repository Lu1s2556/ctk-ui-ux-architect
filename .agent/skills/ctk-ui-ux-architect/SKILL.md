---
name: ctk-ui-ux-architect
description: Diseña, construye, audita y refactoriza interfaces gráficas de escritorio en Python con CustomTkinter (CTk) aplicando arquitectura MVC de alto rendimiento, presupuesto de Canvas, concurrencia con UIQueue, sistema de diseño de 3 niveles de elevación y excelente UX. Úsala siempre que el usuario mencione CustomTkinter, CTk, modernizar Tkinter, crear ventanas desktop en Python, mejorar una UI existente o auditar el diseño/rendimiento de una app CTk.
---

# CustomTkinter UI/UX Architect

Guía definitiva de ingeniería y diseño para construir aplicaciones desktop de alto rendimiento con CustomTkinter (CTk) sobre Tcl/Tk en **Python 3.8.10+**.

---

## Árbol de Decisión Rápida

| Requisito / Escenario | Decisión Técnica Obligatoria | Referencia Clave |
| :--- | :--- | :--- |
| **Navegación entre vistas principales** | Apilar `BaseView` en celda única y alternar con `.tkraise()` | `references/02-layout-and-navigation-patterns.md` |
| **Modal con scroll o formulario pesado** | Crear modal una sola vez; mostrar con `.deiconify()` y ocultar con `.withdraw()` | `references/05-python38-memory-and-packaging.md` |
| **Colección compacta (< 40 ítems)** | `CTkScrollableFrame` + `TimeSlicedBuilder` (lotes de 12 ms) | `references/03-performance-and-concurrency.md` |
| **Tabla densa o catálogo (> 50 filas)** | `CTkThemedTreeview` (`ttk.Treeview` estilizado con tema Clam) | `references/04-hybrid-treeview-and-tables.md` |
| **Operación I/O o cálculo (> 50 ms)** | Hilo daemon secundario + `UIQueueBatcher` (lote de 25 en mainloop) | `references/03-performance-and-concurrency.md` |
| **Búsqueda en tiempo real o resize** | Debounce de 300 ms en `<KeyRelease>` / 450 ms en `<Configure>` | `references/03-performance-and-concurrency.md` |
| **Validación de entradas** | `ValidatedEntry` con label de error de altura fija (`height=16`, sin layout shift) | `templates/ux_components.py` |
| **Iconos e imágenes en Python 3.8** | `ImageCache` singleton para evitar recolección por Garbage Collector | `references/05-python38-memory-and-packaging.md` |

---

## Las 12 Leyes Inquebrantables de CustomTkinter

1. **Presupuesto de Canvas:** CTk renderiza bordes y geometrías mediante `tk.Canvas` en la CPU principal. Máximo 200 widgets vivos por vista y no más de 40-50 filas en un `CTkScrollableFrame`. En widgets repetitivos usar `hover=False`.
2. **Construcción Bajo Demanda y Virtualización:** Renderiza de forma síncrona los primeros 6 elementos visibles; difiere los siguientes con franjas de 12 ms (`.after()`). Para más de 50 filas, usa obligatoriamente `ttk.Treeview` camuflado.
3. **Ciclo de Vida de Vistas (`tkraise` vs `destroy`):** Vistas maestras y tabs se apilan con `grid(row=0, column=0, sticky="nsew")` y alternan con `.tkraise()`. Modales con scrollframe se gestionan con `.withdraw()` y `.deiconify()` para evitar el bug de bloqueo (4-15s) de CTk. Paneles detalle se actualizan con `.configure()`.
4. **Gestión de Memoria en Python 3.8.10:** Conserva referencias duras a todo `CTkImage` para evitar que el GC las destruya. Desconecta `trace_remove()` en variables `StringVar`/`IntVar` cuando se destruyan componentes dinámicos.
5. **Concurrencia Segura (`UIQueue` con Batching):** El hilo principal es el único que puede tocar Tk. Todo worker despacha tareas a una `queue.Queue()`, consumida en ráfagas de hasta 25 eventos por ciclo cada 60 ms.
6. **Debouncing Obligatorio:** Todo filtrado de teclado usa debounce de 300 ms. El redimensionamiento de ventana `<Configure>` usa debounce de 400-500 ms con filtro estricto de emisor (`event.widget is self`).
7. **Arquitectura MVC y Estado Desacoplado:** Las vistas heredan de `ctk.CTkFrame`, no contienen llamadas de red ni SQLite. La sincronización se realiza mediante un `StateManager` reactivo u observador.
8. **Elevación Cromática en 3 Capas (Tuplas Adaptativas):** Prohibido el uso de colores hexadecimales unitarios. Usa tuplas semánticas `(Light, Dark)`: Nivel 0 (Raíz), Nivel 1 (Superficie/Card) y Nivel 2 (Elevado/Inputs). Los frames estructurales usan `fg_color="transparent"`.
9. **Geometría Espacial y Radios Concéntricos:** Layout con `.grid()` explícito. Escala de espaciado en múltiplos de 4/8 px (`4, 8, 12, 16, 24, 32`). Radio del widget hijo según $R_{\text{hijo}} = \max(4, R_{\text{padre}} - P)$.
10. **Jerarquía Tipográfica con `CTkFont`:** Tipografía centralizada por tokens (`H1`, `H2`, `BODY`, `META`). Ajustar `wraplength` reactivo en etiquetas multilínea con debounce.
11. **Micro-UX y Estados Obligatorios:** Jerarquía de botones clara (Primario, Secundario Ghost, Destructivo). Feedback visual inmediato con estado deshabilitado en tareas asíncronas. Empty states mediante `grid_remove()`. Validación inline sin salto de layout.
12. **Auditoría Híbrida (Geométrica + Visual):** Toda entrega se audita estáticamente y dinámicamente con `scripts/ctk_inspector.py` (conteo de widgets, colapso de dimensiones, truncado y capturas multimodales) o vía inspección manual guiada con capturas de pantalla.

---

## Flujos de Trabajo

### Flujo A: Creación de Nueva Interfaz
1. **Definir Tokens y Estructura:** Importar `DesignTokens` y derivar vistas de `ctk.CTkFrame`.
2. **Plantilla Base:** Tomar `templates/base_app_mvc.py` como punto de partida con `Sidebar` + `ViewRouter`.
3. **Componentes y Formularios:** Usar `templates/ux_components.py` (`ValidatedEntry`, `MetricCard`, `AsyncActionButton`, `ToastNotification`).
4. **Verificación:** Ejecutar `ctk_inspector.py` para asegurar 0 widgets truncados y presupuesto de canvas en regla.

### Flujo B: Auditoría y Refactorización de UI Existente
1. **Diagnóstico Estático:** Identificar bloqueos de hilo principal, `.destroy()` recurrentes y colores unitarios hardcodeados.
2. **Diagnóstico Dinámico:** Ejecutar:
   ```bash
   python .agent/skills/ctk-ui-ux-architect/scripts/ctk_inspector.py --target app.py --class MainApp
   ```
3. **Reemplazo Quirúrgico:** Cambiar listas pesadas a `CTkThemedTreeview`, desacoplar eventos con `UIQueueBatcher` y aplicar `tkraise()` en la navegación.

---

## Checklist de Autoverificación Pre-Entrega

- [ ] 1. **Compatibilidad Python 3.8.10:** Tipado mediante `typing.Union`, `typing.Optional`, `typing.List`, etc. Sin `match/case` ni `X | Y`.
- [ ] 2. **Presupuesto Canvas:** Menos de 200 widgets vivos por vista; listas pesadas migradas a `ttk.Treeview`.
- [ ] 3. **Navegación:** Vistas principales alternan con `.tkraise()`; modales pesados usan `.withdraw()`.
- [ ] 4. **Concurrencia:** Cero llamadas de red/base de datos en el hilo principal; uso de `UIQueueBatcher`.
- [ ] 5. **Debouncing:** Búsqueda en vivo (<KeyRelease>) con retardo de 300 ms; resize controlado.
- [ ] 6. **Colores Adaptativos:** Todos los colores personalizados son tuplas `(Light, Dark)` o `"transparent"`.
- [ ] 7. **Radios Concéntricos:** Se cumple $R_{\text{hijo}} = \max(4, R_{\text{padre}} - P)$.
- [ ] 8. **Sin Layout Shifts:** Errores de validación usan labels con altura fija preasignada.
- [ ] 9. **Empty States:** Listas sin registros muestran estado vacío gestionado con `grid_remove()`.
- [ ] 10. **Persistencia de Imágenes:** `CTkImage` anclado a referencias de instancia para evitar Garbage Collection prematuro.
