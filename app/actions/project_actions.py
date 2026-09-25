import subprocess
import time


def open_finansys():
    project_path = r"C:\Users\biell\OneDrive\Desktop\CodexProj\FinanSys"
    git_bash = r"C:\Program Files\Git\git-bash.exe"

    # Abre Vite minimizado
    subprocess.Popen(
        [
            "cmd",
            "/c",
            "start",
            "/min",
            "",
            git_bash,
            "-c",
            f'cd "{project_path}" && npm run dev; exec bash'
        ]
    )

    # Abre Laravel minimizado
    subprocess.Popen(
        [
            "cmd",
            "/c",
            "start",
            "/min",
            "",
            git_bash,
            "-c",
            f'cd "{project_path}" && php artisan serve; exec bash'
        ]
    )

    # Aguarda o servidor iniciar
    time.sleep(3)

    # Abre o sistema no Edge
    subprocess.Popen([
        "cmd",
        "/c",
        "start",
        "msedge",
        "http://127.0.0.1:8000"
    ])

    return "FinanSys iniciado."