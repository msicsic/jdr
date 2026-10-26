# Tâche Codex 120 (3e) : regagner la confiance en rendant service, faute de mieux

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). Pas de Luna. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
**Un seul poste** : priorité réduite, au plus 2 processus de calcul ; le lot 121 (disputes : `social.py`, `ouie.py`, `relations.py`)
tourne en même temps. Ce lot touche `pnj_propositions.py`, `propositions.py`, `echanges.py`, `relations.py` (épreuve du service
rendu, s'il le faut) ; pas `planification.py` hors appel des devis existants, ni `social.py`/`ouie.py`. Termine ton dernier message
par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-relations.md` (§ 7.2 : décision du 2026-10-24 « faute de mieux », « Regagner la confiance », décision 14),
les rapports des lots 45, 107, 110 et 115 (tâche promise), puis `donjon/pnj_propositions.py` (`recours`), `donjon/echanges.py`
(`devis_service`, `evaluer_proposition`, refus retenus), `donjon/relations.py` (`EPREUVES`, bandes).

## Ce qui manque
Un PNJ refusé **par méfiance** (ou rancune) n'a aujourd'hui aucun moyen de regagner la confiance de l'autre : il redemande au délai,
ou se tourne vers la faute. Le plan prévoit `rendre_service` : rendre d'abord un service que l'autre croit utile (lui donner ce qu'il
croit lui manquer, tenir une tâche pour lui), ce qui relève sa relation d'une bande et rouvre la demande (« Brune refusée par
méfiance peut recharger le brasero de Gorm avant de lui redemander une part »).

## Choix de conception (à respecter)
La décision 14 recommandait un geste de la recherche ; la décision du 2026-10-24 (A2b) fait de la proposition un **recours de
dernier ressort**, pour le coût et la plausibilité. **Même cadre ici** : `rendre_service` n'est pas un geste comparé dans chaque
état de la recherche ; c'est un recours tenté après un refus de méfiance ou de rancune, quand ses moyens ordinaires sans faute
n'aboutissent pas, avant toute faute contre ce même personnage. Dis-le dans `docs/plan-relations.md`.

## L'invariant
**Un service rendu sans contrepartie est une épreuve de relation commune** : le bénéficiaire qui le **constate** (voit le feu
rechargé, reçoit le bien, voit la tâche faite) éprouve « service rendu » (confiance et affection relevées par la table
`EPREUVES`, hystérésis des bandes), joueur compris quand c'est lui qui rend le service ; ce qui lève le refus retenu « méfiance »
de ce demandeur (règle des refus retenus : un moyen nouveau). Le recours choisit un service que le proposant peut faire **seul**
(`devis_service`) et que l'autre croit utile (besoin cru, mêmes conditions que la tâche promise du lot 115), une seule tentative par
couple refus/besoin. Aucune règle propre à Brune, Gorm ou au brasero.

## Vérification
- Tests après rechargement, même laps découpé : Brune refusée par méfiance recharge le brasero de Gorm, Gorm le voit, sa confiance
  remonte d'une bande, la redemande est acceptée ; un autre cas (auberge ou mine) ; un service que l'autre ne constate pas ne relève
  rien ; un service impossible n'est pas tenté ; le joueur qui rend un service relève aussi la relation.
- Banc rapide 4 h, quatre scénarios × quatre graines contre la base (cache, sinon calculée une fois) : services rendus / constatés /
  demandes accordées ensuite, aucune usurpation ni boucle ; CPU base/branche lancés ensemble (au bruit près).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md`, `docs/etat-dev.md` (« Branche `codex-rendre-service`, non
fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-120-rendre-service.md`.
