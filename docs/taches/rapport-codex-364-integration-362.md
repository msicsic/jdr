# E6 / 362 — activation indépendante du poste pour le MJ simulé

Branche `codex-e6-libre-date`. Base `origin/integration ba05abe5`, fusion
sans rebase `869c867c`. `etat-dev.md` reprend l'intégration puis cette entrée.
**Correctif vérifié et poussé ; aucun calcul actif, aucune passe Luna.**

**Cause établie.** La TUI E6 remplaçait `jeu.MJ`, sans fixer l'activation de
la connexion. Or `jeu.main` décide, avant d'appeler cette fabrique, si une clé
API est présente. Sans clé, il reste hors ligne et n'appelle jamais le double :
la phrase libre ne peut pas ouvrir le formulaire, d'où l'écran d'introduction
et l'attente du harnais. Avec une clé ambiante, le même test passe après fusion.
Ce diagnostic ne montre pas de régression mécanique des identités du 362.

Reproduction native sans clé : même assertion `test_tui.py:412`, après
61,775 s ; les sorties contiennent « Cette phrase nécessite le MJ IA ».
Contre-épreuve sur copies : huit combinaisons huile/verrou, avec/sans clé
factice et `_cites_du_contexte` d'avant/d'après 362 donnent exactement le
même choix de connexion : zéro appel au double sans clé, un avec clé ;
formulaire seulement avec clé. Les sauvegardes rechargées gardent 50 pièces.
Cette contre-épreuve remplace cette seule fonction par sa version parent,
elle ne prétend pas rejouer toute une ancienne intégration.

**Contrat commun corrigé.** `tests.support.mj_simule` associe le fournisseur
simulé à une connexion de test activée et neutralise le chargement du `.env`
du poste. E6 et la TUI E5 utilisent ce contexte ; leurs assertions sont
inchangées. Le rejeu TUI E6 sans clé ambiante passe en 9,681 s sur huile puis
verrou, avec paiement, compteur d'appels et recharge contrôlés. Aucune règle
de jeu, de configuration réelle, de perception ou de connaissance n'est changée.

**Contrôles.** AST : les 48 assertions E6 et les 74 assertions E5 sont
identiques au parent `b3fd18a3`. `_connu_du_joueur` et `_cites_du_contexte`
sont identiques à l'intégration du 362 ; ses protections sont conservées.
**64 tests distincts / neuf fichiers verts**, zéro échec, erreur ou saut,
171,331 s sans clé API ambiante, deux travailleurs réduits : E6 (10),
correction de parole (5), identités connues (1), N3 (3), offres matérielles
(4), récit (8), enrichissement (10), E4 (14) et E5 (9). Le rejeu isolé TUI
est déjà compris dans ces 64 méthodes. Ni suite complète ni appel au modèle.

**Limites et décision.** L'utilisateur autorise la fusion partielle d'E6
(363/364), avec les limites de compilation et d'orientation Luna du rapport
364. Ce correctif du harnais ne les résout pas et ne les requalifie pas en
succès. Il corrige une dépendance de test au poste, pas une défaillance du MJ.

Bruts : `C:/Users/msics/donjon/artifacts/e6-364/integration-362/` :
reproductions, `activation-mj.json`, `contrats.json`, `tests-demandes.json`,
`sources.json` et **`fin-correction.json` : correctif_verifie=true**.
