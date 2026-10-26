# Tâche Codex 122 (3e) : passer par un intermédiaire, faute de mieux

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). Pas de Luna. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
**Un seul poste, déjà chargé** : une vérification d'intégration tourne en fond (deux processus) ; pour ce lot, **un seul
processus de calcul** à priorité réduite (`tools/tests.py --processus 1`, `comparer_bancs --processus 1`). La connexion du
poste est intermittente : si un appel échoue, reprends là où tu en étais. Termine ton dernier message par `LOT TERMINÉ`
(résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-relations.md` (§ 7.2 : « Intermédiaires », « Regagner la confiance », décision du 2026-10-24
« faute de mieux » ; 3e), les rapports des lots 45, 77, 107, 115 et 120, puis `donjon/pnj_propositions.py` (`recours`,
`rendre_service`, `plan_recours`), `donjon/echanges.py` (`devis_service`, `evaluer_proposition`, tâches confiées, refus
retenus), `donjon/agendas.py`, `donjon/relations.py`.

## Ce qui manque
Un PNJ refusé par méfiance ou rancune peut désormais rendre un service avant de redemander (lot 120). Le plan prévoit
une seconde voie : **passer par quelqu'un que l'autre croit**. « Ilse, que Gorm croit, lui demande de servir Brune,
qu'il refuse en direct. » Obtenir un objet porté par autrui est une tâche confiable (« remis », condition
`{"objet", "remettre": pour}`) ; servir quelqu'un l'est déjà (`{"objet", "servir"}`).

## Choix de conception (à respecter)
Même cadre que les lots 45 et 120 : **un recours de dernier ressort**, pas un geste comparé dans chaque état de la
recherche. Il est tenté après un refus retenu pour méfiance ou rancune, quand les moyens ordinaires sans faute
n'aboutissent pas, avant toute faute envers ce même personnage. L'ordre entre `rendre_service` et l'intermédiaire suit
le devis le moins cher pour le demandeur. Dis-le dans `docs/plan-relations.md`.

## L'invariant
**Une demande portée par un intermédiaire est jugée par la règle commune des demandes, avec la relation de celui qui la
porte.**
- Le demandeur choisit un intermédiaire d'après **ses propres croyances** : quelqu'un qu'il croit en bons termes avec la
  cible (relations qu'il a observées ou entendues, jamais l'attitude privée de la cible) et qui ne se méfie pas de lui ;
  un seul candidat, une seule tentative par couple refus/besoin, sauvegardée.
- L'intermédiaire accepte ou refuse la commission par la règle des tâches confiées (son altruisme, son lien avec le
  demandeur, ce qu'elle lui coûte par `devis_service`), sans jet de plus que la règle commune.
- Acceptée, il planifie la demande avec ses propres moyens et relations ; la cible juge **l'intermédiaire** par la règle
  commune des demandes (`chance_demande`, refus retenus), pas le demandeur d'origine. Le bien obtenu est remis au
  bénéficiaire (« remis ») ou le service lui est rendu (« servir »), par les remises communes ; rien n'est remis à
  l'acceptation.
- Le récit et la chronique disent la chaîne ; la cible apprend pour qui elle cède seulement si on le lui dit.
  Aucune règle propre à Ilse, Gorm, Brune ni à un scénario.

## Vérification
- Tests après rechargement, même laps découpé : Brune refusée par Gorm (méfiance) demande à Ilse ; Ilse accepte, Gorm
  lui cède la part, Ilse la remet à Brune ; un autre cas (mine ou auberge) ; un intermédiaire dont la cible se méfie
  aussi échoue sans boucle ; un intermédiaire qui se méfie du demandeur refuse la commission ; aucune lecture des
  relations privées de la cible.
- Banc rapide 4 h, quatre scénarios × quatre graines contre la base (cache, sinon calculée une fois) : intermédiaires
  sollicités / acceptés / aboutis, aucune usurpation ni boucle.
- Suite complète une fois à la fin (`tools/tests.py --processus 1`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md`, `docs/etat-dev.md` (« Branche
`codex-intermediaires`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-122-intermediaires.md`.
