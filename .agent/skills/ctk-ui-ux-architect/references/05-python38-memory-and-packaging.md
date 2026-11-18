# Gestión de Memoria, Ciclo de Vida y Empaquetado en Python 3.8.10+
# Compatibilidad estricta: Python 3.8.10+

from __future__ import annotations
import os
import sys
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageDraw
from typing import Dict, Tuple, Optional, Any, Callable, List

# --- 1. Gestor de Imágenes Seguro (ImageCache Singleton) ---

class ImageCache:
    """
    Singleton para retener referencias duras de CTkImage en memoria.
    Resuelve el problema silencioso del Garbage Collector de Python 3.8 que borra
    imágenes locales dejando widgets vacíos. Incluye generador de respaldo con PIL.
    """
    _instance: Optional[ImageCache] = None
    _cache: Dict[str, ctk.CTkImage] = {}

    def __new__(cls) -> ImageCache:
        if cls._instance is None:
            cls._instance = super(ImageCache, cls).__new__(cls)
            cls._cache = {}
        return cls._instance

    @classmethod
    def get(
        cls,
        key: str,
        light_path: Optional[str] = None,
        dark_path: Optional[str] = None,
        size: Tuple[int, int] = (20, 20)
    ) -> ctk.CTkImage:
        """Obtiene o crea un CTkImage almacenado de forma persistente."""
        cache_key = str(key) + "_" + str(size[0]) + "x" + str(size[1])
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        img_light = cls._load_pil_or_fallback(light_path, size, is_dark=False)
        img_dark = cls._load_pil_or_fallback(dark_path or light_path, size, is_dark=True)

        ctk_img = ctk.CTkImage(light_image=img_light, dark_image=img_dark, size=size)
        cls._cache[cache_key] = ctk_img
        return ctk_img

    @staticmethod
    def _load_pil_or_fallback(path: Optional[str], size: Tuple[int, int], is_dark: bool) -> Image.Image:
        if path and os.path.exists(path):
            try:
                return Image.open(path).convert("RGBA")
            except Exception:
                pass

        # Generador de icono de respaldo sintético si no existe el archivo físico
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        fill_color = (248, 250, 252, 220) if is_dark else (15, 23, 42, 220)
        margin = max(1, size[0] // 6)
        draw.rounded_rectangle(
            [margin, margin, size[0] - margin, size[1] - margin],
            radius=max(2, size[0] // 5),
            fill=fill_color
        )
        return img


# --- 2. Gestor de Ventanas Modales Seguro (SafeModalToplevel) ---

class SafeModalToplevel(ctk.CTkToplevel):
    """
    Solución definitiva al bug de CTkToplevel + CTkScrollableFrame.
    Destruir (.destroy()) un modal con scrollable frame corrompe el estado interno
    de CTk haciendo que el siguiente modal tarde de 4 a 15 segundos en crearse.
    Esta clase intercepta el cierre, reutiliza la instancia y alterna con withdraw()/deiconify().
    """
    def __init__(self, master: Any, title: str = "Modal", width: int = 500, height: int = 400, **kwargs: Any) -> None:
        super().__init__(master=master, **kwargs)
        self.title(title)
        self.geometry(str(width) + "x" + str(height))
        self.resizable(False, False)

        # Ocultar inicialmente
        self.withdraw()

        # Interceptar el botón [X] de la ventana
        self.protocol("WM_DELETE_WINDOW", self.hide)

        # Contenedor principal del modal
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#F8FAFC", "#0F172A"))
        self.content_frame.pack(fill="both", expand=True)

    def show(self) -> None:
        """Muestra el modal y toma foco modal de forma segura."""
        self.deiconify()
        self.lift()
        self.focus_force()
        try:
            self.grab_set()
        except Exception:
            pass

    def hide(self) -> None:
        """Oculta el modal sin destruir sus widgets ni canvas."""
        try:
            self.grab_release()
        except Exception:
            pass
        self.withdraw()


# --- 3. Limpieza de Variables Tk (CleanableWidgetMixin) ---

class CleanableWidgetMixin:
    """
    Mixin para registrar traces en StringVar / IntVar y asegurar su desvinculación
    automática en el evento <Destroy>, previniendo memory leaks por callbacks fantasma.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs) # type: ignore
        self._tracked_traces: List[Tuple[tk.Variable, str, str]] = []
        if hasattr(self, "bind"):
            self.bind("<Destroy>", self._cleanup_traces_on_destroy, add="+")

    def track_trace(self, var: tk.Variable, mode: str, callback: Callable[..., Any]) -> str:
        """Registra un trace y almacena su ID para limpieza garantizada."""
        trace_id = var.trace_add(mode, callback)
        self._tracked_traces.append((var, mode, trace_id))
        return trace_id

    def _cleanup_traces_on_destroy(self, event: Any) -> None:
        if hasattr(self, "winfo_exists") and not self.winfo_exists():
            for var, mode, trace_id in self._tracked_traces:
                try:
                    var.trace_remove(mode, trace_id)
                except Exception:
                    pass
            self._tracked_traces.clear()


# --- 4. Empaquetado con PyInstaller y Rutas de Recursos ---

def resource_path(relative_path: str) -> str:
    """
    Resuelve la ruta absoluta hacia recursos incluidos con PyInstaller (--onefile).
    Busca en sys._MEIPASS si está congelado en ejecutable, o en el directorio base del proyecto.
    """
    try:
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Comando de compilación PyInstaller recomendado para CustomTkinter:
# pyinstaller --noconsole --onefile --collect-all customtkinter main.py
