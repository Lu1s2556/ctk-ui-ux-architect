# Componentes Esenciales de Micro-UX para CustomTkinter
# Compatibilidad estricta: Python 3.8.10+

from __future__ import annotations
import threading
import customtkinter as ctk
from typing import Optional, Callable, Any, Tuple


class ValidatedEntry(ctk.CTkFrame):
    """
    Entrada con validación en vivo y cero salto de layout (Zero Layout Shift).
    Reserva un espacio fijo de 16 px para el mensaje de error desde la inicialización.
    """
    def __init__(
        self,
        master: Any,
        label_text: str = "",
        placeholder_text: str = "",
        width: int = 240,
        height: int = 36,
        is_password: bool = False,
        **kwargs: Any
    ) -> None:
        super().__init__(master=master, fg_color="transparent", **kwargs)
        self._normal_border: Tuple[str, str] = ("#CBD5E1", "#475569")
        self._error_border: Tuple[str, str] = ("#DC2626", "#EF4444")

        # 1. Label superior descriptivo
        if label_text:
            self.lbl_title = ctk.CTkLabel(
                self,
                text=label_text,
                font=ctk.CTkFont(size=12, weight="normal"),
                text_color=("#475569", "#94A3B8"),
                anchor="w"
            )
            self.lbl_title.pack(fill="x", pady=(0, 4))

        # 2. Input CTkEntry
        self.entry = ctk.CTkEntry(
            self,
            width=width,
            height=height,
            placeholder_text=placeholder_text,
            show="*" if is_password else "",
            corner_radius=6,
            fg_color=("#F1F5F9", "#334155"),
            border_width=1,
            border_color=self._normal_border,
            text_color=("#0F172A", "#F8FAFC")
        )
        self.entry.pack(fill="x")

        # 3. Label inferior de error con altura fija preasignada (evita layout shift)
        self.lbl_error = ctk.CTkLabel(
            self,
            text="",
            height=16,
            font=ctk.CTkFont(size=11, weight="normal"),
            text_color=("#DC2626", "#EF4444"),
            anchor="w"
        )
        self.lbl_error.pack(fill="x", pady=(2, 0))

    def get(self) -> str:
        return self.entry.get()

    def set_text(self, text: str) -> None:
        self.entry.delete(0, "end")
        self.entry.insert(0, text)

    def set_error(self, error_message: Optional[str] = None) -> None:
        """Si error_message es provisto, activa el borde rojo y muestra el motivo."""
        if error_message:
            self.entry.configure(border_color=self._error_border)
            self.lbl_error.configure(text=error_message)
        else:
            self.entry.configure(border_color=self._normal_border)
            self.lbl_error.configure(text="")


class MetricCard(ctk.CTkFrame):
    """
    Tarjeta KPI para dashboards con título secundario, métrica destacada y badge de tendencia.
    """
    def __init__(
        self,
        master: Any,
        title: str,
        value: str,
        trend: str = "",
        is_positive_trend: bool = True,
        width: int = 180,
        height: int = 100,
        **kwargs: Any
    ) -> None:
        super().__init__(
            master=master,
            width=width,
            height=height,
            corner_radius=12,
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
            **kwargs
        )
        self.pack_propagate(False)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=12)

        self.lbl_title = ctk.CTkLabel(
            inner,
            text=title,
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color=("#64748B", "#94A3B8"),
            anchor="w"
        )
        self.lbl_title.pack(fill="x")

        bottom_row = ctk.CTkFrame(inner, fg_color="transparent")
        bottom_row.pack(fill="x", expand=True, side="bottom")

        self.lbl_value = ctk.CTkLabel(
            bottom_row,
            text=value,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w"
        )
        self.lbl_value.pack(side="left")

        trend_color = ("#16A34A", "#22C55E") if is_positive_trend else ("#DC2626", "#EF4444")
        self.lbl_trend = ctk.CTkLabel(
            bottom_row,
            text=trend,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=trend_color,
            anchor="e"
        )
        if trend:
            self.lbl_trend.pack(side="right")

    def update_metric(self, value: str, trend: Optional[str] = None, is_positive: Optional[bool] = None) -> None:
        self.lbl_value.configure(text=value)
        if trend is not None:
            self.lbl_trend.configure(text=trend)
            if is_positive is not None:
                color = ("#16A34A", "#22C55E") if is_positive else ("#DC2626", "#EF4444")
                self.lbl_trend.configure(text_color=color)


class ToastNotification(ctk.CTkFrame):
    """
    Notificación flotante no bloqueante posicionada con .place(relx=0.98, rely=0.96, anchor='se').
    Ajusta bg_color con el color del padre para evitar artefactos en esquinas redondeadas.
    """
    def __init__(
        self,
        master: Any,
        message: str,
        duration_ms: int = 3500,
        is_error: bool = False,
        **kwargs: Any
    ) -> None:
        # Detectar el color del contenedor padre para evitar el artefacto de esquinas de CTk
        parent_bg = "transparent"
        if hasattr(master, "cget"):
            try:
                parent_bg = master.cget("fg_color")
            except Exception:
                pass

        card_bg = ("#DC2626", "#991B1B") if is_error else ("#0F172A", "#1E293B")
        super().__init__(
            master=master,
            corner_radius=8,
            fg_color=card_bg,
            bg_color=parent_bg,
            border_width=1,
            border_color=("#334155", "#475569"),
            **kwargs
        )
        self.duration_ms = duration_ms

        lbl = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="#FFFFFF",
            padx=16,
            pady=10
        )
        lbl.pack()

        # Posicionamiento en esquina inferior derecha
        self.place(relx=0.98, rely=0.96, anchor="se")
        self.lift()
        self.after(self.duration_ms, self._dismiss)

    def _dismiss(self) -> None:
        try:
            self.destroy()
        except Exception:
            pass


class AsyncActionButton(ctk.CTkButton):
    """
    Botón reactivo que brinda feedback visual inmediato al iniciar una tarea asíncrona.
    Cambia a 'Procesando...', desactiva clics repetidos y se restaura al finalizar.
    Permite opcionalmente inyectar un `UIQueueBatcher` para cumplir estrictamente con el rate limit.
    """
    def __init__(
        self,
        master: Any,
        text: str,
        async_worker: Callable[[], Any],
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        loading_text: str = "Procesando...",
        queue_batcher: Optional[Any] = None,
        **kwargs: Any
    ) -> None:
        self._original_text = text
        self._loading_text = loading_text
        self._async_worker = async_worker
        self._on_success_cb = on_success
        self._on_error_cb = on_error
        self._queue_batcher = queue_batcher

        super().__init__(
            master=master,
            text=text,
            command=self._handle_click,
            corner_radius=6,
            fg_color=("#2563EB", "#3B82F6"),
            hover_color=("#1D4ED8", "#2563EB"),
            text_color=("#FFFFFF", "#FFFFFF"),
            **kwargs
        )

    def _dispatch_ui(self, fn: Callable[..., Any], *args: Any) -> None:
        if self._queue_batcher is not None and hasattr(self._queue_batcher, "post"):
            self._queue_batcher.post(fn, *args)
        else:
            self.after(0, lambda: fn(*args))

    def _handle_click(self) -> None:
        self.configure(state="disabled", text=self._loading_text)

        def _worker_thread() -> None:
            try:
                result = self._async_worker()
                self._dispatch_ui(self._on_complete, result, None)
            except Exception as exc:
                self._dispatch_ui(self._on_complete, None, exc)

        threading.Thread(target=_worker_thread, daemon=True).start()

    def _on_complete(self, result: Any, error: Optional[Exception]) -> None:
        self.configure(state="normal", text=self._original_text)
        if error is not None:
            if self._on_error_cb:
                self._on_error_cb(error)
        else:
            if self._on_success_cb:
                self._on_success_cb(result)
