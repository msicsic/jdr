# Tâche Codex 214 (A6, suite) : racheter son bien à celui qui le détient

Suite des lots 192 (projet `récupérer` né d'un portage illégitime constaté) et 207 (la victime réclame d'abord par la parole
`reclamer`, fusionné). Limite relevée par les deux rapports : **« le graphe n'achète qu'au propriétaire, sans rachat au voleur »**
(`planification.gestes`, branche d'achat, condition `v.proprietaire[o] == porteur`). Une victime dont la réclamation est refusée
n'a donc que la reprise (faute, violence). Racheter son propre bien à celui qui le détient (une rançon, un arrangement) est un
moyen plus riche et sans faute. Priorité de l'utilisateur : richesse des comportements des PNJ.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le laptop** (`C:\Users\msics\donjon`, l'utilisateur y travaille) :
au plus 2 processus, priorité réduite. Fichiers : `planification.py` (le geste d'achat seulement), `echanges.py` (vente par le
détenteur), `biens.py`, et leurs tests. **Pas** `deliberation.py`, `agendas.py` (lot 213), `social.py`, `esprits.py`, `pnj.py`
(lot 206), `ouie.py`, ni le MJ. **Bruts dans `C:\Users\msics\donjon\artifacts\racheter-214\`.** Termine par `LOT TERMINÉ`
(résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 192 et 207, 107 (contreparties), 110 (propositions redites), 57 (offre sensée), puis la branche
d'achat de `planification.gestes`, `echanges` (vente, `refuse_achat`, `evaluer_proposition`) et `biens` (propriété, permissions).

## L'invariant
**Le propriétaire d'un bien porté par un autre peut le lui racheter, par le même geste d'achat que tout achat, au prix que le
détenteur accepte selon la règle commune de vente (ses valeurs, sa relation, ce que le bien lui sert, la garde) ; la remise rend le
bien à son propriétaire (possession, permissions et croyances à jour, projet `récupérer` atteint) ; le détenteur qui vend ce qui
n'est pas à lui commet la faute ordinaire de garder ou vendre le bien d'autrui selon son honnêteté, sans règle nouvelle.** Le
rachat se compare aux autres moyens du projet par la recherche commune (prix, faute, violence) ; un rachat refusé est retenu selon
sa cause (lot 110). Même règle pour le joueur (il peut racheter son bien ou se voir proposer un rachat) ; aucune règle propre à un
personnage, un bien ou un scénario. La dénonciation reste hors lot.

## Vérification
- Tests après rechargement : Gorm rachète à Brune le bois du guet qu'elle a pris (capture du lot 207 à 151 sur `9904574`, ou scène
  d'auteur équivalente sur la base actuelle) après une réclamation refusée ; un autre cas de même nature (autre bien, autre
  scénario) ; détenteur qui refuse de vendre ; propriétaire sans pièces ; joueur détenteur et joueur propriétaire ; même laps d'un
  bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) × quatre graines, références du cache, **avec le compteur 199** : rachats,
  réclamations, reprises, S/F/D du lot 183, coût (`tools/mesure_cout.py`, mine 4 h : pas de hausse notable attendue) ; aucune
  usurpation, plantage ni boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-racheter-bien` poussée (pas `main`) ;
`docs/etat-dev.md` (« Branche `codex-racheter-bien`, non fusionnée ») ; rapport d'une page
`docs/taches/rapport-codex-214-racheter-bien.md`.
