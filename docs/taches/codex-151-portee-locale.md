# Tâche Codex 151 (plan prompt, L5) : hors de portée, le moteur répond seul

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le laptop** (`C:\Users\msics\donjon`, Luna connectée ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
Un autre lot tourne sur ce poste (lot 150, assemblage des requêtes dans `mj.py`, `sources.py`, `fournisseurs/`) : au plus
2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche **seulement** la boucle de validation des
propositions dans `mj.py` (refus `HorsDePortee`) et `proximite.py` si besoin, avec leurs tests ; **pas** l'assemblage des
requêtes, `sources.py`, les fournisseurs, les consignes ni le schéma. Termine ton dernier message par `LOT TERMINÉ` (résumé
d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, **`docs/plan-prompt.md`** (décision 4), `docs/contrat-mj.md`, le rapport du lot 44 (portée des improvisations,
« Approche-toi… »), puis `mj.py` : la boucle de validation (`HorsDePortee`, `correction_utilisee`, l'explication finale par
`_echanger` puis son audit, `reponse_du_moteur`, le cas `faisabilite`) et `proximite.exiger`.

## La décision (utilisateur, 2026-10-27)
Refus local déterministe, **pas** de déplacement automatique : le joueur déplace Corvus lui-même (le trajet a un coût en temps,
bruit et lignes de vue). Aujourd'hui, une proposition refusée par `HorsDePortee` part dans une explication rédigée par Luna puis
auditée (deux appels de plus) pour paraphraser « Approche-toi de … ».

## L'invariant
**Quand une proposition valide par ailleurs n'échoue que parce que sa cible n'est pas à portée de main, le joueur lit le refus
du moteur (`reponse_du_moteur`), exact, sans appel d'explication ni audit, comme pour une question de faisabilité ; rien n'est
exécuté ni sauvegardé d'autre.** Une seule cause par refus, avec `attendu` pour le MJ ; plusieurs cibles hors de portée sont
dites dans l'ordre. Ne change pas : une proposition dont la cible est mal choisie (refus d'une autre nature) suit encore la
correction ordinaire ; une parole attendue reste prononcée par le moteur ; le refus ne nomme que des entités perçues ou connues
(aucune fuite). Aucun mot-clé, aucune règle propre à un objet ou un scénario.

## Vérification
- Tests MJ simulé/console après rechargement : le cas de la barricade à six mètres (Relais ou auberge) et un autre geste
  (prendre, découper) sur une cible éloignée : réponse du moteur, nombre d'appels (interprétation seule), état inchangé ;
  la même saisie une fois Corvus adjacent : geste préparé ; une cible mal typée garde la correction ordinaire.
- Luna, **une passe** des bancs qui exercent la portée (`sous-obstacle-*`, `atelier`, `relais`) ; référence `cdaf371` relue du
  cache ou jouée une fois ; appels et secondes par tour MJ, tours finissant sur « Approche-toi ».
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-portee-locale` poussée (pas `main`).
`docs/contrat-mj.md` (la règle de portée), `docs/plan-prompt.md` (L5 fait), `docs/etat-dev.md` (« Branche
`codex-portee-locale`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-151-portee-locale.md`.
