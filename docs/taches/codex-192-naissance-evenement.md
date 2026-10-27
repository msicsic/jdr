# Tâche Codex 192 (A6, deuxième volet) : un projet naît d'un tort subi

Priorité de l'utilisateur, 2026-10-27 : la richesse du comportement des PNJ (ordre A6 → 3d → A5). Le premier volet d'A6
(lots 184 et 184 b, fusionnés : `agendas.NAISSANCES`, `argent_projet`) fait naître un projet d'une dette crue. Ce volet ajoute
**la naissance par événement** de `docs/plan-agendas.md` § 6.5 : un vol subi et la rancune font naître « récupérer » ou
« nuire ». Lot de 30 à 45 minutes (`AGENTS.md`) ; livraison partielle permise si elle dit ce qui reste. Pas de Luna.

**Poste : le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots
calculent sur ce poste (180 c : `narration.py`, `mj.py` ; 191 : `social.py`) : au plus 2 processus, priorité réduite. Fichiers :
`agendas.py`, `argent_projet.py` si utile, `deliberation.py`, une sorte d'agenda ajoutée au vocabulaire commun si elle manque, et
leurs tests ; **pas** `social.py` (191), `narration.py`/`mj.py` (180 c), `presence.py`/`planification.py` hors des seules lectures
nécessaires (189 les touche sur le laptop : si tu dois changer `planification.py`, dis-le avant). **Bruts dans
`C:\Users\msics\donjon\artifacts\naissance-192\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-agendas.md` (§ 3, § 4, § 6.1 à 6.5, § 10, § 11 « ce qui serait un script »), `docs/plan-relations.md`
(épreuves, rancune), les rapports 184, 120 (service rendu, réparation), 121 (disputes), 167 à 167 c, 175, 179 (garder et ses
fins), et la revue vierge 187 (§ 1 et P6), puis `agendas.py`, `argent_projet.py`, `relations.EPREUVES`, `esprits.constater_possession`.

## L'invariant
**Un tort subi et connu de la victime (un bien à soi vu aux mains d'un autre sans permission, ou constaté disparu avec un
auteur identifié) fait naître, par la même table commune et la même voie que le premier volet, un projet « récupérer » visant
ce bien, dont le poids vient de la valeur du bien et des valeurs du PNJ (ambition, honnêteté, douceur, fierté, rancune envers
l'auteur), jamais d'une personne ni d'un scénario.** Ses sous-buts sont les moyens communs existants, comparés sur la même
échelle : réclamer (parole `reclamer`), demander, acheter, reprendre sans faute un bien qui est à soi, avertir un tiers ou un
protecteur ; frapper ou nuire seulement selon la douceur et au prix commun de la violence, sans geste nouveau. Le projet finit
quand le bien est revenu, constaté détruit ou consommé (lot 175), ou que la victime y renonce selon sa ténacité (VOL) ; il dort
sans moyen cru. Aucun accès à ce que la victime ignore (auteur non vu, lieu non su).

Hors lot (à dire dans le rapport) : « nuire » sans bien à récupérer, « punir », « rallier », l'occasion (mercenaire) et le
soupçon déduit (auteur non vu).

## Vérification
- Tests après rechargement : un vol réel vu par sa victime dans une nuit existante (cherche-le : auberge, Lucien/Anselme ;
  Relais ou crue, Brune et la réserve de Gorm ; capture rechargeable) fait naître le projet et la victime agit par un moyen
  commun ; un autre cas de même nature (autre scénario ou données de test) ; une victime qui ignore l'auteur : aucun projet ;
  bien rendu, détruit ou consommé : fin ; refus retenu selon sa cause (lot 110) ; plafond de trois actifs ; même laps d'un
  bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, quatre scénarios × quatre graines (références du cache) : projets nés, moyens employés, aucune usurpation,
  plantage ni boucle nouvelle ; richesse S/F/D du lot 183 (`C:/Users/msics/donjon/artifacts/dormants-183/analyser.py`, mêmes
  définitions) à base identique ; coût (`tools/mesure_cout.py`, mine ou auberge 4 h) relevé.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-naissance-evenement` poussée (pas `main`) ;
`docs/plan-agendas.md` (A6 : fait et reste), `docs/etat-dev.md` (« Branche `codex-naissance-evenement`, non fusionnée ») ;
rapport d'une page `docs/taches/rapport-codex-192-naissance-evenement.md`.
