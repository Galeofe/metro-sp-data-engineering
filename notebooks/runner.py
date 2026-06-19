"""
Executor de notebooks com rastreamento de status.
Usado pelo dashboard Streamlit para executar/sincronizar os notebooks.
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE      = Path(__file__).parent
BASE      = HERE.parent
DATA_GOLD = BASE / "data" / "gold"
STATUS_F  = HERE / ".nb_status.json"

NOTEBOOKS = {
    "bronze": HERE / "bronze_analysis.ipynb",
    "silver": HERE / "silver_analysis.ipynb",
    "gold":   HERE / "gold_analysis.ipynb",
}

LABELS = {
    "bronze": ("📥 Bronze", "#cd7f32"),
    "silver": ("◆ Silver", "#b8b8c8"),
    "gold":   ("◈ Gold",   "#ffd700"),
}


# ── Status persistence ────────────────────────────────────────────────────────
def load_status() -> dict:
    if STATUS_F.exists():
        try:
            return json.loads(STATUS_F.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_status(status: dict):
    STATUS_F.write_text(json.dumps(status, indent=2, ensure_ascii=False),
                        encoding="utf-8")


# ── Data change detection ─────────────────────────────────────────────────────
def data_fingerprint() -> str:
    """Hash dos mtimes dos parquets Gold — muda quando pipeline é re-executado."""
    import hashlib
    h = hashlib.md5()
    for f in sorted(DATA_GOLD.glob("*.parquet")):
        if f.exists():
            h.update(f"{f.name}:{f.stat().st_mtime:.0f}".encode())
    return h.hexdigest()


def notebooks_need_sync() -> bool:
    """True se os dados Gold foram atualizados depois da última sincronização."""
    status = load_status()
    saved_fp = status.get("_data_fingerprint", "")
    return data_fingerprint() != saved_fp


# ── Notebook creation ─────────────────────────────────────────────────────────
def ensure_notebooks():
    """Cria os notebooks se ainda não existem."""
    missing = [k for k, p in NOTEBOOKS.items() if not p.exists()]
    if missing:
        script = HERE / "create_notebooks.py"
        if script.exists():
            subprocess.run(
                [sys.executable, str(script)],
                cwd=str(BASE),
                capture_output=True,
            )
    return all(p.exists() for p in NOTEBOOKS.values())


# ── Execution ─────────────────────────────────────────────────────────────────
def execute_notebook(name: str) -> dict:
    """Executa um notebook com nbclient e retorna dict de status."""
    path = NOTEBOOKS.get(name)
    if not path or not path.exists():
        return {"status": "error", "message": f"Notebook '{name}' não encontrado.",
                "last_run": datetime.now().isoformat()}

    try:
        import nbformat
        import nbclient
    except ImportError:
        return {"status": "error",
                "message": "nbformat/nbclient não instalados. Rode: pip install nbformat nbclient ipykernel",
                "last_run": datetime.now().isoformat()}

    t0 = datetime.now()
    env = {**os.environ, "METRO_SP_BASE": str(BASE), "PYTHONIOENCODING": "utf-8"}
    try:
        nb = nbformat.read(str(path), as_version=4)
        client = nbclient.NotebookClient(
            nb,
            timeout=180,
            kernel_name="python3",
            resources={"metadata": {"path": str(BASE)}},
        )
        client.execute()
        nbformat.write(nb, str(path))   # salva com outputs

        n_cells = sum(1 for c in nb.cells if c.cell_type == "code")
        n_errors = sum(
            1 for c in nb.cells
            for o in c.get("outputs", [])
            if o.get("output_type") == "error"
        )
        duration = (datetime.now() - t0).total_seconds()
        result = {
            "status": "error" if n_errors else "ok",
            "last_run":  datetime.now().isoformat(),
            "duration":  round(duration, 1),
            "cells":     n_cells,
            "errors":    n_errors,
        }
    except Exception as exc:
        result = {
            "status":   "error",
            "last_run": datetime.now().isoformat(),
            "duration": round((datetime.now() - t0).total_seconds(), 1),
            "message":  str(exc)[:600],
        }

    status = load_status()
    status[name] = result
    save_status(status)
    return result


def execute_all(names=None) -> dict:
    """Executa todos os notebooks (ou lista específica) e atualiza fingerprint."""
    if names is None:
        names = list(NOTEBOOKS.keys())
    results = {}
    for name in names:
        results[name] = execute_notebook(name)

    status = load_status()
    status["_data_fingerprint"] = data_fingerprint()
    status["_sync_time"] = datetime.now().isoformat()
    save_status(status)
    return results


# ── Notebook rendering ────────────────────────────────────────────────────────
def render_to_html(name: str) -> str | None:
    """Converte notebook para HTML (para exibição no Streamlit)."""
    path = NOTEBOOKS.get(name)
    if not path or not path.exists():
        return None
    try:
        import nbformat
        from nbconvert import HTMLExporter

        nb = nbformat.read(str(path), as_version=4)
        exporter = HTMLExporter()
        exporter.template_name = "classic"
        body, _ = exporter.from_notebook_node(nb)
        return body
    except Exception:
        return None


def notebook_cells(name: str):
    """Retorna lista de cells do notebook para renderização manual."""
    path = NOTEBOOKS.get(name)
    if not path or not path.exists():
        return []
    try:
        import nbformat
        nb = nbformat.read(str(path), as_version=4)
        return nb.cells
    except Exception:
        return []


# ── Jupyter server ────────────────────────────────────────────────────────────

def _find_jupyter_lab_exe() -> str:
    """
    Retorna o caminho para jupyter-lab.exe / jupyter-lab.
    Procura em Scripts do Python (incluindo instalações user-level no Windows).
    """
    import sysconfig
    candidates = [
        # user scripts (pip install --user no Windows)
        Path(sys.executable).parent.parent / "AppData" / "Roaming" /
            f"Python{sys.version_info.major}{sys.version_info.minor}" / "Scripts" /
            "jupyter-lab.exe",
        # site scripts junto ao python.exe
        Path(sysconfig.get_path("scripts")) / "jupyter-lab.exe",
        Path(sysconfig.get_path("scripts")) / "jupyter-lab",
        # fallback: Scripts no mesmo nível do executável
        Path(sys.executable).parent / "Scripts" / "jupyter-lab.exe",
        Path(sys.executable).parent / "jupyter-lab.exe",
    ]
    # Tentar via sysconfig do usuário
    try:
        user_scripts = Path(sysconfig.get_path("scripts", "nt_user"))
        candidates.insert(0, user_scripts / "jupyter-lab.exe")
    except Exception:
        pass

    for p in candidates:
        if p.exists():
            return str(p)
    return "jupyter-lab"   # último recurso: confiar no PATH


def start_jupyter_lab(port: int = 8888) -> bool:
    """
    Inicia Jupyter Lab em uma janela CMD visível (Windows).
    Usa ServerApp.token='' para não exigir autenticação local.
    Retorna True se o processo foi lançado sem exceção.
    """
    if jupyter_running(port):
        return True   # já em execução

    jlab = _find_jupyter_lab_exe()

    flags = 0
    try:
        # Windows: sem janela CMD visível
        flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
    except AttributeError:
        pass

    try:
        subprocess.Popen(
            [jlab,
             f"--port={port}",
             "--no-browser",
             "--ip=127.0.0.1",
             "--ServerApp.token=",
             "--ServerApp.password=",
             f"--notebook-dir={BASE}"],
            cwd=str(BASE),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
        )
        return True
    except Exception:
        return False


def jupyter_running(port: int = 8888) -> bool:
    """Verifica se algo já está escutando na porta do Jupyter."""
    import socket
    try:
        with socket.create_connection(("localhost", port), timeout=1):
            return True
    except OSError:
        return False