# Tâche Codex 281 : un but de protection nomme le protégé

Le diagnostic 279 (`docs/taches/rapport-codex-279-coups-crue-2024.md`, fusionné ; bruts et captures
`C:\Users\msics\donjon\artifacts\coups-279\`) établit, après le lot 222, que `planification.reagir` rend un but
`proteger` dont `qui` désigne **l'agresseur** (Brune) alors que Gorm protège **Aubin**. `recit_pnj.but_en_mots` affiche
« protéger Brune » et `paroles.engagements_enregistres` fournit au MJ « intention en cours : protéger Brune » : une
question à Gorm pendant ou après l'échauffourée produirait une affirmation incompatible avec l'état.

## L'invariant
**Un but de protection nomme le protégé ; l'agresseur reste la cible du plan. Aucun récit, relevé, texte fourni au MJ
ni souvenir ne présente l'agresseur comme le protégé.** Contrat commun entre le but, son plan, sa restitution (récit,
paroles, rejeu, audit) et la sauvegarde. Aucune branche propre à la crue, à Brune ou à un objet. Si d'autres lecteurs
du champ `qui` d'un but `proteger` (délibération, défense, hystérésis, sonde 219) en dépendent, accorde-les tous et
liste-les ; les anciennes sauvegardes ne sont pas migrées.

Lot de 30 à 45 minutes. Pas de Luna, pas de suite complète (le superviseur la lance). **Poste : le PC fixe**, deux
processus au plus, priorité réduite.

**Fichiers attendus** : `donjon/planification.py` (`reagir`), `donjon/recit_pnj.py`, `donjon/paroles.py`, lecteurs du
but en raccord ; `tools/audit_nuits.py`, `tools/detecter_changements_avis.py` si le relevé en dépend. Le lot 277, non
fusionné, modifie `planification.py` (recours et gestes sociaux) et `echanges.py` : ne touche pas ces fonctions.

## Vérification
- Capture 279 avant le premier coup (`0bad227`, crue 2024) rechargée : but `proteger qui=aubin`, cible du plan Brune,
  récit et texte au MJ justes ; la scène se déroule à l'identique (mêmes gestes). Autre cas de même nature (autre
  protecteur ou scénario, ou épreuve 4c de `test_defense`). Monde, rendu et scène identiques après recharge.
- Tous les fichiers de tests qui lisent ce libellé ou ce champ (trouve-les par recherche).
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes`), cinq scénarios × quatre graines, contre l'intégration à ta
  base : seuls le champ et les textes du but de protection peuvent changer ; tout autre écart est à expliquer.

## Livraison
- Branche `codex-but-protection` poussée ; si la poussée échoue depuis le PC fixe, laisse le commit local et donne son
  hash, sans passer par l'API GitHub. Rapport d'une page `docs/taches/rapport-codex-281-but-protection.md` ; entrée
  « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\protection-281\`. Termine par
  `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
