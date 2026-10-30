# Tâche Codex 378 : S1a, une seule porte pour insérer et évincer un épisode

Premier lot de S1, le socle de la mémoire unifiée ([plan de l'esprit social](../plan-esprit-social.md) ;
[conception S0](../conception-memoire-unifiee.md), § 5 « Plan de migration », ligne S1a, et son
[index mesuré](../conception-memoire-unifiee-annexe-acces.md)). Lis `AGENTS.md`, `docs/etat-dev.md` (court), la
conception S0 en entier (§ 2 à 7) et le rapport 373.

## Invariant (un seul)
**Toute insertion et toute éviction d'un épisode dans la mémoire des événements d'un esprit passent par une porte
commune unique ; le stockage historique (liste, plafond de 40, ordre, sérialisation, clés sauvegardées) reste
strictement inchangé, avec les mêmes crochets et la même réentrance.** Aucun changement de choix, de parole, de délai,
de tirage, de classement, de valeur de relation ni d'ordre de sérialisation. Les lectures ne sont pas encore portées
(S1b et suivants) ; seul le contrôle AST des écritures est ajouté : plus aucune écriture directe du stock hors de la
porte (inventaire décroissant à partir de l'annexe S0).

## Vérification
Les fichiers de tests que la conception S0 indique pour S1a (`esprits`, `relations_graduees`, `defense`, `temps_etat`)
et ceux des écrivains touchés ; cas historique réel et autre cas, état complet, rendu, scène et paroles après recharge,
même laps entier/découpé. **Empreintes 2 h, quatre graines, scénarios touchés et Relais, identiques**
(`tools/comparer_bancs.py --empreintes --reference main`, cache) ; égalité brute de l'état attendue. Pas de suite
complète, ni Luna.

## Contraintes
**Poste : le laptop.** Pendant S1, aucun autre lot PNJ n'ajoute de registre. Lots en cours qui touchent des modules
voisins : 374 (position crue, `esprits.py`/`planification.py`), 375 (rouges de la suite), 376 (messages selon le
découpage, `pnj.py`), 377 (double promesse, `echanges.py`/`agendas.py`) : touche le moins possible leurs fonctions,
signale tout recouvrement ; à la fin, fusionne `origin/integration` dans ta branche si elle a avancé. Deux processus au
plus, priorité réduite, calculs longs détachés.

## Livraison
- Branche `codex-s1a-porte-episodes`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-378-s1a-porte-episodes.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\s1a-378\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
