# Tâche Codex 157 (force 4f, restes) : traîner, enfermer et le geste improvisé sans faux refus

Petit lot de correction issu du lot 147 et de la vérification Luna `cdaf371` (lot 153). Lot de 30 à 45 minutes (`AGENTS.md`).
**Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste, deux sur le laptop : au plus
2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche `couverture_action.py` (dossier et règles
de la contre-revue), `consignes.py` (lignes des gestes de force), `tenir.py`/`operations.py` pour les titres et informations de
plan, et leurs tests ; **pas** `mj.py`, `sources.py`, les fournisseurs (lots 150, 151), `narration.py` (lot 156), ni
`defense.py`/`deliberation.py`/`planification.py` (lot 155). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 147 (force 4f) et 153 (section « Force, critère non atteint »)
et leurs fils (`C:\Users\msics\donjon\artifacts\verif-luna-cdaf371\`, scripts `force-4f-trainer`, `force-4f-enfermer`,
`force-4f-improvise`), puis la contre-revue d'action et la façon dont le lot 154 a corrigé le titre d'un dépôt au sol.

## Les cas (lot 153)
- **Traîner** (5/4 appels) : la contre-revue rejette le pas sud malgré la destination du corps ; elle oppose « crypte » à
  « Salle des vannes » (identifiant `crypte`, nom public différent), puis Luna inverse le pas ou prétend le corps hors de portée.
- **Enfermer** (2/3 appels, refus de l'intention) : porte ouverte à portée, passe porté compatible, mais Luna exige d'approcher
  Bram ou propose de le déplacer, sans verrouiller ; la porte du bureau est confondue avec un meuble.
- **Geste improvisé** (6/4 appels) : `frapper` → `improviser` refusé, ou `tuer` répété sur une cible capable de se défendre.

## L'invariant
**Ce que reçoit la contre-revue d'un geste de force (titre, information, dossier) désigne chaque lieu et chaque objet par son
nom public, avec l'effet que le moteur établit (où va le corps, quelle porte se verrouille sur qui), de sorte qu'un plan conforme
à la demande n'est pas rejeté ; et les consignes décrivent enfermer comme verrouiller une porte réelle derrière la personne.**
Même voie que le lot 154 (titre et dossier communs) ; aucune consigne d'audit ou exception propre à une scène, un objet ou un
personnage. Le geste improvisé : n'ajoute aucune règle lexicale ; si la contre-revue ou la consigne ne dit pas que `tuer` exige
une cible sans défense (le moteur le refuse avec `attendu`), corrige ce qui manque au contrat commun, sinon consigne la limite.

## Vérification
- Tests MJ simulé/console après rechargement : dossier de contre-revue de traîner (nom public de la salle d'arrivée), d'enfermer
  (porte et personne), plan conforme admis ; un plan réellement non conforme toujours rejeté.
- Luna, **deux passes** des trois scripts `force-4f-trainer`, `-enfermer`, `-improvise` et une passe des huit autres bancs de
  force ; référence `cdaf371` relue du cache ; critère : trois appels au plus par saisie, aucun état corporel inventé.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-force-restes` poussée (pas `main`). `docs/plan-force.md`
(4f), `docs/etat-dev.md` (« Branche `codex-force-restes`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-157-force-restes.md`.
