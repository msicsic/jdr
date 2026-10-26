# Lot 141 — Vérification Luna 9a39738

26 octobre 2026 — **Validation partielle : N6/N8 non reproduits, avis incomplets, identité et récit comptable encore dégradés.** Aucun code du jeu changé. Deux passes des vingt scripts du lot 123 et d’`avis-joueur` : **42 parties, 308 saisies, 142 tours MJ, 445 appels**. `gpt-6-luna`, ChatGPT medium/libre, budget 200 par groupe/passe, quatre processus `BelowNormal` au plus, copies temporaires et coffre principal. Lanceur du lot 123 adapté, fonctions de cache/mesure de `banc_multi`, sans nouvel appel aux références : **120 fichiers SHA-256 inchangés** sous `057766f` et `91a4351`. Code du worktree `118ef4a` identique à `9a39738` pour le jeu et le harnais ; 42 parties rangées sous `9a39738`, identité source/cache vérifiée.

Chaque cellule compare **057766f → 9a39738**. Moyennes sur les tours réunis ; nombres de relances/refus/replis totaux des deux passes, contrairement aux moyennes par passe du rapport 123. Refus locaux sans appel hors compteur historique. Détail par passe/groupe/fonction dans `mesures.json` et les fils.

| Groupe | appels/tour | s/tour | médiane s | relances | refus / tours avec refus | replis | illisibles |
|---|---|---|---|---|---|---|---|
| référence | 2,92→2,98 | 10,63→11,51 | 10,07→10,91 | 8→9 | 17/12→18/14 | 0→1 | 0→0 |
| signes | 2,83→2,00 | 11,33→7,28 | 9,65→7,51 | 5→0 | 0/0→0/0 | 0→0 | 0→0 |
| ambiance | 2,00→2,00 | 7,79→7,60 | 6,69→7,05 | 0→0 | 0/0→0/0 | 0→0 | 0→0 |
| noms-soir | 4,46→4,12 | 17,18→14,77 | 15,18→14,16 | 7→5 | 3/3→3/3 | 0→0 | 0→0 |
| ressources-comptes | 5,00→5,00 | 19,80→17,86 | 19,03→16,31 | 5→4 | 0/0→1/1 | 0→0 | 0→0 |
| sous obstacle | 2,20→1,90 | 8,26→6,97 | 7,50→6,83 | 2→0 | 15/8→14/8 | 0→0 | 0→0 |
| vingt communs | 3,21→3,06 | 12,15→11,38 | 10,91→10,36 | 27→18 | 35/23→36/26 | 0→1 | 0→0 |
| avis, sans référence 057766f | 4,83 | 20,19 | 13,71 | 4 | 0/0 | 0 | 0 |

Vingt communs : **437→416 appels (−4,8 %), 135→127 audits** ; médiane des appels/tour **3→3**. Historique `91a4351` relu : 459 appels, 3,38/tour, 11,54 s/tour, médiane 9,57 s, 27 relances, 36 refus/26 tours, trois replis, 35 audits illisibles. Ensemble avec avis : **3,13 appels/tour, 11,76 s/tour**, médianes 3 appels/10,50 s ; passes 3,127/3,141 appels et 11,64/11,88 s par tour. Charges historiques différentes : aucune attribution causale de vitesse.

| Fonction, vingt communs | appels/tour moyenne [médiane], avant→après | s/tour moyenne [médiane], avant→après |
|---|---|---|
| interprétation | 1,09 [1]→1,10 [1] | 4,85 [4,33]→4,81 [4,40] |
| audit narration | 0,99 [1]→0,93 [1] | 3,95 [3,57]→3,57 [3,22] |
| fidélité | 0,26 [0]→0,24 [0] | 0,83 [0]→0,76 [0] |
| contre-revue | 0,17 [0]→0,18 [0] | 0,36 [0]→0,41 [0] |
| récit | 0,49 [0]→0,48 [0] | 1,37 [0]→1,34 [0] |
| révision | 0,20 [0]→0,13 [0] | 0,74 [0]→0,49 [0] |
| audit portée | 0,015 [0]→0 [0] | 0,05 [0]→0 [0] |

**Coût des entrées.** Caractères du JSON compact UTF-8 décodé, hors instructions et schéma, pas des jetons. Sur vingt, entrée d’audit moyenne **14 229→15 170 (+6,6 %)** ; dossier `faits` **12 885→13 807 (+7,2 %)**. Liste `non_vus_connus` seule : moyenne 153, maximum 341 caractères par audit ; avis : maximum 1 327. Les autres ajouts et les générations diffèrent aussi : on ne peut attribuer toute la hausse au lot 132. Sur les longs, maximum du dossier d’audit : Relais **16 180→16 173**, crypte **17 583→18 599**, atelier **12 698→12 867** ; soir-appel **24 287→25 243**, avis **26 855**. Pas d’explosion observée sur ces scripts, aucune borne pour une longue partie libre. Avis : **15/14 appels**, contre neuf au lot 124 et quinze au lot 128 (rapports, sans rejeu) ; les trois avis effectivement typés ont une revue de fidélité, les trois `propos` omis n’en ont aucune. Le coût total comprend aussi quatre relances narratives : il ne mesure pas seulement le typage.

**Cas suivis**, indices à partir de zéro :

- **N6 non reproduit 2/2**, `signes-guet` n°1, « Que fait Gorm en ce moment ? » : « Tu ne vois pas Gorm dans la galerie », deux appels aux deux passes, zéro refus. Fausse absence dans le noir non reproduite 2/2, `signes-noir` n°2 ; Ilse, Brune et Corvus restent dans l’antichambre rechargée.
- **N7 partiel, persistance sémantique**, `soir-noir` n°5, demande du nom : p1 aucun nom antérieur, cas non exercé ; p2 Ilse a dit « Ilse. » au n°2, mais « Ilse. Tu le sais déjà. » est rejeté pour affirmation sans source et attribution nominale. Affiché aux deux passes : « Je ne te dirai pas qui je suis. » Le faux historique « Je m’appelle une voix… » ne revient pas ; rappel exact moteur non proposé, donc non éprouvé ici.
- **N8 non reproduit 2/2**, `ressources` n°1, « je demande à Brune si elle a de quoi manger » : « Brune, as-tu de quoi manger ? » / « As-tu de quoi manger ? ». P2 corrige un contenu refusé, sans réplique descriptive finale.
- **Avis persistants incomplets**, p1 conduite/refuge typés, galerie `propos` (**2/3**) ; p2 conduite et galerie `propos`, seul refuge typé (**1/3**). Saisies exactes dans le script et les bruts ; aucun invariant général acquis.
- **Gorm remboursé 2/2**, `comptes` n°1 : deux pièces rendues, dette absente dans l’issue ; Brune reste débitrice. **Achats payés/livrés 2/2**, `soir-appel` n°5–6 : trois pièces au passeur, part due puis `planches_1` portée après recharge. **Confusion de récit persistante p1** : « tu m’as rendu les trois pièces que tu me devais ». P2 achat correct ; au remboursement n°4, faux refus de « Il te rend ainsi 2 pièces », puis vocabulaire technique « compte […] marqué comme rendu ».

**Nouveaux cas à isoler, sans correction ni attribution causale à un lot.**

- **N9 — Correction de typage bloquée**, `soir-noir` p1 n°2, « Qui est là ? » : première proposition `nom=true`, réplique inventée « Corvus. Qui es-tu ? », refusée ; seconde proposition `qui=true`, mots exacts corrigés, mais affichage « Tu n’as encore rien dit : précise ce que tu veux demander ou faire savoir à ton interlocuteur. » Aucun propos exécuté à ce tour, projection rechargée inchangée. Cause probable dans `MJ.proposer` / `_verifier_fidelite_parole` : `nom` mémorisé après échec de préparation, imposé aux corrections et au secours. Invariant : une déclaration erronée non confirmée ne doit pas rendre irrécupérable une interprétation corrigée. P2 même saisie exécutée, autre parcours sans première erreur.
- **N10 — Explications techniques affichées**, `atelier` p1 n°12, recherche de pierre : « il faudrait que le moteur fournisse un geste de fouille ou de recherche adapté » ; `relais` p2 n°22, prise du pied-de-biche : « Le moteur n’en reconnaît pas […] dont tu connais précisément l’identifiant ». Ces phrases passent l’audit. Invariant : expliquer l’obstacle dans la fiction sans exposer les contrats internes au joueur ; contrôle sémantique commun insuffisant. Aucun geste supplémentaire enregistré.

**Limites et livraison.** Aucun plantage, erreur réseau, budget épuisé, saisie perdue par le harnais ni défaut de recharge ; N9 reste un refus de jeu. Un repli par segments admis, `atelier` p2 n°12. Quatorze projections sous obstacle identiques à 057766f (positions, temps, possessions, passages et blocages), rendus relus. Le harnais ne conserve pas le monde complet ni les panneaux de fiche : comptes contrôlés dans les issues, pas dans un solde rechargé capturé ; aucune garantie sémantique universelle. Aucune suite moteur relancée. Aucune clé de signature Git configurée : commit non signé. Bruts, scripts, mesures, revue et preuves : `C:/Users/msics/donjon/artifacts/verif-luna-9a39738/`.

