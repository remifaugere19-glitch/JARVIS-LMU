#!/usr/bin/env python3
"""JARVIS DEV CONNECT — lecteur GitHub public, lecture seule.

Ce script n'accède pas au dossier JARVIS et n'exécute aucun correctif.
Il affiche uniquement les noms des propositions présentes sur la branche dédiée.
"""
import json
import sys
import urllib.error
import urllib.request

API_URL = (
    "https://api.github.com/repos/remifaugere19-glitch/"
    "JARVIS-LMU/contents/dev-connect/proposals?ref=jarvis-dev-connect"
)
MAX_RESPONSE_BYTES = 512_000
TIMEOUT_SECONDS = 12


def list_proposals():
    request = urllib.request.Request(
        API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "JARVIS-DEV-CONNECT-read-only/0.1",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            payload = response.read(MAX_RESPONSE_BYTES + 1)
            if len(payload) > MAX_RESPONSE_BYTES:
                raise ValueError("Réponse GitHub trop volumineuse")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return []
        raise RuntimeError(f"Erreur GitHub HTTP {exc.code}") from exc
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, list):
        raise ValueError("Réponse GitHub inattendue")
    names = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if item.get("type") == "file" and isinstance(name, str) and name.endswith(".json"):
            names.append(name)
    return sorted(names)


def main():
    try:
        proposals = list_proposals()
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Consultation impossible : {exc}", file=sys.stderr)
        return 1
    if not proposals:
        print("Aucune proposition de correctif disponible.")
    else:
        print("Propositions disponibles (noms uniquement) :")
        for name in proposals:
            print(f" - {name}")
    print("Mode lecture seule : aucune modification locale.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
