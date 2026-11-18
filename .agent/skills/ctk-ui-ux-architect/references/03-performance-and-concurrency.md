# Rendimiento y Concurrencia Segura en CustomTkinter
# Compatibilidad estricta: Python 3.8.10+

from __future__ import annotations
import queue
import threading
import time
import customtkinter as ctk
from typing import Callable, Any, List, Dict, Optional, Tuple

# --- 1. UIQueueBatcher: Concurrencia y Batching Seguro en Tkinter ---

class UIQueueBatcher:
    """
    Despacha tareas desde hilos secundarios al hilo principal agrupando en lotes.
    Procesa un máximo de `max_batch_size` elementos cada `interval_ms` para evitar
    saturar el bucle de eventos Tcl/Tk y el renderizado en CPU.
    """
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
                # Mantener robustez ante excepciones de UI en callbacks
                print("Error ejecutando callback en UIQueueBatcher:", str(e))
            finally:
                self._queue.task_done()
                processed += 1

        self._schedule_poll()

    def post(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Encola una función para ejecutarse de forma segura en el hilo principal."""
        self._queue.put((fn, args, kwargs))

    def run_async(
        self,
        worker_fn: Callable[..., Any],
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_progress: Optional[Callable[[Any], None]] = None
    ) -> threading.Thread:
        """
        Ejecuta `worker_fn` en un hilo daemon.
        Permite enviar reportes de progreso usando el callback seguro provisto al worker.
        """
        def _worker_wrapper() -> None:
            def _safe_progress(data: Any) -> None:
                if on_progress:
                    self.post(on_progress, data)

            try:
                # Comprobar si worker_fn acepta el parámetro report_progress
                try:
                    result = worker_fn(report_progress=_safe_progress)
                except TypeError:
                    result = worker_fn()

                if on_success:
                    self.post(on_success, result)
            except Exception as exc:
                if on_error:
                    self.post(on_error, exc)
                else:
                    print("Error no capturado en hilo de worker_fn:", str(exc))

        thread = threading.Thread(target=_worker_wrapper, daemon=True)
        thread.start()
        return thread

    def stop(self) -> None:
        self._running = False


# --- 2. SharedStateSnapshot: Estado Compartido Protegido y Render Diferencial ---

class SharedStateSnapshot:
    """
    Estructura thread-safe para productores de alta frecuencia (ej. telemetría, contadores).
    La UI consulta periódicamente y solo redibuja si los valores cambiaron.
    """
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state: Dict[str, Any] = {}
        self._last_rendered_state: Dict[str, Any] = {}

    def update(self, key: str, value: Any) -> None:
        """Llamado desde hilos secundarios."""
        with self._lock:
            self._state[key] = value

    def update_many(self, values: Dict[str, Any]) -> None:
        """Actualización múltiple atómica."""
        with self._lock:
            self._state.update(values)

    def get_diff(self) -> Dict[str, Any]:
        """
        Llamado desde el hilo principal de la UI.
        Retorna únicamente los pares (clave, valor) que han cambiado desde la última llamada.
        """
        with self._lock:
            current_copy = dict(self._state)

        diff: Dict[str, Any] = {}
        for k, v in current_copy.items():
            if k not in self._last_rendered_state or self._last_rendered_state[k] != v:
                diff[k] = v
                self._last_rendered_state[k] = v

        return diff


# --- 3. TimeSlicedBuilder: Renderizado Progresivo en Franjas de 12 ms ---

class TimeSlicedBuilder:
    """
    Construye una colección visual dividiendo la carga de CPU en franjas que no superan 12 ms.
    Garantiza que la UI responda de inmediato mostrando los primeros 6 ítems sin congelación.
    """
    def __init__(
        self,
        container: ctk.CTkFrame,
        items: List[Any],
        item_factory: Callable[[ctk.CTkFrame, Any, int], ctk.CTkFrame],
        initial_sync_count: int = 6,
        max_slice_ms: float = 12.0,
        interval_ms: int = 15,
        on_complete: Optional[Callable[[], None]] = None
    ) -> None:
        self.container = container
        self.items = items
        self.item_factory = item_factory
        self.initial_sync_count = initial_sync_count
        self.max_slice_ms = max_slice_ms / 1000.0  # a segundos
        self.interval_ms = interval_ms
        self.on_complete = on_complete

        self._current_index = 0
        self._total = len(items)
        self._is_cancelled = False
        self._after_id: Optional[str] = None

    def start(self) -> None:
        # 1. Renderizar de forma inmediata los primeros elementos para feedback visual instantáneo
        sync_limit = min(self.initial_sync_count, self._total)
        while self._current_index < sync_limit:
            self.item_factory(self.container, self.items[self._current_index], self._current_index)
            self._current_index += 1

        # 2. Encolar el resto con time-slicing
        if self._current_index < self._total:
            self._schedule_next_slice()
        else:
            if self.on_complete:
                self.on_complete()

    def _schedule_next_slice(self) -> None:
        if not self._is_cancelled and self._current_index < self._total:
            self._after_id = self.container.after(self.interval_ms, self._process_slice)

    def _process_slice(self) -> None:
        if self._is_cancelled:
            return

        start_time = time.perf_counter()
        while self._current_index < self._total:
            self.item_factory(self.container, self.items[self._current_index], self._current_index)
            self._current_index += 1

            # Si excedió la franja de 12 ms, ceder el control al mainloop
            if (time.perf_counter() - start_time) >= self.max_slice_ms:
                break

        if self._current_index < self._total:
            self._schedule_next_slice()
        else:
            if self.on_complete:
                self.on_complete()

    def cancel(self) -> None:
        """Detiene la construcción si el usuario cambia de vista o aplica un filtro nuevo."""
        self._is_cancelled = True
        if self._after_id:
            try:
                self.container.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None


# --- 4. Debouncer: Control de Frecuencia de Eventos (Teclado y Resize) ---

class Debouncer:
    """
    Gestor de debounce para widgets de CustomTkinter.
    Evita saturar la CPU con cálculos geométricos en búsquedas rápidas o redimensionado.
    """
    def __init__(self, widget: ctk.CTkBaseClass) -> None:
        self.widget = widget
        self._timers: Dict[str, str] = {}

    def debounce(self, event_key: str, wait_ms: int, callback: Callable[[], None]) -> None:
        """Cancela el temporizador previo para la misma clave y programa una nueva llamada."""
        if event_key in self._timers:
            try:
                self.widget.after_cancel(self._timers[event_key])
            except Exception:
                pass

        after_id = self.widget.after(wait_ms, lambda: self._execute(event_key, callback))
        self._timers[event_key] = after_id

    def _execute(self, event_key: str, callback: Callable[[], None]) -> None:
        if event_key in self._timers:
            del self._timers[event_key]
        callback()

    def cancel_all(self) -> None:
        for after_id in self._timers.values():
            try:
                self.widget.after_cancel(after_id)
            except Exception:
                pass
        self._timers.clear()


# --- Ejemplo de Integración de Debounce con Entrada y Resize ---

def attach_search_debounce(entry_widget: ctk.CTkEntry, on_filter_callback: Callable[[str], None], wait_ms: int = 300) -> Debouncer:
    debouncer = Debouncer(entry_widget)

    def _on_key_release(event: Any) -> None:
        query = entry_widget.get().strip()
        debouncer.debounce("search_query", wait_ms, lambda: on_filter_callback(query))

    entry_widget.bind("<KeyRelease>", _on_key_release)
    return debouncer


def attach_window_resize_debounce(window: ctk.CTk, on_resize_callback: Callable[[], None], wait_ms: int = 450) -> Debouncer:
    debouncer = Debouncer(window)

    def _on_configure(event: Any) -> None:
        # Filtrar estrictamente: solo procesar si el evento proviene de la ventana misma, no de widgets hijos
        if event.widget is not window:
            return
        debouncer.debounce("window_resize", wait_ms, on_resize_callback)

    window.bind("<Configure>", _on_configure)
    return debouncer
