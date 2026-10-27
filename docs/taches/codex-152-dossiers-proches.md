# Tâche Codex 152 (plan prompt, L4) : les dossiers techniques bornés à la proximité

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (`C:\Users\msics\donjon`, Luna connectée ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
Deux autres lots tournent sur ce poste : au plus 2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot
touche les fonctions `dossier` d'`artisanat.py`, `franchissement.py`, `obstacles.py` (dossier seulement, **pas** les trajets ni
`cout_route`) et `espace.py` si besoin, avec leurs tests ; **pas** `mj.py`, `sources.py`, les fournisseurs, `consignes.py`
(lots 150 et 151 en cours sur le laptop), ni `agendas.py`, `deliberation.py`, `planification.py` (lot 146 b). Termine ton
dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, **`docs/plan-prompt.md`** (décisions 1 et 4, L4), `docs/contrat-mj.md`, les rapports des lots 19
(`sous-obstacle`) et 44 (portée des improvisations), puis les quatre `dossier(m)` : `espace.dossier` borne déjà à
`m.visible(id) and spatial.proche(m, id)` ; `artisanat.dossier` et `franchissement.dossier` lisent `m.accessible` (toute la
salle), `obstacles.dossier` lit `m.designable`.

## L'invariant (décision de l'utilisateur, 2026-10-27)
**Un dossier technique (atelier, franchissement, passages d'obstacles, espace) ne décrit que des objets perçus et à portée de
main de Corvus (`spatial.proche`) ; un objet perçu mais éloigné reste un repère dans la vue, sans affordance d'atelier ni de
passage.** La salle n'est plus l'unité de capacité côté MJ ; le moteur garde ses salles. Les refus du moteur sur une cible
éloignée ne changent pas (le lot 151 les rend locaux). Ce qui est porté par Corvus reste à portée. Aucune règle propre à un
objet, un lieu ou un scénario ; aucun changement des consignes (les règles conditionnelles disparaîtront avec L3, ici elles
apparaissent seulement quand un dossier non vide est envoyé).

## Vérification
- Tests MJ simulé/console après rechargement : au Relais et à l'atelier, Corvus à distance d'un obstacle et d'un établi
  (dossiers absents, objets toujours dans la vue), puis adjacent (dossiers présents, geste préparé) ; une perche portée reste
  dans l'atelier ; aucune fuite d'entité non perçue.
- Mesure : avec `tools/mesure_prompt.py` du lot 149 s'il est livré (sinon par l'instrumentation existante), part des appels où
  un dossier est envoyé et taille de `faits`, avant/après, sur les mêmes scènes rejouées.
- Luna, **une passe** des bancs qui exercent ces dossiers (`atelier`, `relais`, `sous-obstacle-*`) ; référence `cdaf371` relue
  du cache ou jouée une fois ; appels et secondes par tour MJ, refus, aucune affordance distante proposée par Luna.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-dossiers-proches` poussée (pas `main`).
`docs/contrat-mj.md` (dossiers bornés), `docs/plan-prompt.md` (L4 fait), `docs/etat-dev.md` (« Branche
`codex-dossiers-proches`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-152-dossiers-proches.md`.
