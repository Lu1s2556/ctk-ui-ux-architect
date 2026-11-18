# Patrones de Layout y Navegación para CustomTkinter
# Compatibilidad estricta: Python 3.8.10+

from __future__ import annotations
import customtkinter as ctk
from typing import Dict, Optional, Any, Callable, List

# --- PATRÓN 1: Sidebar Dashboard + ViewRouter con tkraise() ---

class BaseView(ctk.CTkFrame):
    """
    Clase base para vistas apiladas en el router.
    Usa fg_color="transparent" para heredar la elevación sin redibujar Canvas innecesarios.
    """
    def __init__(self, master: Any, view_name: str, **kwargs: Any) -> None:
        super().__init__(master=master, fg_color="transparent", **kwargs)
        self.view_name = view_name

    def on_show(self) -> None:
        """Hook opcional ejecutado al traer la vista al frente."""
        pass

    def on_hide(self) -> None:
        """Hook opcional ejecutado al pasar la vista a segundo plano."""
        pass


class ViewRouter:
    """
    Enrutador de vistas de alta velocidad.
    Apila todas las vistas en la celda row=0, column=0 y las eleva con tkraise()
    evitando recálculos de geometría o memory leaks por destroy/pack_forget continuo.
    """
    def __init__(self, container: ctk.CTkFrame) -> None:
        self.container = container
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self._views: Dict[str, BaseView] = {}
        self._current_view_key: Optional[str] = None

    def register(self, key: str, view: BaseView) -> None:
        self._views[key] = view
        view.grid(row=0, column=0, sticky="nsew")

    def show(self, key: str) -> None:
        if key not in self._views:
            raise KeyError("Vista no registrada: " + str(key))
        if self._current_view_key == key:
            return

        if self._current_view_key and self._current_view_key in self._views:
            self._views[self._current_view_key].on_hide()

        target_view = self._views[key]
        target_view.tkraise()
        target_view.on_show()
        self._current_view_key = key


class NavigationSidebar(ctk.CTkFrame):
    """
    Sidebar fijo de navegación con indicador de estado activo y selector de modo.
    """
    def __init__(
        self,
        master: Any,
        on_navigate: Callable[[str], None],
        width: int = 220,
        **kwargs: Any
    ) -> None:
        super().__init__(
            master=master,
            width=width,
            corner_radius=0,
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            **kwargs
        )
        self.grid_propagate(False)
        self._on_navigate = on_navigate
        self._nav_buttons: Dict[str, ctk.CTkButton] = {}
        self._active_key: Optional[str] = None

        self._build_header()
        self._nav_container = ctk.CTkFrame(self, fg_color="transparent")
        self._nav_container.pack(fill="both", expand=True, padx=12, pady=16)
        self._build_footer()

    def _build_header(self) -> None:
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header_frame.pack(fill="x", padx=16, pady=(16, 0))
        title = ctk.CTkLabel(
            header_frame,
            text="App Manager",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        title.pack(anchor="w")

    def add_item(self, key: str, label: str) -> None:
        btn = ctk.CTkButton(
            self._nav_container,
            text=label,
            anchor="w",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="normal"),
            fg_color="transparent",
            hover_color=("#F1F5F9", "#334155"),
            text_color=("#475569", "#94A3B8"),
            command=lambda k=key: self.select_item(k)
        )
        btn.pack(fill="x", pady=4)
        self._nav_buttons[key] = btn

    def select_item(self, key: str) -> None:
        if self._active_key == key:
            return
        # Desactivar anterior
        if self._active_key and self._active_key in self._nav_buttons:
            self._nav_buttons[self._active_key].configure(
                fg_color="transparent",
                font=ctk.CTkFont(size=13, weight="normal"),
                text_color=("#475569", "#94A3B8")
            )
        # Activar nuevo
        if key in self._nav_buttons:
            self._nav_buttons[key].configure(
                fg_color=("#F1F5F9", "#334155"),
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#2563EB", "#3B82F6")
            )
            self._active_key = key
            self._on_navigate(key)

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=12, pady=16, side="bottom")
        theme_menu = ctk.CTkOptionMenu(
            footer,
            values=["System", "Light", "Dark"],
            command=self._change_appearance,
            height=32,
            corner_radius=6,
            fg_color=("#F1F5F9", "#334155"),
            button_color=("#E2E8F0", "#475569"),
            text_color=("#0F172A", "#F8FAFC")
        )
        theme_menu.set(ctk.get_appearance_mode())
        theme_menu.pack(fill="x")

    def _change_appearance(self, mode: str) -> None:
        ctk.set_appearance_mode(mode)


# --- PATRÓN 2: Card Grid Responsivo ---

class ResponsiveCardGrid(ctk.CTkFrame):
    """
    Contenedor de tarjetas en cuadrícula de columnas uniformes.
    """
    def __init__(self, master: Any, columns: int = 3, **kwargs: Any) -> None:
        super().__init__(master=master, fg_color="transparent", **kwargs)
        self.columns = columns
        for col_idx in range(columns):
            self.grid_columnconfigure(col_idx, weight=1, uniform="grid_cols")

    def place_card(self, widget: ctk.CTkFrame, index: int, padx: int = 8, pady: int = 8) -> None:
        row = index // self.columns
        col = index % self.columns
        widget.grid(row=row, column=col, padx=padx, pady=pady, sticky="nsew")


# --- PATRÓN 3: Vista Maestro-Detalle Quirúrgica ---

class MasterDetailView(BaseView):
    """
    Patrón Maestro-Detalle: Al hacer clic en un registro del panel izquierdo,
    se actualiza el detalle existente usando .configure(). Nunca se destruye el panel derecho.
    """
    def __init__(self, master: Any, **kwargs: Any) -> None:
        super().__init__(master=master, view_name="master_detail", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Panel Maestro (Lista o controles)
        self.master_panel = ctk.CTkFrame(
            self,
            fg_color=("#FFFFFF", "#1E293B"),
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155")
        )
        self.master_panel.grid(row=0, column=0, padx=(16, 8), pady=16, sticky="nsew")

        # Panel Detalle
        self.detail_container = ctk.CTkFrame(
            self,
            fg_color=("#FFFFFF", "#1E293B"),
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155")
        )
        self.detail_container.grid(row=0, column=1, padx=(8, 16), pady=16, sticky="nsew")
        self.detail_container.grid_rowconfigure(0, weight=1)
        self.detail_container.grid_columnconfigure(0, weight=1)

        # Estados del Detalle: Empty State y Panel Activo
        self.empty_state = EmptyState(
            self.detail_container,
            title="Sin selección",
            description="Selecciona un registro de la lista izquierda para visualizar su detalle."
        )
        self.empty_state.grid(row=0, column=0, sticky="nsew")

        self.detail_content = ctk.CTkFrame(self.detail_container, fg_color="transparent")
        self.detail_content.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        self.detail_content.grid_remove() # Oculto por defecto

        self._build_detail_widgets()

    def _build_detail_widgets(self) -> None:
        self.lbl_title = ctk.CTkLabel(
            self.detail_content,
            text="",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        self.lbl_title.pack(anchor="w", pady=(0, 8))

        self.lbl_meta = ctk.CTkLabel(
            self.detail_content,
            text="",
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color=("#64748B", "#94A3B8")
        )
        self.lbl_meta.pack(anchor="w", pady=(0, 16))

        self.txt_body = ctk.CTkTextbox(
            self.detail_content,
            height=200,
            corner_radius=8,
            fg_color=("#F1F5F9", "#334155"),
            border_width=1,
            border_color=("#CBD5E1", "#475569")
        )
        self.txt_body.pack(fill="both", expand=True)

    def load_record(self, data: Optional[Dict[str, str]]) -> None:
        """Actualización quirúrgica de valores sin reconstruir widgets Tk."""
        if not data:
            self.detail_content.grid_remove()
            self.empty_state.grid()
            return

        self.empty_state.grid_remove()
        self.detail_content.grid()

        self.lbl_title.configure(text=data.get("title", ""))
        self.lbl_meta.configure(text="ID: " + str(data.get("id", "")) + " | Categoría: " + str(data.get("category", "")))
        self.txt_body.delete("1.0", "end")
        self.txt_body.insert("1.0", data.get("content", ""))


# --- PATRÓN 4: EmptyState Reutilizable ---

class EmptyState(ctk.CTkFrame):
    """
    Componente amigable para estados vacíos.
    Se oculta con grid_remove() para recordar geometría al recibir nuevos datos.
    """
    def __init__(
        self,
        master: Any,
        title: str = "No hay datos para mostrar",
        description: str = "Cuando agregues o filtres elementos aparecerán aquí.",
        action_label: Optional[str] = None,
        on_action: Optional[Callable[[], None]] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(master=master, fg_color="transparent", **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        center_box = ctk.CTkFrame(self, fg_color="transparent")
        center_box.grid(row=0, column=0, padx=20, pady=20)

        self.lbl_title = ctk.CTkLabel(
            center_box,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        self.lbl_title.pack(pady=(0, 6))

        self.lbl_desc = ctk.CTkLabel(
            center_box,
            text=description,
            font=ctk.CTkFont(size=13, weight="normal"),
            text_color=("#64748B", "#94A3B8"),
            wraplength=320
        )
        self.lbl_desc.pack(pady=(0, 16))

        if action_label and on_action:
            self.btn_action = ctk.CTkButton(
                center_box,
                text=action_label,
                command=on_action,
                corner_radius=6,
                fg_color=("#2563EB", "#3B82F6"),
                hover_color=("#1D4ED8", "#2563EB"),
                text_color=("#FFFFFF", "#FFFFFF")
            )
            self.btn_action.pack()
