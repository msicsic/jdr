# Tâche Codex 93 : où part le temps d'un tour MJ, et le premier levier qui le réduit sans perdre de contrôle

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). **Luna disponible** : copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth` ; `tools/banc_multi.py --connexion chatgpt`. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 3 processus de calcul, Luna en
4 exécutions au plus ; les lots 90 et 92 (planificateur, bancs) tournent en même temps. Ce lot touche le MJ (`donjon/mj.py`,
`donjon/fournisseurs/openai.py`, `donjon/narration.py`, `tools/banc_multi.py`/`banc_parties.py` pour la mesure), pas
`planification.py` ni `deliberation.py`. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Objectif de l'utilisateur** : le temps avant la réponse au joueur, donc le nombre d'appels par tour et la durée de chacun,
jamais au prix du contrat du MJ (`AGENTS.md`, « Contrat du MJ »). Luna reste `gpt-6-luna`, la comparaison de modèles reste
désactivée.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées des lots 79, 85 (non fusionné : cache de préfixe, +20 % d'appels), 89, 91),
`docs/contrat-mj.md`, le rapport du lot 91 (`docs/taches/rapport-codex-91-un-appel-de-moins.md`), puis `donjon/mj.py` (boucle d'un
tour : interprétation, préparation, récit, audits, relances), `donjon/fournisseurs/openai.py` (requête, `reasoning.effort`,
`prompt_cache_key`), `donjon/transport_openai.py`.

## D'abord, mesurer
Sur l'intégration **119169c** (lot 91 fusionné), deux passes de `relais`, `crypte`, `atelier`, `echanges`, `soir-appel`,
`noms-dialogue` (référence rangée dans le cache) : pour **chaque appel**, sa fonction (interprétation, récit, audit narratif,
fidélité, portée, contre-revue, révision), sa durée, son premier jeton, les jetons d'entrée (dont en cache), de sortie et de
réflexion ; par tour, le chemin critique (les appels successifs qui font attendre le joueur). Ajoute ce relevé au fil
(`banc_parties --fil`) et au résumé de `banc_multi` s'il n'y est pas. Tableau : secondes par tour et par fonction, part de
chaque fonction dans l'attente, appels qui pourraient partir en même temps.

## L'invariant (choisi d'après la mesure, un seul)
**Un appel ne fait attendre le joueur que s'il peut changer ce que le joueur lira.** Choisis le premier levier que la mesure
désigne, parmi ceux qui ne relâchent aucun contrôle : (a) réglage par fonction déjà prévu par le fournisseur (`reasoning.effort`
plus bas pour un appel de contrôle dont la réponse est un rapport typé court, si la qualité des verdicts ne baisse pas) ;
(b) deux appels indépendants lancés en même temps au lieu de l'un après l'autre (même transport, mêmes entrées, même ordre
d'application des résultats) ; (c) entrée inutile retirée d'un appel (taille d'entrée, jetons de sortie bornés par le schéma).
Pas de contrôle supprimé ni affaibli, pas de nouveau mode, pas d'exception de scénario. Si le seul levier important touche le
contrat (un audit sauté), **n'implémente rien** et termine par `QUESTION :` avec la mesure.

## Vérification
- Tests après rechargement avec MJ simulé pour la mécanique touchée (ordre d'application, refus et relances inchangés).
- Luna, **deux passes** des six scripts, intégration 119169c (cache) contre la branche, lancées dans les mêmes conditions :
  secondes par tour (médiane et moyenne), appels par tour, relances, refus, replis, verdicts d'audit comparés (aucun refus juste
  perdu : relis les refus de la référence et vérifie qu'ils tombent encore).
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md` si le contrat de l'appel change, `docs/etat-dev.md`
(« Branche `codex-latence-appels`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-93-latence-par-appel.md`
(le tableau de mesure, le levier, le gain, les limites).
