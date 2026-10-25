# Lot 70 — Vérification Luna de l'intégration fbcf0ff

25 octobre 2026 — **Validation partielle : prime, observation et orientation corrigées ; comptes et faux refus encore défaillants.**
Deux passes des vingt scripts prescrits : **40 parties, 302 saisies, 416 appels**, `gpt-6-luna`/ChatGPT,
medium/libre, budget 200 par groupe/passe ; quatre exécutions au plus, priorité réduite, sauvegardes temporaires,
`SEUIL_AUTH` principal. Aucun arrêt, erreur technique/recharge ou tour écarté. Quarante parties rangées dans le cache
de **fbcf0ff**, identité SHA-256 vérifiée. **main 42bb9c0 et f033364 uniquement relus du cache**, jamais rejoués.

Chaque cellule : **main→f033364→fbcf0ff**, moyenne des deux passes selon la méthode précédente.
Ratios sur les tours MJ ; relances narratives, refus moteur/contre-revue, replis du détecteur historique.
Secondes historiques sous des charges différentes : aucune conclusion causale de performance.

| Groupe | appels/tour | s/tour | relances | refus | tours avec refus | replis | tours MJ |
|---|---|---|---|---|---|---|---|
| Référence : relais/crypte/atelier/echanges | 3,05→2,89→3,05 | 12,1→10,8→12,9 | 3→2→4 | 12,5→9→12 | 8→7→8 | 0,5→0→0 | 33→31→31 |
| Signes : écart/noir/guet | 2,57→2,00→2,67 | 11,3→9,4→12,9 | 0,5→0→2 | 2→0→0 | 1→0→0 | 0→0→0 | 7→6→6 |
| Ambiance | 3,67→2,00→2,33 | 16,6→9,1→13,8 | 2,5→0→0,5 | 0→0→0 | 0→0→0 | 0→0→0 | 3→3→3 |
| Noms et soir | 3,57→3,81→4,04 | 14,1→13,3→18,5 | 2→0,5→2,5 | 1,5→1,5→1,5 | 1,5→1,5→1,5 | 0→0→1 | 14→13→13 |
| **Ensemble onze** | **3,15→2,96→3,21** | **12,7→11,1→14,4** | **8→2,5→9** | **16→10,5→13,5** | **10,5→8,5→9,5** | **0,5→0→1** | **57→53→53** |
| Ressources/comptes | —→3,00→3,40 | —→10,8→14,4 | —→0→1 | —→0→0 | —→0→0 | —→0→0 | —→3→5 |
| Sept sous-obstacle | —→1,90→2,10 | —→7,8→9,0 | —→0→0,5 | —→7→7,5 | —→4→4 | —→0→0 | —→10→10 |
| **Ensemble vingt** | **—→2,80→3,06** | **—→10,6→13,6** | **—→2,5→10,5** | **—→17,5→21** | **—→12,5→13,5** | **—→0→1** | **—→66→68** |

Onze scripts : **3,13/3,28 appels/tour**, **13,9/14,8 s/tour**, un repli par passe.
`comptes` passe de zéro à deux tours MJ grâce aux noms préparés : comparaison à préparation différente.

**Lots et anciens défauts, aux deux passes** (indices de saisie à partir de zéro).

- **56 partiel** : `ressources` dit « Je ne te dois aucune pièce » / « Je ne te dois rien ».
  `comptes` : « Gorm te rend les deux pièces » / « Gorm te rend les deux pièces dues » ; Brune refuse.
  Comptes après moteur : Gorm `rendu`, Brune débitrice de deux, or **24→26**. Échec narratif au soir (1–3).
- **59 tient sur les questions** : `echanges` affiche « Tu sais où est passé le gardien ? » aux deux passes,
  `soir-noir` « Tu dis : “il y a quelqu'un ?” ». Faux « Précise… » disparus ; « je réponds » sans contenu reste à préciser.
- **61 : cas réel corrigé**, `luna-restes-ambiance` n° 3 : « un mètre vers l’est, derrière toi dans ton orientation actuelle »
  aux deux passes, souvenir hors de vue conservé ; faux rejets spatiaux persistants (5).
- **65 tient sur l'attendu**, `relais` n° 22 : `element_33`, `element_9` aux deux passes,
  sans `brune`, `marchand`, `barbe_gorm`, `mains_gorm` dans les candidats ; surfaces visibles `echoppe_*` légitimes.
- **67 : prime corrigée**, `crypte` n° 24 : « Vingt pièces, quand tu me remettras l’anneau du veilleur » /
  « Vingt pièces, si tu me rapportes l’anneau du veilleur » ; trois appels chacun, aucun refus/relance/repli.
  Marché payé encore défaillant (2).

L'impression manquante revient dans `signes-ecart` n° 1 et 5 : « Ilse semble craindre Brune », deux passes ;
le noir reste sans lecture d'intention. `comptes` est désormais joué en ligne.
« Le refus précédent… » et « aucun autre bruit […] n'est décrit » ne réapparaissent pas.
Méta-langage seulement partiellement résolu : `relais`, passe 2 n° 21, conserve « Le geste envisagé dépasse aussi ce que tu peux trancher sans examen plus précis ».

**Nouveaux constats** (causes probables, aucune correction ni attribution certaine à un lot).

1. **Remboursement masqué**, `soir-appel`, passe 1 n° 4, réclamation à Aubin :
   « Elles sont à moi, et elles ne t'ont pas été remises. » Le moteur a remboursé, or 26 au tour suivant.
   Audit `parole`, portée `aucune`, comptes vides : parole potentiellement fausse admise, mais résultat effectif non narré ; état non inversé.
2. **Marché rejeté**, `soir-appel`, passe 1 n° 5, paiement d'une planche : huit appels,
   secours « La contrepartie immédiate est remise […] ». Le paiement est dans l'issue textuelle,
   absent des comptes structurés : récit correct du paiement refusé.
3. **Remboursement vrai rejeté**, `soir-appel`, passe 2 n° 4 : huit appels,
   secours « Aubin te rend 2 pièces […] ». Non-livraison extraite comme dette-objet absente,
   puis effet sourcé confondu avec effet créé par une parole : extraction/portée faillibles.
4. **Mauvaise cible**, `relais`, passe 2 n° 22, prise du pied-de-biche :
   « Tu ne vois rien de tel ici. Cet objet se trouve déjà à cette destination. »
   Après refus, Luna substitue le couteau déjà porté ; moteur protecteur, synthèse de refus incohérente. Aucune prise.
5. **Faux refus spatial**, `crypte`, deux passes n° 26, prise conditionnelle des crochets :
   affichage réduit à « Approche-toi de la trousse de crochets […] ».
   « derrière toi et à ta gauche » rejeté malgré ces repères dans l'attendu ; passe 2, locatif rattaché à Gorm : liaison cible/segment ambiguë.
6. **Lumière rejetée**, `crypte`, passe 2 n° 25, description : « Ta lanterne l'éclaire », six appels.
   Brasero écarté car hors de vue malgré `perception.contributions` niveau 2 : source visible et effet perçu confondus.
7. **Mot ordinaire censuré**, `comptes`, passe 2 n° 2, réclamation à Brune :
   « Elle maintient son refus […] » rejeté pour « refus », puis « Non. Je ne te rendrai pas ces deux pièces. »
   Garde de voix d'auteur trop large.
8. **Présentation rejetée**, `soir-noir`, passe 2 n° 2, « Qui est là ? » :
   « C'est Ilse » refusé comme nom non appris ; affichage à guillemets imbriqués
   « “Une voix inconnue te répond […] : ‘Qui est là ?’” ». Attribution citation/locuteur manquée ; nom donné seulement au n° 5.

**Limites et bruts.** Autres faux audits : ignorance (`signes-noir`/`signes-guet`), météo et ambiance.
Recherche de traces encore réduite à « Le sol en pierre », déjà dans f033364.
Le harnais recharge après sauvegarde et en fin de partie ; six premiers `regarder` précèdent la première sauvegarde.
Il capture les marqueurs des panneaux, pas leur rendu : aucune garantie générale du rendu persistant.
Ni code, modèle, consignes ni `main` modifiés ; aucune suite moteur supplémentaire.
Bruts du dépôt principal : `artifacts/verif-luna-fbcf0ff/` : quarante JSON, journaux, `relecture.txt`,
`revue-condensee.txt`, `obstacles.txt`, `analyse.py`, `textes.py`, `fil.py`, `mesures.json`, `verification.json`,
`constats.md` et `rapport-detaille.md` ; mesures détaillées par script et par passe conservées.
