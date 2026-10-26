# Tâche Codex 97 : jamais le planificateur des PNJ pour le joueur (plantage d'une proposition)

Petit lot de correction (`AGENTS.md`, « Rythme des lots »). **Luna disponible** pour une passe de contrôle, copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** :
priorité réduite, au plus 2 processus de calcul ; le lot 92 c (`planification.py` : graphes repris, certificat d'absence) et le
lot 94 (vérification lourde) tournent en même temps : ne touche pas aux graphes ni au certificat. Termine ton dernier message
par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

## Le constat
Pendant une partie Luna du lot 96 (deuxième script après `relais`, sans doute `crypte`, code de `codex-relances` = intégration
**870eea4** à une ligne de schéma près), le jeu a planté. Trace complète :
`C:\Users\msics\donjon\artifacts\plantage-profil-joueur\journal.txt`. Chaîne : `mj._echanger_prepare` → `paroles.preparer_parole`
→ `_proposer(travail, "joueur", auditeur, …)` → `echanges.proposer` → `evaluer_proposition` → `_livraison_proposition` →
`_devis_proposition` → `devis_service` → `planification.devis_pulsion` → `_pulsion` → `_remettre` → `chercher` → `gestes` →
`Vue.agissables` → `Vue.pertinent` : `profil(monde, id)["capacites"]` sur un `profil` nul : la recherche des PNJ est lancée
pour un personnage sans profil, vraisemblablement **le joueur** comme donneur d'une remise promise.

## L'invariant
**Le planificateur des PNJ ne planifie que pour un PNJ.** Quand l'évaluation d'une proposition doit juger si le joueur peut
livrer ce qu'il promet, elle le juge par la règle commune du joueur (ce que l'auditeur croit qu'il possède ou peut atteindre,
et, pour la remise elle-même, l'effet réel que le moteur exige déjà au moment de livrer, lot 29) ; jamais en faisant chercher un
plan au nom du joueur. Une proposition du joueur ne plante jamais le tour : au pire un refus avec son `attendu`. Corrige le
contrat commun (`echanges` : `_livraison_proposition`, `_devis_proposition`, `devis_service`), pas un cas de script.

## Vérification
- Reproduis d'abord le plantage avec un MJ simulé (la proposition que Luna a pu typer : le joueur offre de remettre un objet,
  ou demande contre une remise de sa part), sur la crypte et sur un autre scénario ; puis la chaîne complète corrigée, état et
  rendu après rechargement : l'offre est acceptée ou refusée selon ce que croit le PNJ, aucun plantage.
- Un garde : tout appel de `chercher`/`devis_pulsion` pour un identifiant sans profil lève une erreur explicite en test.
- Luna, une passe de `crypte` et `ressources` sur la branche : aucun plantage, aucune erreur technique.
- Tests ciblés ; suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/etat-dev.md` (« Branche `codex-promesse-joueur`, non fusionnée »). Rapport
d'une demi-page : `docs/taches/rapport-codex-97-promesse-joueur.md`.
