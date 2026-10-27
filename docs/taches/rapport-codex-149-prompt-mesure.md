# Lot 149 — Préfixe du MJ, mesure seule (L0)

27 octobre 2026 — `codex-prompt-mesure`, **non fusionnée**, base `3f16fe9`.
**Aucun code du jeu changé ni appel Luna/local.** Un processus réduit : **123 parties / 1 354 appels**
(lot 141 : 42/445 ; références `057766f` et `91a4351` : 80/896 ; Argon : 1/13).
Archives complètes, aucun rejeu ; SHA-256 avant/après des sources et manifeste historique vérifié.
Outil réutilisable `tools/mesure_prompt.py`, trois tests courts verts, dont comparaison exacte au
fournisseur simulé. Pas de suite moteur ni clé Git de signature configurée.

**Tailles et stabilité, lot 141.** Moyennes en caractères après mutualisation ; estimation de jetons =
caractères / 4 (sans tokenizer). Schéma = enveloppe `tools` ; entrée avant échappement JSON.
Comparaisons entre appels successifs de même voie/partie ; premier appel exclu.

| Voie | Appels / paires | Consignes / outils / entrée | Consignes / schéma changés | Préfixe JSON / Luna | Cache réel, jetons (% entrée) |
|---|---:|---:|---:|---:|---:|
| Interprétation | 155/113 | 33 335/28 900/17 444 | 42 (37,2 %)/60 (53,1 %) | 33 384/33 892 | 877 056 (29,8 %) |
| Contre-revue | 24/12 | 3 979/455/6 239 | 0/0 | 4 319/4 550 | 0 |
| Fidélité | 36/22 | 2 626/3 221/5 988 | 0/0 | 2 789/5 871 | 2 176 (1,9 %) |
| Audit | 137/103 | 9 598/22 444/17 055 | 0/69 (67,0 %) | 16 792/14 140 | 835 968 (39,0 %) |
| Récit | 71/45 | 5 810/1 347/15 045 | 6 (13,3 %)/12 (26,7 %) | 5 609/5 792 | 0 |
| Révision | 22/8 | 17 775/12 295/23 474 | 1 (12,5 %)/2 (25,0 %) | 36 770/34 724 | 156 160 (49,7 %) |

Blocs moyens, caractères : `D/K/P` = catalogues descriptions/connaissances/profil ; `F` = faits proposables,
`A` = attestations. Objets et surfaces se recouvrent. Chaque bloc individuel est conservé dans les bruts.

| Voie | D/K/P | F / A | Objets / surfaces | Atelier / franchissements / obstacles |
|---|---:|---:|---:|---:|
| Interprétation | 82/407/326 | 2 156/1 822 | 5 246/1 009 | 133/223/139 |
| Audit | 15/99/127 | 854/2 141 | 5 022/941 | 48/84/34 |
| Récit | 2/2/2 | 0/2 272 | 4 631/887 | 0/0/0 |
| Révision | 24/94/131 | 1 001/2 390 | 6 126/1 103 | 52/106/23 |

`espace` absent du corpus ; contre-revue/fidélité sans `faits` de premier niveau.
**Causes Luna**, ordre outils → consignes → entrée : **outils 143**, entrée 159, identique 1 ;
changements de consignes masqués par les outils. Interprétation : enum `faits` 54, branches `proposition` 28,
modes 22 (non exclusifs). Audit : indices des segments 47, structure `anyOf` 4, enum des sources 18.
Le JSON réseau place l'entrée avant les outils : premières divergences entrée 254, consignes 49.
Cette distinction change la priorité de L2 ; la projection Luna ne reconstruit pas ses tokens internes.

**Argon `9d53229` lu sans fusion.** Tours 2→3 : outils **4 573→4 566 jetons**, consignes **9 071→9 071**,
cache **13 312→0**, puis 13 312 au tour 4. Retrait réel : **`objet:brune`**, pas `parole_prevue`, toujours présente.
Attribution Argon : outils 14 387, consignes 17 485, entrée zéro. Mais « jamais items.msg » est **faux sur 141** :
attribution **445/445**, outils **1 016 299**, consignes **807 632**, entrée **47 429 sur neuf appels**.
Le seul ordre des faits d'Argon, réappliqué aux mêmes entrées, allonge le préfixe local simulé `[consignes, entrée]` :
interprétation **32 569→35 839**, audit **15 919→18 452**, récit **5 407→10 747** caractères.
La sonde Argon mélange retrait du schéma, ordre et slots : ses ratios ne sont pas repris comme gain causal.

**Portée.** Dossiers sans référence proche connue : atelier **69/103**, franchissements **8/103**, obstacles **6/59** ;
inconnus **0/61/25**, exclus des numérateurs. Lecture de `a_portee_de_main` calculée par le moteur, pas de distance
inférée de prose. Volume certainement éloigné : **31 060 caractères**. Dix tours terminent leur validation sur
`HorsDePortee` : **24 appels**, dont **12 après refus**, 121 276 jetons d'entrée ; quatre tours répondent déjà localement.
Perche/mur/crochets/poutre, deux passes ; références : dix tours chacune, 24 et 25 appels.

| Lot | Gain attendu Luna | Gain attendu serveur local |
|---|---|---|
| L1, départ `9d53229` | Routage par voie, taille inchangée ; gain réel à mesurer. | Gains d'ordre simulés ci-dessus ; slots à mesurer. |
| L2 | Prioritaire : stabiliser les outils, 60/113 variations d'interprétation, 69/103 d'audit ; taille possiblement accrue. | Grammaire stable ; préfixe amélioré si schéma injecté par le serveur. |
| L3 | Stabiliser les 42/113 changements de consignes après L2. | Même gain, directement en tête du flux. |
| L4 | 31 060 caractères éloignés candidats au retrait. | Même volume de préremplissage évitable. |
| L5 | Jusqu'à 12 appels post-refus évitables ici. | Même économie d'appels et génération. |
| L6 | Socle 33 335 caractères ; réduction non chiffrable avant tri. | Préremplissage froid réduit ; relances à surveiller. |
| L7 | Plafond brut catalogues + surfaces : 1 010 978 caractères cumulés, avant données nécessaires. | Même plafond ; ordre stable à préserver. |
| L8 | Gain faible non isolé ; contrat du sol simplifié. | Même effet, aucune latence démontrée. |

**Reproduction et limites.** Bruts : `C:/Users/msics/donjon/artifacts/prompt-149/` : `mesures.json` par appel/bloc,
usages, préfixes, causes, refus, SHA-256 ; `sources-argon.py`, `rapport-detail.md` et synthèse.
Commande : `python tools/mesure_prompt.py --corpus C:/Users/msics/donjon/artifacts/verif-luna-9a39738
--sortie artifacts/prompt-149 --argon 9d53229 --trace-argon C:/Users/msics/donjon/artifacts/bancs-multi/20261026-212358-22548`.
Archives historiques, pas les prompts actuels ni une partie longue ; UUID remplacé par une constante.
Aucun serveur local mesuré : préfixes simulés ≠ cache acquis, caractères ≠ tokens fournisseur, aucun gain de secondes garanti.
Aucun état modifié/rechargé : preuves d'état des bancs conservées.
