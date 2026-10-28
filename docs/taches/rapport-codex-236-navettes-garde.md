# Lot 236 — diagnostic des navettes de garde

28 octobre 2026, branche `codex-navettes-garde`, non fusionnée, base `ecbf1a1`.
**Arrêt pour question de périmètre, aucun correctif moteur.** Le contrat fautif
implique `pnj_propositions.plan_recours`, hors des fichiers autorisés par le brief.

## Reproduction

Deux nuits auberge, graine 7, départ tiré, joueur au dortoir à sa position
d'entrée : d'abord le worktree détaché `4306c14`, ensuite la branche actuelle
(intégration `ecbf1a1`, après 218/229/230). Un seul calcul à la fois, priorité
BelowNormal ; aucun Luna. Captures à 415, juste avant la fenêtre, puis à 435 ;
trace avant/après chaque choix d'Anselme, croyances et plans compris.

Sur `4306c14`, la rafale est reproduite, sans mesurer l'heure entière historique :

| Minute | Cause et progression observées |
|---|---|
| 420–421 | La garde cherche une lanterne ; découverte du ballot déplacé, puis remise au poste. |
| 422–423 | Ballot remis, pas de navette commerciale relevée. |
| 424–425 | Rétablissement du poêle ; demandes de lanterne puis d'huile. Deux contre-offres à une pièce sont retenues à 425. |
| 426–428 | Retour au poste, démarches autour du poêle ; pas encore le cycle stabilisé. |
| 429 | Lanterne éteinte ; garde reconstruite, mais son plan vide est remplacé par un trajet d'achat d'huile chez Joss. Quatre passages. |
| 430 | À l'étable, avant l'achat, le choix reconstruit le retour au poste ; au poste, il réinjecte l'achat. Sept passages. |
| 431 | Même inversion depuis la cuisine, puis nouveau départ du poste. Sept passages. |
| 432 | Même inversion depuis l'étable. Sept passages. |
| 433 | Même inversion depuis la cuisine. Sept passages. |
| 434 | Même inversion depuis l'étable. Sept passages. |
| 435 | Nouvelle inversion depuis la cuisine, capture finale. |

Pendant ce cycle, même but `garder/chambre_chaude`, même naissance à 429,
aucun `manque`. Le lieu cru de la charge ne bascule pas. La rafale n'est donc
pas un trajet de garde qui change de cible : des moyens commerciaux étrangers
à ce but lui sont greffés puis retirés à la reconstruction.

Sur l'intégration actuelle, aucun passage d'Anselme entre 426 et 435 : garde
au poste, née à 426, plan vide. La demande refusée porte alors sur le bois
d'Odile, sans contre-offre retenue. **Cette fenêtre n'établit pas l'absence
de rafale plus tard dans la nuit.**

## Cause et invariant à corriger

Sur la capture historique rechargée, `planification.garder` rend correctement
`[]` au poste. `deliberation.choisir` appelle ensuite
`pnj_propositions.plan_recours(monde, id, besoin, etapes)`. Ce dernier associe
une ancienne contre-offre à la seule identité du besoin `biens` : il rend
le trajet d'achat d'huile. En déplacement, le plan ordinaire de retour,
non vide et sans faute, empêche ce remplacement : l'achat disparaît avant
exécution. Le retour recrée les conditions de son injection.

La même capture historique chargée par le moteur actuel produit encore
`garde [] → plan_recours biens [] → trajet + acheter`. Le défaut de contrat
subsiste malgré la disparition de son déclencheur dans la nouvelle nuit.
Un recours doit rester rattaché à la demande et au résultat qui le rendent
utile ; le partage d'un besoin ne permet pas de le transférer à un autre but.
Interdire les achats pendant une garde masquerait cette lacune générale.

## Limites et reprise

Le brief impose de poser une question si la cause sort des fichiers autorisés.
Il faut autoriser le contrat commun des recours dans `pnj_propositions.py`
avec son raccord à `deliberation`, puis ajouter les cas rechargés réels et
analogues, les laps découpés et les rendus. Aucun invariant corrigé revendiqué,
aucun banc 20 nuits ni suite complète lancés avant cette décision.

Bruts : `C:/Users/msics/donjon/artifacts/navettes-236/` : captures 415/435,
chroniques 415–435, choix JSONL et scripts de diagnostic. Les déplacements
manuels du script causal servent uniquement à isoler l'injection du recours ;
ils ne constituent pas un test de nuit corrigée.
