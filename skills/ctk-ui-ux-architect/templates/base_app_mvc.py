#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plantilla Base MVC para Aplicaciones CustomTkinter
Integra: DesignTokens, StateManager, UIQueueBatcher, Sidebar + ViewRouter (tkraise),
CTkThemedTreeview con búsqueda con debounce de 300 ms, y soporte del flag --inspect.
Compatibilidad estricta: Python 3.8.10+
"""

from __future__ import annotations
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, List, Tuple, Any, Optional, Callable

# --- 1. MODELO / ESTADO COMPARTIDO (StateManager) ---

class StateManager:
    """Gestor de estado observable simple y thread-safe."""
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state: Dict[str, Any] = {}
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._state[key] = value
            callbacks = list(self._subscribers.get(key, []))
        for cb in callbacks:
            try:
                cb(value)
            except Exception as e:
                print("Error en callback de StateManager:", str(e))

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._state.get(key, default)

    def subscribe(self, key: str, callback: Callable[[Any], None]) -> None:
        with self._lock:
            if key not in self._subscribers:
                self._subscribers[key] = []
            self._subscribers[key].append(callback)


# --- 2. CONCURRENCIA SEGURA (UIQueueBatcher) ---
# shortcut: standalone template copy, extract to shared module if packaging

class UIQueueBatcher:
    """Despacha tareas desde hilos secundarios al hilo principal en ráfagas."""
    def __init__(self, root: ctk.CTk, interval_ms: int = 60, max_batch_size: int = 25) -> None:
        self.root = root
        self.interval_ms = interval_ms
        self.max_batch_size = max_batch_size
        self._queue: queue.Queue = queue.Queue()
        self._running = True
        self._schedule_poll()

    def _schedule_poll(self) -> None:
        if self._running:
            self.root.after(self.interval_ms, self._process_batch)

    def _process_batch(self) -> None:
        processed = 0
        while processed < self.max_batch_size:
            try:
                task = self._queue.get_nowait()
            except queue.Empty:
                break
            try:
                fn, args, kwargs = task
                fn(*args, **kwargs)
            except Exception as e:
                print("Error ejecutando callback en UIQueueBatcher:", str(e))
            finally:
                self._queue.task_done()
                processed += 1
        self._schedule_poll()

    def post(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        if not self._running:
            return
        self._queue.put((fn, args, kwargs))

    def stop(self) -> None:
        self._running = False


# --- 3. COMPONENTE HÍBRIDO: CTkThemedTreeview ---

class CTkThemedTreeview(ctk.CTkFrame):
    def __init__(self, master: Any, columns: Tuple[str, ...], **kwargs: Any) -> None:
        super().__init__(
            master=master,
            corner_radius=8,
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            **kwargs
        )
        self.columns = columns
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._style = ttk.Style()
        if "clam" in self._style.theme_names():
            self._style.theme_use("clam")

        self.tree = ttk.Treeview(
            self,
            columns=self.columns,
            show="headings",
            style="BaseMVC.Treeview",
            selectmode="extended"
        )
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(2, 0), pady=2)

        self.vsb = ctk.CTkScrollbar(self, orientation="vertical", command=self.tree.yview, width=14)
        self.vsb.grid(row=0, column=1, sticky="ns", padx=(0, 2), pady=2)
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.update_theme()

    def update_theme(self) -> None:
        is_dark = (ctk.get_appearance_mode().lower() == "dark")
        bg_surface = "#1E293B" if is_dark else "#FFFFFF"
        bg_alt = "#243247" if is_dark else "#F8FAFC"
        bg_head = "#0F172A" if is_dark else "#F1F5F9"
        fg_text = "#F8FAFC" if is_dark else "#0F172A"
        fg_head = "#94A3B8" if is_dark else "#475569"

        self._style.configure(
            "BaseMVC.Treeview",
            background=bg_surface,
            fieldbackground=bg_surface,
            foreground=fg_text,
            borderwidth=0,
            rowheight=30
        )
        self._style.map(
            "BaseMVC.Treeview",
            background=[("selected", "#2563EB" if not is_dark else "#3B82F6")],
            foreground=[("selected", "#FFFFFF")]
        )
        self._style.configure(
            "BaseMVC.Treeview.Heading",
            background=bg_head,
            foreground=fg_head,
            relief="flat",
            font=("Segoe UI", 10, "bold")
        )
        self.tree.tag_configure("evenrow", background=bg_surface, foreground=fg_text)
        self.tree.tag_configure("oddrow", background=bg_alt, foreground=fg_text)

    def set_headers(self, headers: Dict[str, Tuple[str, int]]) -> None:
        for col, (title, width) in headers.items():
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor="w")

    def insert_rows(self, data: List[Tuple[Any, ...]]) -> None:
        self.clear()
        for idx, row in enumerate(data):
            tag = "evenrow" if (idx % 2 == 0) else "oddrow"
            self.tree.insert("", "end", values=row, tags=(tag,))

    def clear(self) -> None:
        children = self.tree.get_children()
        if children:
            self.tree.delete(*children)


# --- 4. VISTAS Y ENRUTADOR ---

class BaseView(ctk.CTkFrame):
    def __init__(self, master: Any, view_name: str, **kwargs: Any) -> None:
        super().__init__(master=master, fg_color="transparent", **kwargs)
        self.view_name = view_name

    def on_show(self) -> None:
        pass


class TableCatalogView(BaseView):
    """Vista de catálogo con búsqueda con debounce de 300 ms y empty state."""
    def __init__(self, master: Any, **kwargs: Any) -> None:
        super().__init__(master=master, view_name="catalog", **kwargs)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._all_records: List[Tuple[str, str, str, str]] = [
            ("SKU-001", "Laptop Pro 16", "Hardware", "$1,499.00"),
            ("SKU-002", "Monitor 4K 27\"", "Periféricos", "$399.00"),
            ("SKU-003", "Teclado Mecánico", "Accesorios", "$89.00"),
            ("SKU-004", "Mouse Ergonómico", "Accesorios", "$59.00"),
            ("SKU-005", "Hub USB-C 7 en 1", "Hardware", "$45.00"),
            ("SKU-006", "Auriculares Studio", "Audio", "$129.00")
        ]
        self._search_after_id: Optional[str] = None

        self._build_toolbar()
        self._build_content()

    def _build_toolbar(self) -> None:
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        lbl_title = ctk.CTkLabel(
            toolbar,
            text="Inventario de Productos",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        lbl_title.pack(side="left")

        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Buscar por SKU o nombre...",
            width=260,
            height=34,
            corner_radius=6,
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#CBD5E1", "#475569")
        )
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

    def _build_content(self) -> None:
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # 1. Tabla Treeview híbrida
        self.table = CTkThemedTreeview(
            self.content_container,
            columns=("sku", "name", "category", "price")
        )
        self.table.grid(row=0, column=0, sticky="nsew")
        self.table.set_headers({
            "sku": ("SKU", 100),
            "name": ("Nombre de Producto", 260),
            "category": ("Categoría", 140),
            "price": ("Precio Unitario", 120)
        })

        # 2. Empty State
        self.empty_state = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.empty_state.grid(row=0, column=0, sticky="nsew")
        self.empty_state.grid_remove() # Oculto por defecto

        center_empty = ctk.CTkFrame(self.empty_state, fg_color="transparent")
        center_empty.place(relx=0.5, rely=0.5, anchor="center")

        lbl_no_data = ctk.CTkLabel(
            center_empty,
            text="No se encontraron registros",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        lbl_no_data.pack(pady=4)

        lbl_no_desc = ctk.CTkLabel(
            center_empty,
            text="Prueba ajustando el término de búsqueda para ver resultados.",
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color=("#64748B", "#94A3B8")
        )
        lbl_no_desc.pack()

        self._apply_filter("")

    def _on_search_key(self, event: Any) -> None:
        """Debounce de 300 ms en filtrado de teclado (Ley 6)."""
        if self._search_after_id:
            try:
                self.after_cancel(self._search_after_id)
            except Exception:
                pass
        self._search_after_id = self.after(300, self._trigger_filter)

    def _trigger_filter(self) -> None:
        query = self.search_entry.get().strip().lower()
        self._apply_filter(query)

    def _apply_filter(self, query: str) -> None:
        if not query:
            filtered = self._all_records
        else:
            filtered = [
                r for r in self._all_records
                if query in r[0].lower() or query in r[1].lower() or query in r[2].lower()
            ]

        if not filtered:
            self.table.grid_remove()
            self.empty_state.grid()
        else:
            self.empty_state.grid_remove()
            self.table.grid()
            self.table.insert_rows(filtered)


# --- 5. APLICACIÓN PRINCIPAL (BaseAppMVC) ---

class BaseAppMVC(ctk.CTk):
    """Ventana principal que articula el patrón MVC de alto rendimiento."""
    def __init__(self) -> None:
        super().__init__()
        self.title("CustomTkinter MVC Master")
        self.geometry("980x620")
        self.minsize(800, 500)
        self.configure(fg_color=("#F8FAFC", "#0F172A"))

        # Servicios compartidos
        self.state_manager = StateManager()
        self.queue_batcher = UIQueueBatcher(self)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Sidebar
        self._build_sidebar()

        # 2. Router de vistas con tkraise()
        self.views_container = ctk.CTkFrame(self, fg_color="transparent")
        self.views_container.grid(row=0, column=1, sticky="nsew")
        self.views_container.grid_rowconfigure(0, weight=1)
        self.views_container.grid_columnconfigure(0, weight=1)

        self._views: Dict[str, BaseView] = {}
        self._init_views()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155")
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo / Header
        lbl_brand = ctk.CTkLabel(
            self.sidebar,
            text="Control Desk",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        lbl_brand.pack(anchor="w", padx=20, pady=(24, 16))

        # Botón navegación
        self.btn_nav_catalog = ctk.CTkButton(
            self.sidebar,
            text="Catálogo",
            height=38,
            corner_radius=6,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#F1F5F9", "#334155"),
            text_color=("#2563EB", "#3B82F6"),
            command=lambda: self.show_view("catalog")
        )
        self.btn_nav_catalog.pack(fill="x", padx=12, pady=4)

        # Footer / Selector de apariencia
        opt_theme = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Dark", "Light", "System"],
            command=self._change_theme,
            height=32,
            corner_radius=6,
            fg_color=("#F1F5F9", "#334155"),
            button_color=("#E2E8F0", "#475569"),
            text_color=("#0F172A", "#F8FAFC")
        )
        opt_theme.set(ctk.get_appearance_mode())
        opt_theme.pack(side="bottom", fill="x", padx=12, pady=16)

    def _init_views(self) -> None:
        catalog = TableCatalogView(self.views_container)
        self._views["catalog"] = catalog
        catalog.grid(row=0, column=0, sticky="nsew")
        self.show_view("catalog")

    def show_view(self, key: str) -> None:
        """Navegación instantánea en el eje Z sin recálculos de geometría."""
        if key in self._views:
            view = self._views[key]
            view.tkraise()
            view.on_show()

    def _change_theme(self, mode: str) -> None:
        ctk.set_appearance_mode(mode)
        # Sincronizar Treeviews existentes
        for v in self._views.values():
            if hasattr(v, "table") and hasattr(v.table, "update_theme"):
                v.table.update_theme()

    def _on_close(self) -> None:
        self.queue_batcher.stop()
        self.destroy()


if __name__ == "__main__":
    if "--inspect" in sys.argv:
        # Modo de autoinspección
        from ctk_inspector import CTkInspector
        app = BaseAppMVC()
        inspector = CTkInspector(app)
        app.after(500, lambda: (inspector.run_audit(), app.quit(), app.destroy()))
        app.mainloop()
    else:
        app = BaseAppMVC()
        app.mainloop()
