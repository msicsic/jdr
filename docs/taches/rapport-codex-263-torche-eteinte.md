# Lot 263 — extinction du service payé, hameau 1985

28 octobre 2026, PC fixe. Branche `codex-torche-eteinte`, **non fusionnée**,
base `integration 769c7f1` (brief présent dans le dernier commit initial).
**Diagnostic seul : aucun code du jeu modifié. Verdict : extinction légitime
selon le contrat actuel ; faux positif historique de la sonde 227.**

**Reproduction.** Deux nuits de 12 h, successives, un processus à priorité
réduite, départ tiré, graine 1985, scénario `crue_hameau`, joueur passif en
`chambre_cloche`, comme l’audit 241. Sur `769c7f1`, l’offre payée de la première
minute et l’extinction à 41 min sont absentes. Repli prévu par le brief sur
`c870c8b`, dans un worktree détaché : **les 1 233 entrées de chronique sont
identiques à l’archive 241**, aux mêmes instants. Calculs achevés en 176,6 s
et 108,5 s, sans comparaison de vitesse. Aucun Luna, suite complète ni banc
comparatif ; aucun calcul actif.

**Trace du contrat.** Les instants ci-dessous sont en dixièmes de seconde.

| Instant | Fait et preuve |
|---|---|
| `686` (1 min) | Brune propose à Ilse l’allumage contre une pièce ; offre acceptée. |
| `2436` | Brune allume la torche. |
| `2536` | Réussite constatée, travail payé déclaré fait. `echanges.tenu → biens.retenir_service` inscrit `de=brune`, `pour=ilse`, `condition={objet:torche, allume:true}`, **`lieu_beneficiaire=antichambre`**. Ilse y est crue et réellement présente ; croyance `vu`, minute 3. |
| `24090` (40 min 9 s) | Clôture publiée par `biens.clotures_services_du_choix`. Brune et sa torche allumée sont encore en `echoppe` ; Ilse est réellement en `crypte`, crue là par Brune (`vu`, minute 40, confiance 1, case `[4,0]`). |
| `24105` | Brune rejoint la crypte. La protection déjà close ne renaît pas. |
| `24600` (41 min) | Brune éteint la torche par `eteindre`, but et motif `menager`. Torche portée par Brune, encore 23 minutes de combustible avant/après le geste ; Ilse est alors crue et réellement en crypte. |

**Pourquoi la clôture est valable.** À `24090`, `services_proteges` applique
bien l’ancrage 238 : le bénéficiaire est cru ailleurs que l’`antichambre`
retenue à la réussite **et** que l’`echoppe` où se trouve le résultat courant ;
il ne porte pas ce résultat. La flamme est encore crue allumée, Ilse vivante :
la cause est le départ observé, pas une cessation physique. Le choix complet
publie cette clôture, découverte par `choisir → _plan_abri → chercher →
_entrees_communes → services_proteges`. À 41 min, l’intention est vide,
`services_proteges=[]` et `lumiere_utile=False` : `menager_flamme` crée
`menager → eteindre(torche)`. La réunion ultérieure n’annule pas la clôture.

**Verdict et limites.** Aucun défaut de l’invariant moteur identifié dans cet
épisode. La sonde 227 conserve le paiement et juge la présence au seul instant
de la perte ; elle ignore la clôture légitime déjà publiée. Un contrôle du
résultat payé doit tenir compte de l’historique des clôtures et de leur preuve
de départ, pas seulement de la présence lors de sa réutilisation. Aucun
correctif de sonde réalisé dans ce lot. Cette preuve ne certifie pas toutes
les clôtures ni toutes les pertes signalées par le 227.

**Recharge et bruts.** Captures à `2536`, `24090`, juste avant et juste après
`24600`, puis à 720 min : état complet, `regarder` et `scene_percue` identiques
après sauvegarde/rechargement. Même contrôle sur la fin de la nuit actuelle.
Le joueur passif reste éloigné : son rendu local ne montre pas directement
la torche ; son état physique et les croyances figurent dans les captures.
Bruts exclusivement dans `C:/Users/msics/donjon/artifacts/torche-263/` :
chroniques, événements de création/clôture/extinction, piles d’appels,
recherches, captures, vues, analyse et scripts de diagnostic.
