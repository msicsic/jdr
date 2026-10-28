# Lot 225 — Réessai lié à l'obstacle cru

**Branche `codex-reessai-obstacle`, non fusionnée**, départ `e4d8655`
vérifié, arbre initial propre. Aucun Luna ; au plus deux travailleurs de
simulation/tests, priorité réduite. Bruts exclusivement
`C:/Users/msics/donjon/artifacts/reessai-225/`. Aucune clé de signature Git
configurée : commit non signé.

**Diagnostic avant correction.** Mine 1985, joueur au puits : Odon vise
40 pièces à 0, 91 et 182 min ; renoncements capturés à **31, 122 et 213**.
Bram est témoin aux trois instants, avec Gaspard au deuxième, Mathe au
troisième. Le plan attend une occasion sans témoin devant le coffre de
paie : crocheter, puis ouvrir/prendre. Les trois captures donnent le même
monde et le même rendu après sauvegarde/rechargement.
Rejeu final du même départ : renoncements **31 et 147**, reprise à **114**
après constat sans témoin ; aucun retour à 91 ou 182 par délai. Monde/rendu
finaux rechargés identiques (`reproduction-finale.json`).

**Contrat.** `renoncer` conserve, par motif, des obstacles distincts pour
chaque but et moyen : étape, lieu, témoins crus ou arrivée inaccessible,
instant du constat. `choisir` consulte `renoncement_tient` et
`obstacle_patience` ; ni le temps ni une nouvelle date de regard n'effacent
l'obstacle. Un autre moyen reste possible et **ne fait pas oublier le
premier obstacle**, même s'il échoue à son tour. La patience reste 30 min ;
`REPIT` disparaît. Les inspections ordinaires des lieux concernés deviennent
des rondes de contrôle, avec les priorités, routes et coûts existants ; leur
période est `PATIENCE`, pas une autorisation de reprendre le geste abandonné.
L'inconscience propre cesse de retenir au réveil. Les enregistrements sont
sauvegardés et validés dans le seul bloc `renoncements` d'`esprits.verifier`.

**Raccords expressément autorisés pendant le lot.** `pnj._patienter`,
`pnj.agir`, `pnj._impasse`, puis `passage.faire_place` et
`passage._patienter` transmettent la cause effectivement rencontrée.
`corps.py` reste intact. Contrôle AST dans `synthese.json` : aucun changement
des fonctions des lots voisins, notamment `menager_flamme`, `_temoins` et
la perception ; aucun changement du MJ, de `social.py`, `ouie.py`,
`echanges.py` ou des scénarios.

**Vérifications.** 51 tests ciblés verts (50 mécanismes, un rendu) : capture réelle
d'Odon, autre PNJ/cause/scénario (Gorm, passage occupé), vérité cachée distincte
du constat, reprise après levée, autre moyen conservant l'ancien obstacle,
ronde sans nouvelle reçue, laps entier/découpé et monde/rendu rechargés.
La revue du banc préliminaire a révélé l'effacement indu de l'ancien obstacle
lors d'un autre moyen : correction et régression ajoutées, première suite
interrompue avant son achèvement. **Passe complète finale unique achevée :
2 462 tests / 286 fichiers, 2 014,763 s, zéro erreur, trois échecs bruts**.
L'oracle ancien de `test_rondes_resumees` imposait une demande de vivres dans
toute ronde détaillée ; remplacé par une scène qui contrôle inspections
regroupées et paroles/décisions conservées, **repassé vert (19,185 s)**.
Restent les **deux MiMo historiques `6 != 5`**, déjà reproduits par 213/223 ;
suite non verte. Aucun code moteur changé après le banc, aucune seconde
suite complète. Créneau dépassé par les vérifications.

**Banc final : 20 paires de 4 h**, cinq scénarios × 1985/7/42/2024 ;
20 références `bd45f65` relues du cache (identité des nuits avec le code du
223 attestée par son rapport), aucune référence rejouée. Classes 219 :
suspects **5→4** (aucun scénario en hausse), cycles **468→498**, préemptions
**53→53**, à expliquer **61→52** ; dérives **196→193**, états payés perdus
**6→6**. Zéro plantage/usurpation. Temps du cache non comparés.
Moyennes par nuit ; A/R = attente urgente / sans recours, en PNJ·min ;
S/F/D reprend exactement les familles du script du lot 183.

| Scénario | A/R avant → après | Renoncements | S/F/D avant → après |
|---|---|---|---|
| Relais | 0/0 → 0/0 | 0→0 | 9,5/3,5/1,438 → identique |
| Mine | 0/0 → 0/0 | 3→1,5 | 25,5/4,5/1,964 → 23/4,25/1,75 |
| Auberge | 0/20 → 0/0 | 0,5→0,5 | 11/4,25/1 → 12/4,25/1,094 |
| Crue | 196,25/0 → identique | 0→0 | 17,5/7,5/2,625 → identique |
| Hameau | 97,5/0 → identique | 0→0 | 31/7,5/2,667 → identique |

**Limites.** Un entier provenant d'une ancienne sauvegarde ne contient
aucune cause récupérable : il n'est plus un délai opposable, et le prochain
renoncement enregistrera son obstacle réel. La vérification ordinaire reste
soumise aux urgences et aux trajets admissibles ; elle ne promet pas une
inspection immédiate de tout lieu distant. Aucun certificat général
d'absence de toutes les boucles du jeu n'est revendiqué.
