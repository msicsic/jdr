# Lot 139 — La crue et les évacués du hameau

Branche `codex-crue-hameau`, non fusionnée ; base `3df20ff`. Aucun Luna,
au plus deux calculs à priorité réduite. Les scénarios existants et le moteur
restent inchangés. `crue_hameau.py` charge le nouveau JSON ; enregistrement minimal
dans `banc_pnj.py`, option `jeu.py --crue-hameau` et sauvegarde séparée.

**Personnages proposés, retouchables.** **Maël**, vannier au refuge, débrouillard
et serviable, connaît Gorm et Aubin ; **Sève**, raccommodeuse de filets à la galerie,
attentive et loyale, connaît Aubin et Ilse. Chacun possède quatre pièces et un
baluchon, huit caractéristiques, huit valeurs, des besoins ordinaires et un corps
humide modérément affamé/fatigué. Six PNJ au total. Arrivée par la digue avant la
nuit ; savoir déclaré sur les maisons noyées du hameau, aucune mesure initiale de
la conduite ni des vannes. Gorm et Aubin ont des constats de ces salles sèches
(valeur zéro ; aucun niveau sous le sol ou pente fictive). Aucun comportement dédié.

**Ressources mesurées.** Vivres 4→7 parts, bois du guet 3→4 charges ; foyers
150/120 min, autres bois 2×120 min, guet 4×90 min. Ces stocks permettent de chauffer
sans imposer leur distribution. En 1985, six parts restent en réserve, les deux
foyers finissent éteints avec du bois restant ; Brune reste affamée/froide. Maël
et Sève n'ont alors aucun besoin pressant. Aux autres graines, Brune mange et des
foyers sont alimentés ; Maël finit avec faim 66/67 (7/42), sans urgence enregistrée.
L'accès et l'entretien restent un enjeu, pas une pénurie totale imposée.

**Banc 4 h, départ tiré, joueur à la galerie.** Chaque cellule `crue → hameau`.
Le témoin est lu du cache `97e7198` (diff `donjon/` vide jusqu'à la base), sans rejeu.
Les totaux de minutes portent sur quatre puis six PNJ ; les temps CPU ne sont pas comparés.

| Graine | Avis | Adoptions | Échanges | Sans recours / attente (min) | Noir / eau (min) | Passages/h max |
| --- | --- | --- | --- | --- | --- | --- |
| 1985 | 7→15 | 0→2 | 28→81 | 60/60→100/95 | 150/215→30/150 | 18→28 |
| 7 | 2→5 | 0→0 | 15→68 | 60/15→60/0 | 5/60→0/70 | 14→15 |
| 42 | 5→6 | 0→0 | 18→38 | 60/5→60/0 | 65/150→65/70 | 14→34 |
| 2024 | 4→6 | 0→0 | 25→18 | 60/0→60/15 | 85/110→15/145 | 24→18 |

Zéro dispute, plantage, écart de vérification ou usurpation. Aucune répétition,
demande en boucle ni va-et-vient signalés. Observations : Gorm attend un devoir
confié (1985), alternances aller voir/autre but (42/2024), Brune 95 min dans l'eau
peu profonde (2024) ; elles ne démontrent pas une boucle nouvelle.

**Adoption et portée.** En 1985 à 193 min, Sève et Aubin adoptent l'avis d'Ilse sur
le palier. Sève n'a pas vu les salles basses ; leurs mesures lui viennent de paroles.
Elle a néanmoins déjà vu le palier mouillé : ce résultat ne prouve pas une alerte
avant toute exposition à l'eau. La prévision antérieure combine déjà des rumeurs
(`dit:brune`), remplacées par `dit:ilse`. Une adoption par un évacué dans une nuit
sur quatre ; aucune adoption de Maël, qui observe vite l'eau depuis le refuge.
Pas de garantie de fréquence, d'évacuation collective ou d'avantage tactique.

**Vérification.** Contrôle manuel `lieu`/`relie` (lot 137 absent de la base) et
`Monde.verifier`, quatre graines chargées/sauvées/rechargées ; deux scènes (1985/42)
identiques en bloc/découpées, état et rendu rechargés. Deux captures naturelles
(Sève/Aubin) vérifient adoption, prévision, chronique et rendu après recharge.
Quatre tests ciblés verts (2,10 s), après correction d'une attente de test trop forte
sur l'absence de tout constat. Quatre nuits de crue de 2 h : chroniques, mesures et
états complets strictement identiques à la base. La capture instrumentée reproduit
exactement l'état complet, la chronique et les
mesures de 1985, après correction de la sonde (retour de fonction omis au premier
essai, sans changement du jeu).
Suite complète unique : **2 076 tests, 228 fichiers, deux échecs MiMo `6 != 5`,
zéro erreur ni ignoré**, 2 061,03 s, un processus réduit. Ces deux échecs sont
reproduits seuls sur la base intacte `3df20ff` (deux tests, 1,57 s).

Bruts : `artifacts/crue-hameau-139/` ; captures compressées versionnées sous
`tests/fixtures/crue_hameau/`. Pas de clé Git de signature configurée : commit non signé.

Branche livrée sur `origin/codex-crue-hameau`, sans fusion dans `main`.
