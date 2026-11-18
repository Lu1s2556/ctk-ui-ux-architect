# Tokens de Diseño y Superficies para CustomTkinter
# Compatibilidad estricta: Python 3.8.10+

from __future__ import annotations
import customtkinter as ctk
from typing import Tuple, Optional, Callable, Any, Union

ColorType = Tuple[str, str]

class DesignTokens:
    """
    Sistema unificado de tokens de diseño para CustomTkinter.
    Todos los colores se estructuran en tuplas adaptativas (Modo Claro, Modo Oscuro).
    """

    # --- Paleta de Superficies y Elevación (Ley 8) ---
    BG_ROOT: ColorType = ("#F8FAFC", "#0F172A")       # Nivel 0: Fondo base de la ventana
    BG_SURFACE: ColorType = ("#FFFFFF", "#1E293B")    # Nivel 1: Tarjetas, Sidebars, Contenedores principales
    BG_ELEVATED: ColorType = ("#F1F5F9", "#334155")   # Nivel 2: Inputs, Hover de tarjetas, Paneles flotantes

    # --- Bordes y Separadores ---
    BORDER_SUBTLE: ColorType = ("#E2E8F0", "#334155") # Bordes estándar para superficie nivel 1
    BORDER_FOCUS: ColorType = ("#2563EB", "#3B82F6")  # Borde activo de campos interactivos
    BORDER_DANGER: ColorType = ("#DC2626", "#EF4444") # Borde para campos con error de validación

    # --- Jerarquía de Texto ---
    TEXT_PRIMARY: ColorType = ("#0F172A", "#F8FAFC")   # Títulos y texto de alto contraste
    TEXT_SECONDARY: ColorType = ("#475569", "#94A3B8") # Subtítulos y descripciones
    TEXT_MUTED: ColorType = ("#94A3B8", "#64748B")     # Placeholders y metadatos secundarios
    TEXT_INVERTED: ColorType = ("#FFFFFF", "#FFFFFF")  # Texto sobre acentos sólidos

    # --- Colores de Acento e Interacción ---
    ACCENT_PRIMARY: ColorType = ("#2563EB", "#3B82F6") # Botones de acción primaria y selección
    ACCENT_HOVER: ColorType = ("#1D4ED8", "#2563EB")   # Estado hover para acción primaria
    ACCENT_GHOST_BORDER: ColorType = ("#CBD5E1", "#475569")
    ACCENT_GHOST_HOVER: ColorType = ("#F1F5F9", "#334155")

    # --- Estados Semánticos ---
    STATUS_SUCCESS: ColorType = ("#16A34A", "#22C55E")
    STATUS_WARNING: ColorType = ("#D97706", "#F59E0B")
    STATUS_DANGER: ColorType = ("#DC2626", "#EF4444")
    STATUS_DANGER_HOVER: ColorType = ("#B91C1C", "#DC2626")

    # --- Escala de Espaciado Espacial (Ley 9: Múltiplos de 4/8 px) ---
    SPACE_XS: int = 4
    SPACE_SM: int = 8
    SPACE_MD: int = 12
    SPACE_LG: int = 16
    SPACE_XL: int = 24
    SPACE_2XL: int = 32

    # --- Radios Base ---
    RADIUS_CARD: int = 12
    RADIUS_CONTROL: int = 6
    RADIUS_PILL: int = 9999

    # --- Tipografías (Inicializadas tras instanciar la raíz Tk) ---
    _font_h1: Optional[ctk.CTkFont] = None
    _font_h2: Optional[ctk.CTkFont] = None
    _font_h3: Optional[ctk.CTkFont] = None
    _font_body: Optional[ctk.CTkFont] = None
    _font_body_bold: Optional[ctk.CTkFont] = None
    _font_meta: Optional[ctk.CTkFont] = None
    _font_mono: Optional[ctk.CTkFont] = None

    @classmethod
    def initialize_fonts(cls) -> None:
        """Inicializa las instancias de CTkFont una vez que la ventana raíz ha sido creada."""
        cls._font_h1 = ctk.CTkFont(size=24, weight="bold")
        cls._font_h2 = ctk.CTkFont(size=18, weight="bold")
        cls._font_h3 = ctk.CTkFont(size=15, weight="bold")
        cls._font_body = ctk.CTkFont(size=13, weight="normal")
        cls._font_body_bold = ctk.CTkFont(size=13, weight="bold")
        cls._font_meta = ctk.CTkFont(size=11, weight="normal")
        cls._font_mono = ctk.CTkFont(family="Consolas", size=12, weight="normal")

    @classmethod
    def FONT_H1(cls) -> ctk.CTkFont:
        if cls._font_h1 is None:
            cls.initialize_fonts()
        return cls._font_h1  # type: ignore

    @classmethod
    def FONT_H2(cls) -> ctk.CTkFont:
        if cls._font_h2 is None:
            cls.initialize_fonts()
        return cls._font_h2  # type: ignore

    @classmethod
    def FONT_H3(cls) -> ctk.CTkFont:
        if cls._font_h3 is None:
            cls.initialize_fonts()
        return cls._font_h3  # type: ignore

    @classmethod
    def FONT_BODY(cls) -> ctk.CTkFont:
        if cls._font_body is None:
            cls.initialize_fonts()
        return cls._font_body  # type: ignore

    @classmethod
    def FONT_BODY_BOLD(cls) -> ctk.CTkFont:
        if cls._font_body_bold is None:
            cls.initialize_fonts()
        return cls._font_body_bold  # type: ignore

    @classmethod
    def FONT_META(cls) -> ctk.CTkFont:
        if cls._font_meta is None:
            cls.initialize_fonts()
        return cls._font_meta  # type: ignore

    @classmethod
    def FONT_MONO(cls) -> ctk.CTkFont:
        if cls._font_mono is None:
            cls.initialize_fonts()
        return cls._font_mono  # type: ignore


def concentric_radius(parent_radius: int, padding: int) -> int:
    """
    Calcula el radio visualmente armónico para un widget hijo dentro de un contenedor.
    Fórmula: R_hijo = max(4, R_padre - P)
    """
    return max(4, parent_radius - padding)


def create_primary_button(
    master: Any,
    text: str,
    command: Optional[Callable[[], None]] = None,
    width: int = 140,
    height: int = 36,
    corner_radius: int = DesignTokens.RADIUS_CONTROL,
    **kwargs: Any
) -> ctk.CTkButton:
    """Fábrica de botones para acciones primarias (Call to Action principal)."""
    return ctk.CTkButton(
        master=master,
        text=text,
        command=command,
        width=width,
        height=height,
        corner_radius=corner_radius,
        font=DesignTokens.FONT_BODY_BOLD(),
        fg_color=DesignTokens.ACCENT_PRIMARY,
        hover_color=DesignTokens.ACCENT_HOVER,
        text_color=DesignTokens.TEXT_INVERTED,
        **kwargs
    )


def create_ghost_button(
    master: Any,
    text: str,
    command: Optional[Callable[[], None]] = None,
    width: int = 140,
    height: int = 36,
    corner_radius: int = DesignTokens.RADIUS_CONTROL,
    **kwargs: Any
) -> ctk.CTkButton:
    """Fábrica de botones secundarios estilo Ghost con borde sutil."""
    return ctk.CTkButton(
        master=master,
        text=text,
        command=command,
        width=width,
        height=height,
        corner_radius=corner_radius,
        font=DesignTokens.FONT_BODY(),
        fg_color="transparent",
        hover_color=DesignTokens.ACCENT_GHOST_HOVER,
        text_color=DesignTokens.TEXT_PRIMARY,
        border_width=1,
        border_color=DesignTokens.ACCENT_GHOST_BORDER,
        **kwargs
    )


def create_danger_button(
    master: Any,
    text: str,
    command: Optional[Callable[[], None]] = None,
    width: int = 140,
    height: int = 36,
    corner_radius: int = DesignTokens.RADIUS_CONTROL,
    **kwargs: Any
) -> ctk.CTkButton:
    """Fábrica de botones para acciones irreversibles o destructivas."""
    return ctk.CTkButton(
        master=master,
        text=text,
        command=command,
        width=width,
        height=height,
        corner_radius=corner_radius,
        font=DesignTokens.FONT_BODY_BOLD(),
        fg_color=DesignTokens.STATUS_DANGER,
        hover_color=DesignTokens.STATUS_DANGER_HOVER,
        text_color=DesignTokens.TEXT_INVERTED,
        **kwargs
    )
