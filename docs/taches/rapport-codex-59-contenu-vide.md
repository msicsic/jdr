# Lot 59 — Parole sans contenu mécanique

Branche `codex-contenu-vide`, non fusionnée ; base `18abb2c`, issue de l’intégration
`c592d68`. `origin/integration` était à jour au départ, sans le lot 56. `main` intacte.

## Invariant et correction

Une parole exploitable demeure valable sans effet typé. Aucun effet ou terme mécanique
ne naît d’une réplique seule. Le basculement constaté vient du chevauchement des voies :
la parole générale de 47 b fixe l’audience, tandis que `conversation_pnj` calcule les
missions. Cette voie reste disponible. La contre-revue réduite jugeait mots et contenu
ensemble : deux refus de typage devenaient une demande de reformulation avant le secours
local. L’audit confondait liberté des mots d’un PNJ et liberté des termes mécaniques.

Dans `mj._verifier_fidelite_parole`, des mots identiques à la saisie, sans contenu ou avec
`propos` seulement, n’ont plus d’interprétation à revoir. La revue reste pour les autres
mots et les contenus typés. Après deux typages refusés, les mots fournis sont préparés
sur le monde original sans effet typé ; sans mots fournis, le joueur les précise.
`parole_du_moteur` réutilise `paroles.mots_dits`, y compris pour les questions directes.
Aucun effet des copies refusées ne passe.

Le rapport de `narration` exige une `portee_mecanique` par segment, indépendante du
verdict. Le moteur refuse une portée sans fondement ou contradictoire même sous
`parole`, exige une source pour `etablie` et une preuve pour une contradiction ;
`consigner` refait ces contrôles avant sauvegarde. Les doubles d’audit suivent ce
schéma. Aucun objet, lieu ou scénario dans ces gardes ; aucune consigne ajoutée au
choix d’interprétation de Luna, aucun changement du modèle ni de `biens.py`/`paroles.py`.

## Vérification

**Suite complète unique** (`tools/tests.py --processus 3`) : **1 800 tests,
16 ignorés, un échec préexistant**, **1 088,45 s**, priorité réduite.
`test_appel_negocie.QuoiTests.test_cas_reel_mine_josse_dit_ce_qu_il_veut_gaspard_le_fait_venir`
attend une demande promise ; Josse essuie un refus puis obtient un échange accepté.
Rejeu isolé sur une copie de **18abb2c** : même assertion et chronique identique,
encodage normalisé. Aucun correctif PNJ hors périmètre.
Les **quatre tests du lot** passent sur leurs assertions finales (**8,92 s**) :
console, MJ simulé, sauvegarde/recharge ; mots entendus, contrats, missions, or et texte
persistant ; prime inventée, prix à l’auberge et deux questions réelles. Ils contrôlent
aussi le rapport incomplet et une portée établie sans source, indépendamment du verdict.

**Luna, une passe**, quatre scripts, copies uniquement :

| Saisie ciblée | Résultat affiché | Appels |
|---|---|---:|
| Crypte, prime de l’anneau | 20 pièces du moteur, offre en attente sans paiement | 5 |
| Soir-noir, « il y a quelqu’un ? » | Parole dite ; « Oui. Qui parle ? » | 6 |
| Échanges, question du gardien | Parole dite ; « Je ne sais pas où est passé le gardien. » | 3 |
| Noms-dialogue, demande de bois | Aubin seul répond | 4 |

Aucun « Précise… » sur les deux questions, aucun repli ni erreur technique/recharge.
Faux positif d’audit sur « ici » dans la remise de l’anneau : reformulé avant affichage.
Référence **main 42bb9c0 relue du cache**, mêmes scripts vérifiés par empreinte :
**69 → 70 appels**, **22 → 21 tours MJ**, **3,14 → 3,33 appels/tour**,
**12,6 → 13,2 s/tour**, **277,28 → 276,77 s** au total ; relances **2 → 3**,
refus **3 → 4**, replis **0 → 0**. Charge du cache différente.
Un décalage de budget (500 contre 200) a fait tenter au lanceur une référence,
arrêtée au premier tour local avant tout appel (`agendas` absent de l’ancien code) ;
comparaison faite ensuite par lecture explicite du cache, sans nouveau banc de `main`.
Aucune partie au-delà de 24 appels.

## Limites et traces

La reconnaissance de la portée mécanique, la fidélité des paraphrases et la pertinence
des sources restent sémantiques : **pas de garantie absolue contre les inventions**.
Les croyances fausses d’un PNJ restent possibles sans établir leur contenu comme fait.
La compatibilité conjointe avec le lot 56, absent de la base, reste à vérifier à l’intégration.

Bruts dans le worktree : `artifacts/tests-59.log`, `cibles-finales-59.log`,
`echec-base-59.log`, `luna-59.log`, `relecture-59.txt`, `comparaison-luna-59.md`
et `artifacts/bancs-multi/20261024-235004-37276/`.
