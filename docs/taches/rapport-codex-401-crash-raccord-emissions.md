# Lot 401 — Raccord des émissions sans redécoupage divergent

Branche `codex-crash-raccord`, base `integration 4c160145`, laptop.
Bruts : `C:/Users/msics/donjon/artifacts/crash-raccord-401/`.

**Cause et invariant.** La capture réelle de `echanges` (Relais, graine 1985,
« je dis à tous que l'eau monte et qu'il faut garder le feu ») reproduit
`KeyError: '0'`. Deux réponses moteur commencent par « le vieil homme voûté »
et « la femme sèche ». `segments(" ".join(fixes))` les fusionne : après les
guillemets, la nouvelle attribution commence en minuscule. Chaque réplique
isolée est pourtant bien établie par `conversation_validee.faits` ; ni parole
manquante ni segment vide. La cause étant démontrée, pas de bissection.

`narration.raccorder_emissions` établit maintenant les preuves sur le texte
final, dont l'assemblage conserve déjà les frontières de tous les segments.
Rendu, audit et recontrôle de sauvegarde partagent ainsi le même découpage.
Chaque occurrence moteur conserve son ordre et ses mots ; aucun audit retiré,
aucun ajout au prompt, aucune exception de scénario ou registre d'esprit.

**Preuves hors ligne.** `tests/data/crash-raccord-401.json.gz` archive état,
rapport et réponse Luna avant raccord. L'état avant saisie est reconstruit
depuis le tour précédent ; sa préparation produit exactement le monde complet
et le rapport capturés. La vraie boucle de jeu rejoue la saisie avec le MJ
simulé, admet la réponse libre, sauvegarde puis recharge : les deux émissions
moteur restent strictement identiques et une seule nouvelle réponse s'ajoute.
Affichage, scène et registre rechargés sont contrôlés. Autre cas : deux
émissions identiques sans ponctuation finale, raccord répété, admission et
recharge sans perte ni réémission. Les deux tests échouent sur le raccord de
la base avec `KeyError: '0'`, puis passent avec le correctif.

**Vérification.** **63 tests verts / quatre fichiers, 247,064 s**, zéro échec,
erreur ou saut : émissions, narration, messages selon découpage et ouïe commune
(`tests-final.txt`).
Pas de suite complète ni de nuit passive : seul le raccord de la réponse MJ
change, aucune simulation PNJ modifiée. Un travailleur de tests réduit au plus,
deux traitements actifs au maximum avec Luna.

**Luna.** Après la capture diagnostique interrompue par le plantage, une seule
passe de validation sur copies, `gpt-6-luna` et coffre `SEUIL_AUTH` indiqué :
`echanges` **9 appels / 3 tours MJ**, `noms-dialogue` **15 / 4** ; zéro erreur
technique, erreur de recharge ou repli dans les deux bancs. Limite : le tour
« l'eau monte » reçoit cette fois un refus de contenu avant raccord ; il est
donc couvert par la capture rejouée hors ligne. Les quatre signalements de
noms du banc `echanges` et les refus de noms inconnus restent visibles dans
les bruts ; aucune garantie supplémentaire sur la sémantique de Luna.

Branche à fusionner par le superviseur. Aucune sauvegarde utilisateur touchée.
