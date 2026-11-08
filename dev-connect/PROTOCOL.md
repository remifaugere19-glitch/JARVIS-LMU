# Protocole JARVIS DEV CONNECT — brouillon 0.1

## Transport
GitHub, branche `jarvis-dev-connect`. Les propositions peuvent être placées sous `dev-connect/proposals/`. Le client Windows ne doit pas considérer le contenu du dépôt comme fiable par défaut.

## Proposition (format conceptuel)
```json
{
  "schema_version": "0.1",
  "id": "example-001",
  "description": "Modification factice, sans effet",
  "target_relative_path": "config/example.json",
  "base_sha256": "64 caractères hexadécimaux",
  "proposed_sha256": "64 caractères hexadécimaux",
  "requires_restart": true,
  "status": "PROPOSED"
}
```

Aucune proposition réelle n'est publiée à cette étape. Ce document ne définit **pas** un format exécutable et n'autorise aucune écriture.

## Contrôles requis avant une implémentation
- Vérifier l'origine, la branche et l'identifiant du commit; ne pas suivre des liens externes arbitraires.
- Rejeter les chemins absolus, les traversées de répertoire, les liens symboliques et les fichiers hors de la copie de test.
- Vérifier les empreintes et les différences avant approbation.
- Afficher exactement les fichiers touchés, les risques et le besoin éventuel de redémarrage.
- Demander une confirmation locale explicite pour chaque application.
- Refuser l'exécution de scripts issus du dépôt.
- Ne jamais modifier la version active en pleine course.
- Ne jamais publier de contenu sensible dans le dépôt public.

## Limite actuelle
Cette branche ne permet pas encore à ChatGPT de communiquer automatiquement avec JARVIS DEV CONNECT ni de modifier JARVIS ou LMU.
