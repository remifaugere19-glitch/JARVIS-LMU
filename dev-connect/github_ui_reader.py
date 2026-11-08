"""Lecteur de propositions GitHub pour JARVIS DEV CONNECT.

Composant indépendant : ne lit ni n'écrit dans le dossier JARVIS.
N'exécute aucun contenu téléchargé.
"""
import json
import urllib.error
import urllib.request

URL = "https://api.github.com/repos/remifaugere19-glitch/JARVIS-LMU/contents/dev-connect/proposals?ref=jarvis-dev-connect"
LIMIT = 256 * 1024

def fetch_proposal_names(opener=urllib.request.urlopen):
    request = urllib.request.Request(URL, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "JARVIS-DEV-CONNECT-readonly/0.2",
    })
    try:
        with opener(request, timeout=10) as response:
            raw = response.read(LIMIT + 1)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return []
        raise
    if len(raw) > LIMIT:
        raise ValueError("Réponse GitHub trop volumineuse")
    items = json.loads(raw.decode("utf-8"))
    if not isinstance(items, list):
        raise ValueError("Format GitHub inattendu")
    return sorted(
        x["name"] for x in items
        if isinstance(x, dict) and x.get("type") == "file"
        and isinstance(x.get("name"), str)
        and x["name"].endswith(".json")
    )

def show_in_window(parent, log_callback):
    """Bouton de consultation, à appeler explicitement depuis l'interface Tkinter."""
    from tkinter import messagebox
    try:
        names = fetch_proposal_names()
    except Exception as exc:
        messagebox.showerror("GitHub", f"Lecture impossible : {exc}", parent=parent)
        return
    if names:
        log_callback("GitHub — propositions (noms uniquement) : " + ", ".join(names))
    else:
        log_callback("GitHub — aucune proposition disponible.")
    messagebox.showinfo("GitHub", "Consultation terminée. Aucun correctif appliqué.", parent=parent)
