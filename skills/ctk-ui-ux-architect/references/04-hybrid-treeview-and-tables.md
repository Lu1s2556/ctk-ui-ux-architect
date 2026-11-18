# Tablas Densas e Híbridas con CustomTkinter y ttk.Treeview
# Compatibilidad estricta: Python 3.8.10+

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import List, Tuple, Dict, Any, Optional, Union

class CTkThemedTreeview(ctk.CTkFrame):
    """
    Componente híbrido de alto rendimiento para renderizar de 50 a 50.000 filas.
    Envuelve ttk.Treeview estilizado con tema 'clam' integrado armónicamente
    con la paleta de colores adaptativa y el escalado de CustomTkinter.
    """
    def __init__(
        self,
        master: Any,
        columns: Tuple[str, ...],
        show: str = "headings",
        height: int = 15,
        **kwargs: Any
    ) -> None:
        # Contenedor Nivel 1 con bordes suaves
        super().__init__(
            master=master,
            corner_radius=8,
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            **kwargs
        )
        self.columns = columns
        self.show = show
        self._tree_height = height

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._style = ttk.Style()
        self._setup_style()

        # Instanciar Treeview nativo dentro del contenedor CTk
        self.tree = ttk.Treeview(
            self,
            columns=self.columns,
            show=self.show,
            height=self._tree_height,
            style="CTkHybrid.Treeview",
            selectmode="extended"
        )
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(2, 0), pady=2)

        # Scrollbar vertical de CustomTkinter
        self.vsb = ctk.CTkScrollbar(
            self,
            orientation="vertical",
            command=self.tree.yview,
            width=14,
            corner_radius=4
        )
        self.vsb.grid(row=0, column=1, sticky="ns", padx=(0, 2), pady=2)
        self.tree.configure(yscrollcommand=self.vsb.set)

        # Scrollbar horizontal de CustomTkinter
        self.hsb = ctk.CTkScrollbar(
            self,
            orientation="horizontal",
            command=self.tree.xview,
            height=14,
            corner_radius=4
        )
        self.hsb.grid(row=1, column=0, sticky="ew", padx=(2, 0), pady=(0, 2))
        self.tree.configure(xscrollcommand=self.hsb.set)

        self.update_theme_colors()

    def _setup_style(self) -> None:
        """Configura el motor de estilos usando 'clam' como base neutral."""
        available_themes = self._style.theme_names()
        if "clam" in available_themes:
            self._style.theme_use("clam")

    def update_theme_colors(self) -> None:
        """
        Sincroniza dinámicamente los estilos del Treeview con el modo de apariencia
        actual (Light/Dark) y el factor de escala DPI de CustomTkinter.
        """
        mode = ctk.get_appearance_mode().lower()
        is_dark = (mode == "dark")

        # Escalar altura de fila según DPI
        try:
            scaling = self._get_widget_scaling()
        except Exception:
            scaling = 1.0
        row_height = max(26, int(32 * scaling))

        # Colores adaptativos
        bg_surface = "#1E293B" if is_dark else "#FFFFFF"
        bg_row_alt = "#243247" if is_dark else "#F8FAFC"
        bg_header = "#0F172A" if is_dark else "#F1F5F9"
        fg_text = "#F8FAFC" if is_dark else "#0F172A"
        fg_header = "#94A3B8" if is_dark else "#475569"
        border_color = "#334155" if is_dark else "#E2E8F0"
        select_color = "#3B82F6" if is_dark else "#2563EB"

        # Aplicar estilo al Treeview principal
        self._style.configure(
            "CTkHybrid.Treeview",
            background=bg_surface,
            fieldbackground=bg_surface,
            foreground=fg_text,
            borderwidth=0,
            rowheight=row_height,
            font=("Segoe UI", int(10 * scaling))
        )
        self._style.map(
            "CTkHybrid.Treeview",
            background=[("selected", select_color)],
            foreground=[("selected", "#FFFFFF")]
        )

        # Aplicar estilo a las cabeceras
        self._style.configure(
            "CTkHybrid.Treeview.Heading",
            background=bg_header,
            foreground=fg_header,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", int(10 * scaling), "bold")
        )
        self._style.map(
            "CTkHybrid.Treeview.Heading",
            background=[("active", border_color)],
            foreground=[("active", fg_text)]
        )

        # Configurar tags de filas alternas (zebra striping)
        self.tree.tag_configure("evenrow", background=bg_surface, foreground=fg_text)
        self.tree.tag_configure("oddrow", background=bg_row_alt, foreground=fg_text)

    def set_headers(self, headers_dict: Dict[str, Tuple[str, int, str]]) -> None:
        """
        Configura texto, ancho y alineación de cada columna.
        Estructura de headers_dict: {col_id: (header_text, width_px, anchor_alignment)}
        """
        for col_id, (header_text, width, anchor) in headers_dict.items():
            self.tree.heading(col_id, text=header_text, anchor=anchor)
            self.tree.column(col_id, width=width, minsize=40, anchor=anchor)

    def insert_batch(self, rows_data: List[Union[List[Any], Tuple[Any, ...]]], clear_first: bool = False) -> None:
        """
        Inserta un lote grande de registros aplicando zebra striping instantáneo.
        A diferencia de crear cientos de Canvas en CTk, ttk.Treeview puede insertar
        10.000 filas en menos de 100 ms.
        """
        if clear_first:
            self.clear()

        current_count = len(self.tree.get_children())
        for idx, row in enumerate(rows_data):
            row_idx = current_count + idx
            tag = "evenrow" if (row_idx % 2 == 0) else "oddrow"
            self.tree.insert("", "end", values=row, tags=(tag,))

    def clear(self) -> None:
        """Elimina todos los elementos del Treeview de forma instantánea."""
        items = self.tree.get_children()
        if items:
            self.tree.delete(*items)

    def get_selected_rows(self) -> List[Tuple[Any, ...]]:
        """Retorna los valores de las filas seleccionadas actualmente."""
        selected_ids = self.tree.selection()
        return [self.tree.item(item_id, "values") for item_id in selected_ids]
