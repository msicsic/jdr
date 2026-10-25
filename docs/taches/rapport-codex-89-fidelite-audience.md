# Lot 89 — Fidélité du contenu et décision d'audience

25 octobre 2026 — `codex-fidelite-audience`, **non fusionnée**, base `96c6396`.
**Validation partielle ; objectif global d'appels non atteint.** Aucun changement
de `main`, des scénarios, de l'audience ou du modèle `gpt-6-luna`.

**Mesure préalable.** Toutes les contre-revues des quarante parties 882907c
(lot 79), trois parties du lot 82 et deux du lot 84 : **16 + 14 + 10 revues de
parole**. Cinq refus, tous injustifiés selon le contrat moteur :

| Lot/script | Nombre | Motif de la revue et erreur |
|---|---|---|
| 82, soir-appel/noms-dialogue | 2/1 | « quelqu'un » porte sur l'ensemble, `ressource` sur l'interlocuteur : rejugement d'audience |
| 84, soir-appel | 1 | `demande` avec valeur 3 ne représente pas explicitement l'échange : forme pourtant exécutable |
| 84, ressources | 1 | La question de dette devient réclamation : conséquence admise par le moteur |

Aucun refus justifié de parole dans ce corpus ; le refus de geste sous obstacle
du lot 79 est exclu. Motifs exacts et sources : `artifacts/refus-historiques.json`.

**Contrat corrigé.** `MJ._auditer_action` sépare parole et gestes. Le rapport
obligatoire porte `perimetre` : seul `sens` peut refuser ; `adresse` et
`validation_moteur` ne relancent pas le MJ. `couverture_action.verifier` exige
toujours les opérations demandées, même hors périmètre. `sens_parole` fournit
les opérations exécutables communes et le prix calculé par `offre` : la revue
compare le sens, sans redécider la représentation. Après le défaut Luna ci-dessous,
`paroles.SENS_CONTENU.reclamer` est aligné sur le contrat existant : interroger
sur son dû ou le réclamer ; le moteur décide du règlement. Cette clarification
est mesurée sur `8c47cc7` dans la section « Seconde mesure » ci-dessous.

**Tests.** Quatre nouveaux tests de vraie console : bois/Aubin et nourriture/Lucien
au premier contrôle malgré une objection d'adresse ; achats de parts sous demande
chiffrée et proposition, paiement/livraison ; questions de dette à Aubin/Gorm ;
mots contraires et autre ressource refusés, opération manquante toujours bloquée.
État, parole unique, sortie, conversation et inventaire après recharge contrôlés.
**71 tests ciblés consolidés verts**, après correction d'une scène de dette.
Suite complète unique : **1 931 tests, 16 ignorés**, 199 fichiers, trois processus,
**1 444,24 s** ; huit échecs d'attentes de dossier dans deux anciens fichiers et
une erreur Windows de remplacement de sauvegarde temporaire dans le test TUI.
Attentes adaptées ; reprise finale des deux fichiers, du seul test TUI en erreur
(inchangé) et des quatre nouveaux tests : **15 tests verts, 56,40 s**.
**Bilan consolidé sans défaut restant reproduit**, sans seconde suite complète.

**Luna, une passe**, ChatGPT medium/libre, copies, priorité réduite, une exécution ;
quatre références 882907c exclusivement en cache : **53 → 57 appels / 14 tours**,
**3,79 → 4,07 appels/tour** ; relances **4 → 2** (0,29 → 0,14/tour), refus **0 → 2**,
replis du détecteur **0 → 2**, un tour avec erreur réseau, aucun arrêt/défaut de recharge.

| Script | Appels/tour, référence → lot | Relances |
|---|---|---|
| soir-appel | 4,25 → 4,25 | 1 → 2 |
| noms-dialogue | 4,00 → 3,50 | 2 → 0 |
| ressources | 3,67 → 4,33 | 1 → 0 |
| echanges | 3,00 → 4,33 | 0 → 0 |

Le bois passe au premier audit dans les deux scripts et Aubin répond sur ses
planches. L'achat du soir subit un délai de **203,4 s avant proposition** : aucun
achat exécuté. Le remboursement finit sur le rendu moteur après deux relances.
La question de dette reste bloquée : `qui` extrait à tort, correction puis repli
incomplets. Définition commune ensuite clarifiée, sans rejouer Luna. `echanges` :
champ interdit de `propos` refusé avant revue puis corrigé ; trois alertes lexicales
du harnais sont les noms saisis repris par des refus locaux, sans fuite narrative.

**Limites.** Périmètre appliqué déterministement, classement et opérations encore
sémantiques : faux refus classé `sens` et écart classé hors périmètre restent
possibles. L'invariant général n'est pas garanti. Temps historiques sous d'autres
charges, aucun gain causal revendiqué. Bruts du worktree : `artifacts/verification-luna-lot89.json`,
`bancs-multi/20261025-210728-32172/`, `tests-cibles*` et `tests-complets.{log,json}`.

## Seconde mesure

25 octobre 2026 — **Deux passes des quatre scripts sur le commit signé `8c47cc7`**,
ChatGPT medium/libre, copies temporaires, deux exécutions parallèles à priorité réduite.
Les huit parties de **882907c sont exclusivement relues du cache** ; huit parties
de `8c47cc7` jouées et rangées. **Aucune erreur technique, aucun arrêt ni défaut
de recharge.** Moyennes par script sur ses deux passes ; chaque cellule donne
**882907c → 8c47cc7**. Refus : validations moteur/contre-revue ; relances : narratives.

| Script | Appels/tour | Relances | Refus | Replis du harnais |
|---|---|---|---|---|
| soir-appel | 4,25 → 5,25 | 1 → 2,5 | 0 → 0 | 0 → 0 |
| noms-dialogue | 3,75 → 4,125 | 1,5 → 0,5 | 0 → 1 | 0 → 0 |
| ressources | 3,67 → 4,33 | 1 → 0,5 | 0 → 0 | 0 → 0 |
| echanges | 3,00 → 4,00 | 0 → 0 | 0 → 0 | 0 → 0 |

Ensemble : **104 → 125 appels / 28 tours MJ**, **3,71 → 4,46 appels/tour** ;
moyennes par passe : relances **3,5 → 3,5**, refus **0 → 1**, replis **0 → 0**.
L'objectif global de réduction des appels reste **non atteint** ; les secondes
des références sont historiques, sans conclusion causale sur la latence.

**Causes, effets et comparaison des sorties.**

- **Deux refus et deux demandes non exécutées**, un par passe, `noms-dialogue`
  n° 3 : « Ilse, tu m'entends ? ». La revue extrait `qui` alors qu'elle déclare
  les mots conformes ; le moteur exige cette opération absente. La correction
  propose `qui`, justement jugé contraire à la question d'audition ; l'extraction
  initiale conservée bloque ensuite le repli littéral. Les deux références
  prononcent la question et Ilse répond. **Régression reproduite**, même si le
  détecteur historique de replis ne compte pas « Ta demande n'a pas été exécutée ».
  Aucun autre refus de validation dans les huit parties.
- **Question de dette**, `ressources` n° 2 : `reclamer` correctement extrait aux
  deux passes, sans `qui`, sans refus ni repli ; « Non. Je ne te dois aucune pièce. »
  puis « Aubin, vieux passeur ne te doit aucune pièce. » s'affichent. Le second
  passage demande une relance narrative de compte, sans échec du tour.
- **Champ interdit de `propos`**, `echanges`, question du gardien : **non reproduit
  aux deux passes**, question dite et réponse reçue sans refus ni correction.
  Les cinq refus locaux de désignation (n° 4 à 8, noms Brune/Aubin/Ilse inconnus)
  sont identiques, texte pour texte, aux deux références : zéro appel Luna,
  aucune régression. Les alertes lexicales correspondantes reprennent les noms
  saisis ; elles ne constituent pas des fuites narratives.
- **Achats du soir exécutés aux deux passes** : or **26 → 23**, `planches_1`
  portée après déplacement et recharge. Une proposition explicite et une demande
  historique chiffrée sont acceptées au premier contrôle. Les relances du soir
  portent sur les comptes narrés : offre inventée ou dette inversée à la question
  du bois, désignation de la part livrable refusée sémantiquement, offre et solde
  de livraison confondus ou omis.
  Elles aboutissent à une narration, sans repli ni nouvelle transaction. La
  première narration d'achat admise cite toutefois `planches_1` et emploie
  « rendues » pour les pièces payées ; qualité de prose non améliorée par ce lot.

**Correction de la régression dans le contrat commun.** L'analyse choisissait des
codes dans une liste dont les sens étaient regroupés en description. Elle
évalue maintenant **chaque opération séparément**, par un booléen obligatoire
portant sa propre définition de `SENS_CONTENU` dans le schéma. Tous peuvent être
faux ; aucun mot ni type n'est exempté. Le contrôle structurel refuse les cartes
incomplètes ou mal typées avant accumulation ; les opérations reconnues restent
exigées sur les corrections. Le périmètre de fidélité et les effets moteur ne
changent pas. Le classement du sens demeure sémantique, donc sans garantie
générale contre toute extraction erronée.

Un nouveau test de console/recharge couvre le cas d'Ilse et une autre question
ordinaire à Aubin, chacun avec une analyse lisible puis une analyse mal typée
relue sans correction du contenu : paroles, destinataires, conversation, sortie
et or après recharge. **77 tests ciblés verts, six fichiers, deux processus à
priorité réduite, 53,93 s** ; couverture des achats manquants et conservation des
opérations également revérifiées. Pas de seconde suite complète. Une erreur de
délimiteur corrigée avait empêché l'import des premiers tests et d'une tentative
de banc ; cette tentative n'a fait **aucun appel Luna**.

**Reprise de `noms-dialogue` après correction : deux passes**, mêmes références
en cache : **14 appels sur quatre tours chacune**, soit **3,50 appels/tour**,
**zéro relance, refus, repli, erreur technique ou défaut de recharge**. « Ilse,
tu m'entends ? » est prononcée au premier contrôle avec toutes les opérations
fausses ; Ilse répond « Oui, je t'entends », et la sauvegarde rechargée conserve
le tour. Bois à Aubin et passage demandé à Brune restent correctement typés.
Les trois autres scripts ne sont pas rejoués après cette correction : leurs
chiffres ci-dessus restent ceux de `8c47cc7`, pas une moyenne artificielle sur
deux versions du code. Aucun autre changement de code.

Bruts : `artifacts/bancs-multi/20261025-214008-41452/` (mesure de `8c47cc7`),
`20261025-214903-31636/` (reprise corrigée), `seconde-mesure-analyse.{json,txt}`,
`reprise-noms-dialogue-analyse.json` et `tests-seconde-mesure.{log,json}`.
