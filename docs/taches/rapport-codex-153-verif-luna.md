# Lot 153 — Vérification Luna cdaf371

27 octobre 2026 — **Validation partielle : N9 corrigé sur le parcours réel ; N7, avis incomplets et trois restes de force persistants.** Deux passes des 32 scripts demandés : **64 parties, 352 saisies, 180 tours MJ, 542 appels**. Copie détachée exacte de `cdaf371`, supprimée après usage ; `gpt-6-luna`, ChatGPT medium/libre, budget 200 par groupe/passe, trois exécutions `BelowNormal` au plus, coffre principal. Aucun code du jeu changé, aucune suite moteur relancée, `main` intact. Les 64 parties manquantes ont été jouées et rangées sous `cdaf371` : identité source/cache SHA-256 vérifiée. Référence `9a39738` exclusivement relue : **63 fichiers inchangés**. Son harnais diffère seulement par l'ajout de `rixe` ; clés historiques conservées, aucun rejeu.

**Mesures.** Sur les 42 parties communes : **445 → 448 appels**, 142 tours MJ ; appels/tour moyenne **3,13 → 3,15**, médiane **3 → 3** ; secondes/tour moyenne **11,76 → 10,64**, médiane **10,50 → 9,80** ; relances **22 → 21**, refus **36 → 39** sur **26 → 27** tours, replis **1 → 1**, audits illisibles **0 → 0**. Force : **94 appels / 38 tours**, 2,47 appels/tour, 7,75 s/tour, médianes 2 / 6,11 ; trois relances, neuf refus sur cinq tours. Ensemble : **3,01 appels/tour, 10,03 s/tour**, médianes **2 / 9,16**, 24 relances, 48 refus/32 tours, un repli, zéro audit illisible. Secondes = attente cumulée des appels, charges historiques différentes : aucun gain de vitesse causal établi.

Par fonction, ensemble `cdaf371` ; moyennes [médianes] par tour, zéros inclus. Les comparaisons par fonction et groupe sont dans `mesures.json`.

| Fonction | appels/tour | s/tour | jetons cachés (`usage`) |
|---|---:|---:|---:|
| interprétation | 1,02 [1] | 4,31 [4,16] | 1 117 312 |
| audit narration | 0,89 [1] | 2,99 [2,94] | 1 018 368 |
| fidélité | 0,20 [0] | 0,58 [0] | 0 |
| contre-revue | 0,24 [0] | 0,42 [0] | 19 072 |
| récit | 0,52 [1] | 1,30 [1,79] | 7 296 |
| révision | 0,13 [0] | 0,41 [0] | 139 264 |
| audit portée | 0,006 [0] | 0,02 [0] | 0 |

Cache total : **2 301 312** jetons ; attribution fournisseur : outils **1 186 259**, consignes **1 020 882**, items **94 171**. Sur les communs : **1 871 360 → 2 124 928** ; aucune écriture de cache ni réflexion facturée dans `usage`. Détail dans `usage-voies.json`.

**Cas suivis**, indices à partir de zéro :

- **N9 corrigé sur le parcours exercé**, `soir-noir` n°2 « Qui est là ? » : parole prononcée 2/2. P2 propose d'abord `nom` avec « Je suis Corvus », refusé, puis corrige en `qui` et exécute la question en cinq appels ; aucune obligation erronée persistante, aucun « Tu n'as encore rien dit ». P1 six appels, sans cette erreur initiale.
- **N10 non reproduit 2/2** : `atelier` n°12, recherche de pierre, et `relais` n°22, prise du pied-de-biche, expliqués en fiction ; aucun contrat interne affiché relevé. Le rejet de l'ancienne formulation n'est pas réexercé naturellement.
- **N7 persistant**, `soir-noir` p2 n°5 « je demande à la voix comment elle s'appelle » : « Je suis Ilse » avait été entendu au n°2. L'audit rejette « Je t’ai déjà dit que je suis Ilse » en inversant les révisions 2 et 5, puis le rappel disparaît ; six appels. P1 aucun nom prononcé antérieurement : rappel non exercé.
- **Avis incomplets persistants** : conduite/galerie/refuge, p1 **avis/propos/avis**, p2 **propos/propos/avis**, soit **3/6**, inchangé face à 141. Les saisies « l'eau va gagner la conduite basse / la galerie de ronde » restent parfois sans effet d'avis typé. Unique repli : galerie p1 n°1, segments admis, sans erreur technique.
- **Gorm remboursé 2/2**, `comptes` n°1 : deux pièces rendues dans les issues ; Brune refuse. **Achats partiels** : `soir-appel` p2 n°5 payé, n°6 livré, `planches_1` portée après recharge ; p1 achat bloqué (ci-dessous). Confusion comptable antérieure non réémise dans les échanges aboutis. **Fausse absence dans le noir non reproduite 2/2**, `signes-noir` n°2 : non-perception sans absence, trois personnages toujours dans l'antichambre rechargée.

**Force, critère non atteint.** Les huit autres premières saisies (4b, 4c, achever, ligoter, question d'assommement) sont typées en **deux appels aux deux passes**. Restes, appels p1/p2 : **traîner 5/4, enfermer 2/3, improvisé 6/4**. Traîner n°0 : contre-revue rejette le pas sud malgré la destination du corps ajoutée ; elle oppose « crypte » à « Salle des vannes » (identifiant `crypte`). P1 inverse ensuite le pas vers la case occupée ; p2 prétend le corps hors de portée. Aucun déplacement enregistré. Enfermer n°0 : porte ouverte à portée, passe porté compatible, mais p1 exige d'approcher Bram et p2 propose de le déplacer vers le baraquement, sans verrouiller ; refus de l'intention injustifié. Improvisé n°0 : p1 passe de `frapper` à `improviser`, refus corporel ; p2 répète `tuer` sur une cible capable de se défendre, refus moteur juste pour ce typage. Aucun résultat corporel inventé ni mort/inconscient parlant relevé ; assommement, ligotage et mort racontés après leurs issues moteur. Ces scripts n'éprouvent pas chaque paraphrase ni tous les gestes 4d.

**Nouveau cas N11 — achat irrécupéré**, `soir-appel` p1 n°5 « je paie Aubin trois pièces pour une de ses planches » : contrepartie `pieces` avec `objet=planches`, refus précis demandant un objet à pièces ; correction `objet=planches de bac` encore invalide, affichage « Corvus cherche ses mots… ». Aucune parole d'achat ni planche portée dans les projections suivantes. P2 retire ce champ et réussit. Invariant à reprendre : la correction d'un échange doit respecter le contrat typé reçu, sans perdre une intention exprimable ; cause probable interprétation/correction de `contrepartie.objet`, pas manque de planches. Aucun correctif ici.

**Limites et livraison.** Zéro plantage, erreur réseau, budget épuisé ou erreur de recharge ; 64 parties complètes, 161 audits lisibles. Le harnais recharge à chaque tour et conserve textes, projections et dossiers, mais pas le monde complet, les panneaux de fiche ni tous les soldes/corps : leurs invariants complets après recharge ne sont pas certifiés. Les refus sémantiques restent partiels. Bruts : `C:/Users/msics/donjon/artifacts/verif-luna-cdaf371/` (`lecture.txt`, `revue.txt`, `force.json`, mesures, usages, empreintes et lanceurs). Aucune clé de signature configurée : commit non signé ; branche seule poussée.
