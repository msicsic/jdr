# Lot 91 — Un appel de fidélité en moins

25 octobre 2026 — Branche `codex-un-appel-de-moins`, **non fusionnée**,
base `123cc0c` (intégration), code signé `031a86e`. Référence Luna : `ef86ff1`.

**Invariant et changement.** L'interprétation `repondre_au_joueur` déclare les
opérations demandées dans sa proposition de parole. `paroles.OPERATIONS` et
`SCHEMA_OPERATIONS` portent les définitions communes de `SENS_CONTENU`, partagées
avec la revue. `couverture_action.lire_operations` refuse une déclaration absente,
incomplète ou mal typée avant accumulation ; `verifier_operations` exige la même
couverture que le lot 82, désormais avant tout appel de revue. Les corrections et
le repli conservent les opérations reconnues pour la saisie entière.
`MJ._verifier_fidelite_parole` saute la revue seulement pour les mots exacts sans
opération déclarée ni contenu typé opérant ; les reformulations et contenus typés
restent revus. Un secours local sans déclaration conserve la revue. Le champ
interprétatif est retiré avant préparation et sauvegarde de la transaction :
aucune modification des effets moteur, de l'audience, des scénarios ou du modèle.

**Preuve console et recharge.** « bonsoir », « Ilse, tu m'entends ? » et une autre
question ordinaire passent sans revue ; les déclarations invalides sont corrigées
sans audit ni affichage du refus technique. Deux demandes de ressources reformulées
gardent une revue. Achat de planche et offre de soupe : opération déclarée mais
simple parole refusée localement, marché corrigé revu une fois, paiement, réserve,
propriété, remise ou livraison et inventaire rechargé contrôlés. Un repli ne perd
pas l'achat déclaré ; une revue illisible ne valide pas le contenu typé.
Les anciennes simulations portent désormais leur déclaration d'interprétation ;
les attentes d'appel systématique sont adaptées au nouveau contrat.

**Vérifications finales.** Suite complète unique : **1 935 tests, 16 ignorés**, 200 fichiers,
trois processus réduits, **1 396,20 s**. Trois échecs et une erreur dans trois
anciennes simulations/attentes : revues encore attendues pour des mots exacts
ou un repli incomplet, et opération `nom` indûment déclarée par la simulation.
Après adaptation au contrat, reprise finale des douze fichiers modifiés :
**128 tests verts, un ignoré, 107,86 s**, deux processus réduits (le dernier fichier
inchangé de la suite calculait encore). **Bilan consolidé sans défaut restant
reproduit**, sans seconde suite complète.

**Luna.** ChatGPT medium/libre, copies temporaires, deux passes de chacun des sept
scripts distincts demandés : soir-appel, noms-dialogue, ressources, echanges et
relais, crypte, atelier (`echanges` appartient aux deux groupes). Intégration et
lot entrelacés, deux exécutions au plus, priorité réduite ; suite complète à trois
processus de calcul à priorité réduite. Les 28 parties sont jouées ici ; les 14 références sont rangées dans le cache,
empreintes SHA-256 vérifiées. Aucun arrêt, erreur technique ni défaut de recharge.
**280 → 278 appels / 84 tours MJ (3,333 → 3,310), mais 13,76 → 14,43 s/tour :
objectif global de temps non atteint.** Totaux par fonction : interprétation/récit
R **149 → 155**, narration N **80 → 86**, fidélité F **50 → 37**, portée P **1 → 0**.
Treize appels F en moins ; corrections et narration absorbent presque tout le gain.
Sur les quatre scripts ciblés seuls : **118 → 109 appels / 28 tours**.
R/N/F/P ci-dessous = appels par tour ; relances/refus/replis = moyenne par passe.

| Script | R/N/F/P par tour, intégration → lot | Total | s/tour | Relances/refus/replis par passe |
|---|---|---|---|---|
| soir-appel | 2,38/1,38/1,00/0,00 → 2,25/1,12/1,00/0,00 | 4,75 → 4,38 | 20,1 → 19,4 | 1,5/0/0 → 0,5/0,5/0 |
| noms-dialogue | 1,88/1,12/0,75/0,00 → 1,75/1,00/0,50/0,00 | 3,75 → 3,25 | 15,5 → 14,9 | 0,5/0/0 → 0/0/0 |
| ressources | 2,00/1,00/1,00/0,00 → 2,33/1,33/1,00/0,00 | 4,00 → 4,67 | 15,2 → 18,5 | 0/0/0 → 1/0/0,5 |
| echanges | 2,17/1,00/1,17/0,00 → 2,00/1,00/0,33/0,00 | 4,33 → 3,33 | 17,1 → 15,1 | 0/0,5/0 → 0/0/0 |
| relais | 1,50/0,75/0,31/0,00 → 1,69/0,94/0,25/0,00 | 2,56 → 2,88 | 11,1 → 12,7 | 0/4/0 → 1,5/4/0 |
| crypte | 1,44/0,83/0,39/0,00 → 1,56/1,00/0,22/0,00 | 2,67 → 2,78 | 12,0 → 13,4 | 0/2/0 → 1/2/0 |
| atelier | 1,82/0,95/0,50/0,05 → 1,91/1,00/0,41/0,00 | 3,32 → 3,32 | 12,9 → 13,3 | 1,5/4,5/0 → 1,5/3,5/0 |

**Achats et limites.** Les deux achats du lot sont exécutés : or **26 → 23**, `planches_1`
portée dans l'état final rechargé. Au premier passage, l'interprétation déclare
l'achat mais propose `propos` : refus local sans revue, puis marché typé corrigé
et accepté. `Ilse, tu m'entends ?` passe aux deux essais sans revue : **3 appels**
contre **4**, sans refus ni repli. Le repli de `ressources` est narratif, sur la
question de dette, sans échec de transaction.
La reconnaissance des opérations reste sémantique : une omission initiale sur
une parole exacte peut encore échapper au contrôle ; un faux positif reste exigé
pendant les corrections. Aucun lexique ni exception de scénario ne remplace cette
limite. Les revues typées et l'audit narratif peuvent toujours se tromper ou relancer
le MJ. Les mesures sur deux passes et un poste partagé ne garantissent pas une
baisse générale de latence.

Bruts : `artifacts/tests-complets-91.{log,json}`, `tests-reprise-91.{log,json}`,
`tests-nouveaux-91.json`, `bancs-multi/20261025-221012-47460/`,
`analyse-luna-91.json` (fonctions, conséquences d'achat, empreintes des parties).
