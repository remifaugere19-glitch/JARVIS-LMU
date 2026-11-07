# JARVIS Direct pour Windows

1. Extraire le petit ZIP et double-cliquer sur INSTALLER_JARVIS_DIRECT.bat.
2. Choisir le dossier de la copie V58 installée, puis cliquer sur « Activer une fois ».
3. Vérifier que le panneau affiche « A_JOUR » et une heure de vérification récente. La révision initiale est 0.

L’agent vérifie la branche jarvis-direct du dépôt remifaugere19-glitch/JARVIS-LMU environ toutes les 15 secondes. La propagation GitHub et la durée des tests s’ajoutent à ce délai. Une fois le correctif publié, le PC télécharge les fichiers modifiés et les tests, vérifie les empreintes et teste une copie locale. Il sauvegarde les fichiers concernés puis relance les composants actifs de JARVIS. LMU reste ouvert. Une relance du moteur peut couper la voix et réinitialiser les informations temporaires de la session. Un composant Windows élevé peut demander les droits correspondants.

Le panneau « JARVIS - mises a jour directes » sur le Bureau permet de voir l’état, de mettre la réception en pause ou d’annuler la dernière mise à jour. Les sauvegardes sont dans SYSTEME_JARVIS/DIRECT_GITHUB/ANCIENNES_VERSIONS. L’agent démarre à l’ouverture de session Windows via l’entrée JARVISDirect de la clé Run de l’utilisateur. Il lit le dépôt public et conserve les diagnostics sur le PC.

## Publication des prochaines corrections

Dans une copie de travail, utiliser package/publisher.py avec --baseline et --candidate pointant chacun vers la racine JARVIS_LMU, un numéro --revision consécutif, un --id unique, au moins un --test et un dossier --output. Chaque test reçoit la copie de l’application dans la variable JARVIS_CANDIDATE_ROOT. Vérifier le correctif et publier en un commit ses objets jarvis-updates/blobs et son entrée dans la liste updates de jarvis-updates/channel.json, sur la branche jarvis-direct. Le fichier release_preview.json est une proposition et ne déclenche aucune installation. Un fichier peut atteindre 32 Mio et le contenu modifié d’une révision 128 Mio. Les binaires doivent être construits pour Windows et compatibles avec les dépendances installées.

Les tests locaux couvrent le remplacement de code, les échecs de test, les sauvegardes, la récupération après interruption et les retours arrière. La gestion des processus Windows est simulée durant ces essais. Le premier essai en jeu reste à effectuer.
