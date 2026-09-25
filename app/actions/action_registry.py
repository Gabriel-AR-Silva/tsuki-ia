from app.actions.project_actions import open_finansys

ACTIONS = {
    "open_finansys": {
        "aliases": [
            "finansys",
            "abrir finansys",
            "iniciar finansys"
        ],
        "handler": open_finansys
    }
}