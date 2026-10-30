# Tâche Codex 356 : la suite de l'intégration 7eb45ff, attribution et harnais du consentement

La suite complète de l'intégration `7eb45ff` (après les lots 325 à 348) donne **3 075 tests, 143 échecs et 18 erreurs**.
Bruts : `C:\Users\msics\donjon\artifacts\suite-7eb45ff\suite.log` et `suite.json` (copie du PC fixe). Lis `AGENTS.md`,
`docs/etat-dev.md` (court) et le rapport 339 (`docs/taches/rapport-codex-339-*.md`, même méthode sur une suite
précédente). Pour retrouver un lot, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Constat déjà fait par le superviseur
Le lot 325 (U-C, consentement) affiche « Compris : … » avant un acte lourd et attend « tenter ». Plusieurs tests écrits
avant lui donnent à la console des saisies simulées sans « tenter » : ils échouent sans défaut du jeu. Trois fichiers ont
déjà été adaptés (`test_repli_et_appel`, `test_mandat_joueur`, `test_emissions_parole`, commit 3930182) : le harnais
`jouer` de `tests/test_repli_et_appel.py` accepte `suite=("tenter",)`, et `tests/consentement_support.py` existe.
Mais d'autres familles apparaissent aussi (rendu social, protection de Gorm, ouïe de Bram, lampes de la mine,
fournisseurs/websocket, cache KV local) : rien ne garantit qu'elles viennent toutes du consentement.

## Ce qu'on attend (un invariant : la suite redevient un témoin fiable)
1. **Attribution de chaque échec et erreur** à la fusion qui l'a introduit : rejouer chaque test (ou chaque fichier) sur
   les commits de fusion `--first-parent` entre le dernier état connu (suite du lot 339) et `7eb45ff`, par bissection,
   deux processus réduits au plus. Tableau : test, première fusion rouge, cause en une ligne, catégorie (harnais du
   consentement / attente périmée prouvée / régression réelle / environnement).
2. **Harnais du consentement** : adapter les seuls tests de cette catégorie pour qu'ils confirment l'aperçu (« tenter »
   ou `consentement_support`), **sans changer aucune assertion** ; preuve qu'après adaptation ils vérifient la même
   chose qu'avant 325.
3. **Attentes périmées** : seulement avec preuve (la fusion responsable a changé volontairement le comportement, citée
   dans son rapport) ; sinon, c'est une régression.
4. **Régressions réelles** : ne pas les corriger ici sauf correctif évident d'une ligne dans le contrat commun ; les
   lister avec leur cas et leur fusion d'origine, pour des petits lots séparés.

## Vérification
Les fichiers adaptés et les fichiers touchés, verts sur l'intégration actuelle (`origin/integration`). Pas de suite
complète (le superviseur la relance), ni Luna, ni banc.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite, calculs longs détachés (`CALCUL EN COURS`). Lots en
cours : 353 (`jeu.py`, `tui.py`), 354 (`page.html`, `dialogues.py`, `jeu.py`, `paroles.py`), 355 (E4,
`propositions.py`, `echanges.py`, `agendas.py`, comptes) ; ne touche aucun fichier de code de ces lots ; les fichiers
de tests sont permis.

## Livraison
- Branche `codex-suite-rouge-7eb45ff`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport `docs/taches/rapport-codex-356-suite-rouge-7eb45ff.md` (tableau d'attribution en annexe dans
  `docs/taches/attribution-codex-356-suite-rouge.md`) ; entrée « non fusionnée » de 8 lignes au plus dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\suite-rouge-356\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
