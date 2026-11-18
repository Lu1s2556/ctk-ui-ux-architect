#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditor Automático de Interfaces CustomTkinter
Valida presupuestos de Canvas, colapsos geométricos, truncado de texto y colores adaptativos.
Genera capturas multimodales en Light/Dark/Responsive cuando PIL.ImageGrab está disponible.
Compatibilidad estricta: Python 3.8.10+
"""

from __future__ import annotations
import argparse
import importlib.util
import json
import os
import sys
import time
from typing import Dict, List, Tuple, Any, Optional

try:
    import customtkinter as ctk
except ImportError:
    ctk = None

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None


class CTkInspector:
    """Motor de inspección geométrica, cromática y de rendimiento para CustomTkinter."""

    def __init__(self, app_instance: Any, output_dir: str = "./ui_audit") -> None:
        self.app = app_instance
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.report_path = os.path.join(self.output_dir, "audit_report.json")

    def run_audit(self, capture_screenshots: bool = True) -> Dict[str, Any]:
        """Ejecuta la auditoría completa tras estabilizar el layout."""
        self.app.update_idletasks()
        self.app.update()

        metrics = self._inspect_widget_tree()
        screenshots_taken: List[str] = []

        if capture_screenshots and ImageGrab is not None:
            screenshots_taken = self._capture_multimodal_states()

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": metrics,
            "screenshots": screenshots_taken,
            "verdict": self._compute_verdict(metrics)
        }

        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report

    def _inspect_widget_tree(self) -> Dict[str, Any]:
        all_widgets: List[Any] = []
        scrollable_frame_loads: Dict[str, int] = {}
        collapsed_containers: List[str] = []
        truncated_texts: List[Dict[str, Any]] = []
        hardcoded_single_colors: List[Dict[str, Any]] = []

        def _traverse(widget: Any) -> None:
            all_widgets.append(widget)
            cls_name = widget.__class__.__name__

            # Comprobar carga de CTkScrollableFrame
            if cls_name == "CTkScrollableFrame":
                # En CTkScrollableFrame los hijos residen en scrollable_canvas o contenedor interno
                child_count = 0
                for attr_name in ("_parent_canvas", "_scrollable_frame"):
                    if hasattr(widget, attr_name):
                        inner = getattr(widget, attr_name)
                        if hasattr(inner, "winfo_children"):
                            child_count = max(child_count, len(inner.winfo_children()))
                if child_count == 0:
                    child_count = len(widget.winfo_children())
                scrollable_frame_loads[str(widget)] = child_count

            # Contenedores colapsados (ancho o alto <= 2 estando mapeados)
            if hasattr(widget, "winfo_ismapped") and widget.winfo_ismapped():
                w = widget.winfo_width()
                h = widget.winfo_height()
                if (w <= 2 or h <= 2) and cls_name in ("CTkFrame", "Frame", "CTkScrollableFrame"):
                    collapsed_containers.append(str(widget) + " (w=" + str(w) + ", h=" + str(h) + ")")

            # Textos truncados
            if cls_name in ("CTkLabel", "CTkButton", "Label", "Button"):
                try:
                    req_w = widget.winfo_reqwidth()
                    curr_w = widget.winfo_width()
                    if widget.winfo_ismapped() and curr_w > 0 and (req_w > curr_w + 6):
                        txt = ""
                        if hasattr(widget, "cget"):
                            try:
                                txt = str(widget.cget("text"))
                            except Exception:
                                pass
                        truncated_texts.append({
                            "widget": str(widget),
                            "class": cls_name,
                            "text_sample": txt[:30],
                            "req_width": req_w,
                            "curr_width": curr_w
                        })
                except Exception:
                    pass

            # Detección de colores unitarios hardcodeados (prohibidos por Ley 8)
            for color_attr in ("fg_color", "text_color", "border_color"):
                if hasattr(widget, "cget"):
                    try:
                        val = widget.cget(color_attr)
                        if isinstance(val, str) and val.startswith("#"):
                            hardcoded_single_colors.append({
                                "widget": str(widget),
                                "property": color_attr,
                                "value": val
                            })
                    except Exception:
                        pass

            for child in widget.winfo_children():
                _traverse(child)

        _traverse(self.app)

        total_count = len(all_widgets)
        warnings: List[str] = []
        criticals: List[str] = []

        if total_count > 250:
            criticals.append("Total de widgets excede presupuesto de Canvas (" + str(total_count) + " > 250).")
        elif total_count > 150:
            warnings.append("Total de widgets en rango de alerta (" + str(total_count) + " > 150).")

        for s_widget, count in scrollable_frame_loads.items():
            if count > 45:
                criticals.append("CTkScrollableFrame con sobrecarga: " + str(count) + " filas. Migrar a CTkThemedTreeview.")

        if collapsed_containers:
            warnings.append("Se detectaron " + str(len(collapsed_containers)) + " contenedores colapsados.")

        if truncated_texts:
            warnings.append("Se detectaron " + str(len(truncated_texts)) + " textos potencialmente truncados.")

        return {
            "total_widgets": total_count,
            "scrollable_frame_loads": scrollable_frame_loads,
            "collapsed_containers": collapsed_containers,
            "truncated_texts": truncated_texts,
            "hardcoded_single_colors_count": len(hardcoded_single_colors),
            "hardcoded_single_colors_samples": hardcoded_single_colors[:10],
            "warnings": warnings,
            "criticals": criticals
        }

    def _capture_multimodal_states(self) -> List[str]:
        captures: List[str] = []
        try:
            self.app.lift()
            self.app.focus_force()
            self.app.update_idletasks()
            self.app.update()

            def _grab_window(filename: str) -> None:
                x = self.app.winfo_rootx()
                y = self.app.winfo_rooty()
                w = self.app.winfo_width()
                h = self.app.winfo_height()
                bbox = (x, y, x + w, y + h)
                img = ImageGrab.grab(bbox=bbox)
                out_path = os.path.join(self.output_dir, filename)
                img.save(out_path)
                captures.append(out_path)

            # 1. Dark Default
            ctk.set_appearance_mode("Dark")
            self.app.update_idletasks()
            time.sleep(0.2)
            _grab_window("01_dark_default.png")

            # 2. Light Default
            ctk.set_appearance_mode("Light")
            self.app.update_idletasks()
            time.sleep(0.2)
            _grab_window("02_light_default.png")

            # 3. Responsive Small
            orig_geo = self.app.geometry()
            self.app.geometry("820x540")
            self.app.update_idletasks()
            time.sleep(0.2)
            _grab_window("03_responsive_small.png")

            # Restaurar estado
            self.app.geometry(orig_geo)
            ctk.set_appearance_mode("Dark")
            self.app.update_idletasks()

        except Exception as exc:
            print("Aviso: No se pudieron completar las capturas gráficas:", str(exc))

        return captures

    def _compute_verdict(self, metrics: Dict[str, Any]) -> str:
        if metrics["criticals"]:
            return "FAILED_CRITICAL"
        if metrics["warnings"]:
            return "PASSED_WITH_WARNINGS"
        return "PASSED_PERFECT"


def audit(app_instance: Any, output_dir: str = "./ui_audit", close_after: bool = False) -> None:
    """
    Función de una sola línea para auditar cualquier app CustomTkinter en ejecución.
    Ejemplo de uso:
        from ctk_inspector import audit; audit(app)
    """
    inspector = CTkInspector(app_instance, output_dir=output_dir)

    def _run() -> None:
        report = inspector.run_audit(capture_screenshots=False)
        print("\n================= 🔍 AUDITORÍA CTK =================")
        verdict = report["verdict"]
        symbol = "🟢" if verdict == "PASSED_PERFECT" else ("🟡" if verdict == "PASSED_WITH_WARNINGS" else "🔴")
        print(f"Veredicto: {symbol} {verdict}")
        print(f"Total widgets vivos: {report['metrics']['total_widgets']} (Límite Canvas: 200)")
        print(f"Contenedores colapsados: {len(report['metrics']['collapsed_containers'])}")
        print(f"Textos cortados/truncados: {len(report['metrics']['truncated_texts'])}")
        print(f"Colores sin tupla adaptativa: {report['metrics']['hardcoded_single_colors_count']}")
        if report["metrics"]["criticals"]:
            print("\n🚨 CRÍTICOS:")
            for c in report["metrics"]["criticals"]:
                print(f"  • {c}")
        if report["metrics"]["warnings"]:
            print("\n⚠️ ADVERTENCIAS:")
            for w in report["metrics"]["warnings"]:
                print(f"  • {w}")
        print(f"Reporte guardado en: {inspector.report_path}")
        print("===================================================\n")
        if close_after:
            try:
                app_instance.quit()
                app_instance.destroy()
            except Exception:
                pass

    app_instance.after(600, _run)


def find_all_targets(max_depth: int = 4, scan_templates: bool = False) -> List[str]:
    """
    Busca de forma recursiva archivos Python que instancien o hereden de ctk.CTk,
    ignorando directorios irrelevantes como .git, venv, build, etc.
    Por defecto ignora .agent y skills para no auto-auditar las plantillas internas,
    a menos que no se detecte ninguna app externa o scan_templates sea True.
    """
    ignored_dirs = {
        ".git", ".claude-plugin", ".codex-plugin",
        "venv", ".venv", "env", ".env", "__pycache__", "build", "dist",
        "node_modules", ".idea", ".vscode", "ui_audit"
    }
    if not scan_templates:
        ignored_dirs.update({".agent", "skills"})

    found_targets: List[str] = []

    for root, dirs, files in os.walk("."):
        # Filtrar directorios ignorados in-place para que os.walk no entre en ellos
        dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.startswith(".")]

        depth = os.path.relpath(root, ".").count(os.sep)
        if depth >= max_depth:
            dirs.clear()
            continue

        for f in files:
            if f.endswith(".py") and not f.startswith("test_") and f != "ctk_inspector.py":
                file_path = os.path.normpath(os.path.join(root, f))
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
                        content = fp.read()
                        if "customtkinter" in content or "ctk.CTk" in content:
                            found_targets.append(file_path)
                except Exception:
                    pass

    return found_targets


def select_target_interactively() -> Optional[str]:
    """Detecta objetivos y permite al usuario elegir si hay múltiples apps en el repositorio."""
    targets = find_all_targets(scan_templates=False)
    # Si no hay apps de usuario, permitir auditar plantillas del paquete como demostración
    if not targets:
        template_targets = find_all_targets(scan_templates=True)
        if template_targets:
            targets = template_targets

    if not targets:
        return None
    if len(targets) == 1:
        return targets[0]

    # Priorizar candidatos estándar como primer opción sugerida si existen
    priority_names = {"main.py", "app.py", "gui.py", "window.py"}
    targets.sort(key=lambda t: (0 if os.path.basename(t).lower() in priority_names else 1, t))

    print("\n🔍 Se detectaron aplicaciones CustomTkinter en el proyecto:")
    for idx, t in enumerate(targets, start=1):
        print(f"  [{idx}] {t}")

    try:
        choice = input(f"\n👉 Elige una opción [1-{len(targets)}] (Enter para [1]): ").strip()
        if not choice:
            return targets[0]
        selected_idx = int(choice) - 1
        if 0 <= selected_idx < len(targets):
            return targets[selected_idx]
    except Exception:
        pass

    return targets[0]


def inspect_file(target_file: str, class_name: Optional[str] = None, output_dir: str = "./ui_audit") -> Dict[str, Any]:
    """Carga dinámicamente un archivo Python con una app CustomTkinter y ejecuta la auditoría."""
    abs_path = os.path.abspath(target_file)
    if not os.path.exists(abs_path):
        raise FileNotFoundError("No se encontró el archivo especificado: " + abs_path)

    spec = importlib.util.spec_from_file_location("user_app_module", abs_path)
    if spec is None or spec.loader is None:
        raise ImportError("No se pudo cargar la especificación del módulo: " + abs_path)

    module = importlib.util.module_from_spec(spec)
    sys.modules["user_app_module"] = module
    spec.loader.exec_module(module)

    # Identificar la clase que hereda de ctk.CTk
    target_cls = None
    if class_name and hasattr(module, class_name):
        target_cls = getattr(module, class_name)
    else:
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, ctk.CTk) and attr is not ctk.CTk:
                target_cls = attr
                break

    if target_cls is None:
        # Fallback a instanciar la clase si se llama App o Main
        for fallback_name in ("App", "MainApp", "MainWindow"):
            if hasattr(module, fallback_name):
                target_cls = getattr(module, fallback_name)
                break

    if target_cls is None:
        raise ValueError("No se encontró una subclase de ctk.CTk en el módulo especificado.")

    print("Instanciando", target_cls.__name__, "para auditoría automática...")
    app = target_cls()

    inspector = CTkInspector(app, output_dir=output_dir)
    audit_result: Dict[str, Any] = {}

    def _scheduled_audit() -> None:
        print("Ejecutando escaneo visual y de árbol de widgets...")
        report = inspector.run_audit(capture_screenshots=True)
        audit_result.update(report)
        print("\n================= 🔍 AUDITORÍA CTK =================")
        verdict = report["verdict"]
        symbol = "🟢" if verdict == "PASSED_PERFECT" else ("🟡" if verdict == "PASSED_WITH_WARNINGS" else "🔴")
        print(f"Veredicto: {symbol} {verdict}")
        print(f"Total Widgets: {report['metrics']['total_widgets']}")
        print(f"Contenedores colapsados: {len(report['metrics']['collapsed_containers'])}")
        print(f"Textos truncados: {len(report['metrics']['truncated_texts'])}")
        print(f"Colores hardcodeados: {report['metrics']['hardcoded_single_colors_count']}")
        if report["metrics"]["criticals"]:
            print("\n🚨 CRÍTICOS:")
            for crit in report["metrics"]["criticals"]:
                print("  •", crit)
        if report["metrics"]["warnings"]:
            print("\n⚠️ ADVERTENCIAS:")
            for warn in report["metrics"]["warnings"]:
                print("  •", warn)
        print("\nReporte guardado en:", inspector.report_path)
        print("===================================================\n")
        try:
            app.quit()
            app.destroy()
        except Exception:
            pass

    app.after(600, _scheduled_audit)
    app.mainloop()
    return audit_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CTk UI/UX Inspector")
    parser.add_argument("--target", default=None, help="Ruta al archivo .py que define la aplicación CTk (autodetectado si se omite)")
    parser.add_argument("--class", dest="class_name", default=None, help="Nombre de la clase que hereda de ctk.CTk")
    parser.add_argument("--output-dir", default="./ui_audit", help="Directorio para reporte y capturas")
    args = parser.parse_args()

    target = args.target or select_target_interactively()
    if not target:
        print("\n❌ Error: No se encontró ningún archivo con CustomTkinter en el proyecto.")
        print("💡 Sugerencia: Especifica la ruta directamente con:")
        print("   python ctk_inspector.py --target ruta/a/tu_app.py\n")
        sys.exit(1)

    print(f"🎯 Auditando archivo: {target}")
    try:
        report = inspect_file(target, class_name=args.class_name, output_dir=args.output_dir)
        sys.exit(0 if report.get("verdict") != "FAILED_CRITICAL" else 1)
    except Exception as exc:
        print("❌ Error durante la auditoría:", str(exc))
        sys.exit(1)
