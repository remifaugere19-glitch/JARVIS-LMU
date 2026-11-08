# JARVIS DEV CONNECT — étape suivante (V54 protégée)

## État confirmé
- JARVIS Imola V54 est la référence fonctionnelle validée par son utilisateur.
- La copie de test Windows existe et a été vérifiée : `JARVIS_TEST_DEV_20261108_110158`.
- La lecture GitHub et l'application d'un patch **factice** sur une copie ont été testées.
- Le dépôt GitHub public ne contient pas le code complet de la V54 locale.

## Périmètre
L'évolution concerne **tous** les domaines : démarrage/interface, télémétrie, reconnaissance des voitures/custom teams, freinage, voix/Discord, spotter/drapeaux, stratégie/carburant/pneus/météo, MFD/setups, mémoire/IA, mises à jour/sauvegardes, diagnostic/distribution.

## Séquence d'intégration sécurisée
1. **Lecture seule** : sélectionner la copie de test, confirmer le chemin canonique et afficher l'inventaire des fichiers concernés.
2. **Proposition** : télécharger uniquement des manifestes JSON de la branche `jarvis-dev-connect` et présenter leur diff. Aucune exécution de code téléchargé.
3. **Vérifications préalables** : refuser chemins absolus, `..`, liens symboliques, cibles hors copie, changements de fichier inattendus et empreintes SHA-256 divergentes. Vérifier également que la proposition provient du commit attendu.
4. **Approbation** : confirmation explicite de chaque lot de modifications sur la **copie** ; jamais de mise à jour silencieuse de V54.
5. **Application transactionnelle** : sauvegarder les fichiers de la copie, écrire des fichiers temporaires dans le même répertoire, valider les empreintes, remplacer de manière atomique si possible ; annuler le lot et restaurer les sauvegardes en cas d'échec.
6. **Contrôles** : syntaxe, imports, tests ciblés et non-régression des 11 domaines ; puis essais LMU manuels lorsque nécessaires.
7. **Promotion éventuelle** : uniquement après demande explicite et sauvegarde vérifiée de V54. Ne jamais appliquer en course.

## Limites
- Un inventaire JSON sans code source ne permet pas de produire un patch fonctionnel fiable.
- Le dépôt étant public, ne pas y déposer la V54, des logs sensibles, des chemins personnels, des jetons ou des données privées.
- L'outil Windows doit être lancé localement par l'utilisateur ; une écriture GitHub ne modifie pas automatiquement le PC.
- Le « hot reload » est un objectif ultérieur, pas une fonctionnalité validée.

## Prochain test utile
Sur la copie Windows uniquement, exporter en privé les **fichiers d'entrée et leurs imports locaux** (sans secrets) ou partager une archive ciblée dans la conversation. Étudier ensuite un changement concret demandé par l'utilisateur, préparer un manifeste avec SHA-256 et faire approuver son application à la copie.
