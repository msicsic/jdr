# Tâche Codex 359 : E5, le choix direct conserve l'accord affiché jusqu'à la validation

Cinquième lot de l'échéance négociée, après E1 à E4 (348, 350, 352 et sa correction 357, 355), fusionnés : un accord
daté (une part livrée ou une tâche accomplie avant une limite, contre des pièces payées maintenant) existe dans le moteur
et passe par le contenu typé existant. Conception : `docs/conception-menace-echeance.md`, sections 3, 5 (ligne E5 et
preuve commune P) et 6 (arbitrages acceptés le 2026-10-30, à ne pas rouvrir). Lis `AGENTS.md`, `docs/etat-dev.md`
(court), la conception et les rapports 355 (E4), 325 (U-C), 344/349/354 (menus U-M) et 353 (U-T).

## Invariant (un seul)
**Proposer un accord daté par le choix direct (menu web et terminal) transmet au moteur exactement les termes affichés :
prestation, limite (relative et heure de jeu, arbitrage 6), prix ; corriger un terme, annuler ou laisser l'offre se
périmer ne change rien au monde ; la validation passe par le consentement U-C et revalide les termes sans modèle.** Aucun
clic n'est réinterprété ; le formulaire ne reçoit que des paramètres publics (biens connus, destinataire perçu, prix
dans l'or de Corvus) ; « demain » ou une limite sans repère établi demande une précision (arbitrage 6) ; un délai
indéterminé est montré comme tel et l'accord reste possible sans limite (arbitrage 4).

## Vérification
- Proposer date et prix, corriger, annuler, offre périmée ; huile (auberge, cas 1.2) et une autre tâche ; refus du
  moteur rendus publiquement ; parité avec la saisie typée d'E4 (même contenu, même accord, mêmes comptes) ; zéro appel au
  modèle ; nombre de choix jusqu'à l'effet ; monde, comptes, paroles, scène et fiche identiques après recharge.
- Tests ciblés et voisins (E1 à E4, menus U-M, terminal U-T, consentement, tests du clic Node). Pas de Luna, de banc
  ni de suite complète.

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/gestes_publics.py`, `donjon/comprehension.py`, `donjon/web/page.html`,
`donjon/web/pont.py`, `jeu.py`/`tui.py` pour le terminal, `donjon/consentement.py` si un raccord est nécessaire. Ne
touche pas aux règles d'`agendas`/`echanges`/`propositions` (E4) sauf paramètre public manquant, signalé. Deux processus
au plus, priorité réduite.

## Livraison
- Branche `codex-e5-choix-direct`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-359-e5-choix-direct.md` ; entrée « non fusionnée » de 8 lignes au plus
  dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\e5-359\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
