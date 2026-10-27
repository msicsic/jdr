# Tâche Codex 207 (A6, suite) : la victime réclame son bien avant de le reprendre

Suite du lot 192 (`docs/taches/rapport-codex-192-naissance-evenement.md`, « Limites ») : un portage illégitime constaté fait
naître le projet `récupérer {objet, qui}`, mais le seul moyen du graphe est de **porter le bien** (le reprendre, au prix commun
de la faute et de la violence). Manque la **réclamation spécifique du vol** : demander au porteur de rendre ce qu'il a pris,
comme le fait déjà le joueur par la parole typée `reclamer`. Le lot 200 a produit la première récupération née en nuit libre
(Gorm, bois du guet pris par Brune, crue 7, né à 152, atteint à 228) : c'est le cas réel. Priorité de l'utilisateur : richesse
des comportements des PNJ.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le laptop** (`C:\Users\msics\donjon`, l'utilisateur y travaille) :
au plus 2 processus, priorité réduite. Fichiers : `agendas.py`, `echanges.py`, `biens.py`, `pnj_propositions.py` si la demande y
vit, et leurs tests. **Pas** `planification.py`, `deliberation.py`, `eau.py` (lot 205), `ouie.py` (lot 195), `social.py`,
`esprits.py`, `pnj.py` (lot 206), ni le MJ : la réclamation est un **recours hors de la recherche**, comme les propositions
« faute de mieux » (lot 45) et le service spontané (lot 120), placé avant la reprise par la faute. **Bruts dans
`C:\Users\msics\donjon\artifacts\reclamer-207\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 192, 184 (projets et recours comparés), 45 et 120 (recours hors recherche), 77 (contre-offre),
puis le contenu `reclamer` (`paroles.py`, `biens.reclamer_dette`), `agendas` (`récupérer`) et le choix du recours.

## L'invariant
**Le porteur d'un projet `récupérer` demande d'abord au porteur cru de lui rendre son bien, par la parole typée commune `reclamer`
(celle du joueur), quand il peut lui parler sans danger qu'il croit ; le porteur décide par la règle commune (honnêteté, relation,
garde, ce que le bien lui sert), rend le bien par une remise réelle ou refuse ; un refus est retenu selon sa cause et ouvre les
moyens existants (reprise, au prix commun de la faute) ; une restitution atteint le projet.** Croyances du réclamant seulement ;
même règle quand le porteur est le joueur (il reçoit la réclamation et peut rendre) ; aucune règle propre à Gorm, Brune, un bien
ou un scénario. Le rachat au voleur et la dénonciation restent hors lot.

## Vérification
- Reproduire d'abord le cas réel du lot 200 (crue 7, capture rechargeable juste avant 152) et dire ce que fait Gorm sur la base.
- Tests après rechargement : la victime réclame et obtient restitution ; refus retenu puis reprise par les moyens existants ; le
  joueur porteur reçoit la réclamation et rend ou refuse ; un autre cas de même nature (autre bien, autre scénario) ; aucune
  réclamation à qui l'on croit absent ou dont on a peur ; même laps d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) × quatre graines, références du cache, **avec le compteur des
  changements d'avis** : réclamations, restitutions, reprises, S/F/D du lot 183 ; aucune usurpation, plantage ni boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-reclamer-vol` poussée (pas `main`) ;
`docs/etat-dev.md` (« Branche `codex-reclamer-vol`, non fusionnée ») ; rapport d'une page
`docs/taches/rapport-codex-207-reclamer-vol.md`.
