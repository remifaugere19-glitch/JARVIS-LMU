# JARVIS DEV CONNECT — branche de développement

Cette branche est indépendante de la version JARVIS V54 installée sur le PC.

## Objectif
Transporter des propositions de modifications depuis ChatGPT vers un agent local Windows, sans VSCodium ni Roo Code.

## État
**Protocole seulement. Aucune connexion locale, aucun agent automatique et aucune modification à chaud ne sont actifs.**

## Règles de sécurité
1. Le dépôt est **public** : ne jamais y publier de code privé de V54, logs sensibles, secrets, chemins personnels, télémétrie ou configuration locale.
2. Le client local ne doit lire que les demandes explicitement sélectionnées, depuis une branche dédiée, et n'exécuter aucun contenu téléchargé.
3. Toute demande est une proposition, jamais une commande. Validation humaine obligatoire avant modification.
4. Interdire les chemins absolus, chemins contenant `..`, liens symboliques sortants et destinations hors du dossier de test.
5. Vérifier le SHA-256 de la base et du contenu proposé avant toute application.
6. Préparer les changements sur une **copie de test**, jamais directement sur la V54 active.
7. Vérifier la syntaxe et effectuer les tests; conserver une sauvegarde et un journal de retour arrière.
8. Aucune application à chaud dans LMU tant qu'un mécanisme de rechargement et ses conditions de sûreté n'ont pas été vérifiés.
9. Ne pas synchroniser la V54 avec `main` : ce dépôt contient une autre version.

## Prochaines étapes
- Valider le schéma des propositions.
- Construire un lecteur local GitHub en lecture seule, sans exécution ni écriture dans JARVIS.
- Tester le transport de messages factices.
- Étudier ensuite les modifications à chaud, uniquement sur un environnement de test.

Le protocole initial se trouve dans `dev-connect/PROTOCOL.md`.
