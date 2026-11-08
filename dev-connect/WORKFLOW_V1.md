# JARVIS DEV CONNECT V1 — workflow de test

Le client Windows est fourni sous forme de ZIP dans la conversation ChatGPT. Il utilise exclusivement la bibliothèque standard Python.

1. Lire la liste des propositions depuis la branche `jarvis-dev-connect` du dépôt **public**.
2. Charger et vérifier le JSON d'une proposition sélectionnée.
3. Sélectionner JARVIS comme **source en lecture seule**.
4. Créer explicitement une copie de test indépendante.
5. Vérifier les chemins, empreintes SHA-256 et la syntaxe Python; prévisualiser les différences.
6. Appliquer seulement sur la copie de test avec confirmation explicite et sauvegarde.
7. Exporter manuellement un diagnostic anonymisé; aucun envoi automatique.

Le test `test-lecture-seule-001.json` ne contient aucune modification et n'est pas applicable.

**Limitations :** pas de connexion automatique à ChatGPT, pas de dépôt de diagnostic automatique sur GitHub, pas d'accès distant au PC, pas de rechargement à chaud de la V54. Ne pas confondre le dépôt GitHub avec la V54 locale. Ne jamais publier de code privé ou de secrets sur le dépôt public.
