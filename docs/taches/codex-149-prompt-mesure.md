# Tâche Codex 149 (plan prompt, L0) : mesurer ce que reçoit le MJ et ce qui casse le préfixe

Lot de 30 à 45 minutes (`AGENTS.md`). **Mesure seule : aucun changement de code du jeu.** **Poste : le PC fixe**
(`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste
(dont des bancs longs) : un processus de calcul, priorité réduite. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, **`docs/plan-prompt.md`** (constat, décisions, lots L0 à L8), les rapports des lots 93 (mutualisation
`$defs`, mesure par appel) et 95 (entrées de l'audit narratif), puis `mj.py` (assemblage du schéma et des consignes
d'interprétation, `dossier_*`), `donjon/sources.py`, `donjon/fournisseurs/openai.py` et `fournisseurs/schema.py`.

## Ce qu'il faut mesurer
Sur les fils Luna déjà joués, **sans rejouer Luna** : `C:\Users\msics\donjon\artifacts\verif-luna-9a39738\` (lot 141, 42
parties) et les références en cache ; si les requêtes complètes n'y sont pas archivées, reconstruis-les en rejouant les
parties avec un MJ simulé qui renvoie les réponses archivées (aucun appel réseau), sur des copies.
- **Taille réellement envoyée par voie** (interprétation, contre-revue, fidélité, audit narratif, narration…), après
  mutualisation : `instructions`, schéma (`tools`/`text.format`), entrée, et dans l'entrée chaque bloc de `faits`
  (catalogues `*_a_completer`, `faits_narratifs_proposables`, `attestations`, objets, surfaces génériques, dossiers
  `atelier`/`franchissements`/`passages_obstacles`/`espace`). Caractères et estimation de jetons.
- **Stabilité du préfixe** : pour chaque voie, entre deux appels successifs d'une même partie, longueur du préfixe commun
  de la requête sérialisée dans l'ordre d'envoi, et **première cause de divergence** (consignes, schéma : modes, `anyOf`,
  enum de `faits` ; entrée). Proportion d'appels où le schéma ou les consignes changent.
- **Jetons cachés** relevés par le fournisseur dans les fils (lot 93), par voie, à rapprocher du préfixe commun.
- Pour les dossiers bornés à la salle : sur combien d'appels un dossier d'atelier, de franchissement ou d'obstacles est
  envoyé alors qu'aucun de ses objets n'est à portée de main de Corvus (`spatial.proche`).
- Combien de tours finissent par un refus `HorsDePortee` et ce qu'ils ont coûté en appels (lot 5 du plan).

## Livraison
Branche `codex-prompt-mesure` : un outil de mesure réutilisable s'il sert aux lots suivants (`tools/mesure_prompt.py`, avec
un test court), `docs/taches/rapport-codex-149-prompt-mesure.md` (une page : tableaux par voie, causes de divergence classées,
gain attendu de chaque lot L1 à L8) et une entrée dans `docs/etat-dev.md` (« Branche `codex-prompt-mesure`, non fusionnée »).
Commits signés si une clé est configurée, branche poussée (pas `main`). Bruts dans `C:\Users\msics\donjon\artifacts\prompt-149\`.
