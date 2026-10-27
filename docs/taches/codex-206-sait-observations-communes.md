# Tâche Codex 206 : un PNJ ne dit ou tait une nouvelle que d'après ce qu'il croit de l'auditeur

Limite déterminante du lot 191 (`docs/taches/rapport-codex-191-deja-entendu.md`, « Limite déterminante ») : le contrôle
historique `social._sait`, appelé par `social.bavarder`, lit encore **le savoir réel de l'auditeur** pour décider de lui taire
une nouvelle. Le locuteur se tait donc parce que l'autre sait, sans avoir aucun moyen de le savoir : une fuite d'information
privée dans la décision d'un PNJ, contraire au principe de subjectivité (chacun agit sur ses propres croyances). Au lot 191,
retirer `_sait` ou le remplacer par une vue commune a provoqué des régressions de défense et de trajets ; l'essai a été retiré.
Ce lot reprend ce contrat. Priorité de l'utilisateur : richesse et justesse des comportements des PNJ.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le laptop** (`C:\Users\msics\donjon`, l'utilisateur y travaille) :
au plus 2 processus, priorité réduite. Fichiers : `social.py`, `esprits.py` (registres des faits dits et entendus, observations
communes), `pnj.py` **hors `_abriter`** (perception et témoins, si l'observation commune l'exige) et leurs tests ; **pas**
`eau.py`, `deliberation.py`, `planification.py`, `route_admissible.py` (lot 205), ni `ouie.py` (lot 195), ni le MJ.
**Bruts dans `C:\Users\msics\donjon\artifacts\sait-206\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 191 (en entier), 64 et 108 (faits dits, valeurs redites), 55 (constats partagés), 88 (le locuteur
ne consulte plus la prévision privée de l'auditeur : le même principe pour l'eau), puis `social._sait`, `bavarder`, `nouvelles`,
`_a_dire`, les registres de `esprits` et les témoins de `pnj`.

## L'invariant
**Un PNJ décide de dire ou de taire une nouvelle d'après ses seules croyances sur ce que l'auditeur sait : ce qu'il lui a déjà
dit, ce qu'il l'a entendu dire ou dire à d'autres, et ce qu'il sait que l'auditeur a observé avec lui (une observation commune :
ils étaient tous deux témoins du même fait, et le locuteur percevait l'auditeur à ce moment), jamais le savoir réel de
l'auditeur.** Une nouvelle que l'auditeur connaît déjà par une voie que le locuteur ignore peut donc lui être redite ; c'est
voulu, et la réception commune la traite comme une confirmation. Même règle pour tout PNJ, et pour ce que les PNJ disent au
joueur ; aucune règle propre à un personnage, un fait ou un scénario.

## Vérification
- Reproduire d'abord les régressions du lot 191 (défense et trajets) quand `_sait` est retiré : dire ce qu'elles lisaient
  vraiment (quelle information l'auditeur recevait ou non) et en tirer l'observation commune nécessaire ; ne pas réancrer les
  tests historiques pour les faire passer.
- Tests après rechargement : un PNJ redit une nouvelle à un auditeur qui la sait par une voie qu'il ignore (cas réel tiré d'une
  nuit, et un autre de même nature) ; il la tait à un auditeur qu'il a vu témoin du même fait ; registre des faits dits
  conservé ; même laps d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) × quatre graines, références du cache, **avec le compteur des
  changements d'avis** : confidences, avertissements redits, avis, retours suspects ; aucune usurpation, plantage ni boucle
  nouvelle (répétitions textuelles comprises).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-sait-observations` poussée (pas `main`) ;
`docs/etat-dev.md` (« Branche `codex-sait-observations`, non fusionnée ») ; rapport d'une page
`docs/taches/rapport-codex-206-sait-observations.md`.
