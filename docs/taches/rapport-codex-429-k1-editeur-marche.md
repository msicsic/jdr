# Lot 429 — K1, éditeur de marché à deux termes

Branche `codex-k1-editeur-marche`, base `integration` **`b941c492`**.
**Terminé, non fusionné** ; code `4b0b4ddc`, vérification conclue le 2026-10-31.

**Invariant.** Le formulaire compose ce que Corvus donne et ce qu’il demande :
objet entier, part, tâche ponctuelle, pièces (fonds ou source explicite), et
contrepartie éventuellement nulle. Les deux termes de l’aperçu sont ceux
transmis à `echanges.proposer`. Les références publiques sont résolues sans
réécriture des clauses. Une clause inconnue reçoit un refus avec `attendu`.

**Changement.** `accords_publics` étend le catalogue E5 ; `parole_accord` applique
`propositions.erreur_terme` / `verifier` puis produit la parole déterministe.
Le descripteur transporte `demande` et `contrepartie` entiers, avec un adaptateur
K0/E5 sans perte. K0 reste borné aux achats de parts et tâches : deux lignes
localisées dans `dialogues.py`. Le jugement, la dette, les transferts et les
engagements d’`echanges.py` sont conservés.

**Interfaces et libre.** Le web affiche termes, montants et limites exactes.
Console et TUI réutilisent `AccordTerminal` : un entier offre des pièces,
`terme N` choisit une autre contrepartie. Tout reste modifiable avant validation.
Après sa revue de fidélité, le libre non daté ouvre le même éditeur et le même
descripteur, sans effet ; un mélange avec d’autres actes est refusé explicitement.
E6 garde les dates non compilables à préciser. Aucun modèle dans l’éditeur,
aucun contrôle de fidélité retiré.

**Vérification finale.** **79 tests découverts : 77 réussis, 2 ignorés,
aucun échec ni erreur**, sur huit fichiers K0, K1, E5/E6, accords datés,
U-D, comptes parlés et propositions. Les deux tests de schéma sont ignorés
car `jsonschema`, facultatif, est absent ; les validateurs moteur sont exercés.
K0 : 7/7, 137,8 s ; K1 : 5/5, 221,2 s ; reprise des trois fichiers : 29 tests, 309,0 s.
Deux travailleurs au plus, priorité réduite, sur copies ; aucune suite complète,
aucun banc PNJ ni appel Luna.

**Parcours réels.** Aubin accepte les pièces contre les planches et refuse la
cloche contre la tâche d’allumage ; Odile accepte la lanterne contre une part
d’huile. Les vrais callbacks web, la console et la TUI contrôlent les termes
soumis, le verdict, l’état sauvegardé et les vues rechargées. Autres preuves :
libre avec modèle simulé et revue appelée, clauses inconnues, mélange d’actes,
rien, source des pièces, pièces demandées, limite à 6123. Les anciens tests de
marché valident désormais le brouillon avant « tenter » ; la TUI contrôle le
registre public des paroles et la parité avec le web.

**Attribution supplémentaire.** Fichier du helper de parole : 12/14 réussis,
une assertion et une erreur liées à l’ancien contexte
`esprits_interlocuteurs`. **Mêmes deux défauts sur l’archive intacte de la base
`b941c492`**, 14 tests rejoués (52,7 s) ; hors du correctif K1.

**Limites.** Le catalogue des tâches reste celui des prestations ponctuelles E5 ;
pas de nouveau langage de conditions, maintien, prêt ou offre persistante.
La fidélité sémantique de toute saisie libre n’est pas une garantie déterministe :
elle conserve sa revue et le contrôle explicite du joueur. Le verdict du PNJ
reste indépendant d’un brouillon valide.

Bruts : `C:/Users/msics/donjon/artifacts/k1-editeur-429/` : `bilan-final.json`,
`cloture.json`, `paroles.json`, `paroles-base-b941c492.json` ; `fin-initial.json`
garde le premier bilan, `fin.json` clôt la vérification et distingue l’extension.
Aucun calcul en cours. Branche poussée ; fusion et suite complète au superviseur.
