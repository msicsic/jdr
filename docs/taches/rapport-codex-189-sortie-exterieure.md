# Lot 189 — sorties terminales et déplacements internes

Branche `codex-sortie-exterieure`, **non fusionnée**, base `60617f9`, laptop,
sans Luna. Deux travailleurs de calcul au plus, priorité réduite ; bruts
exclusivement `C:/Users/msics/donjon/artifacts/sortie-189/`.

**Invariant.** `exterieur: true` termine la présence : un plan interne ne
peut l'emprunter ni promettre une inspection après arrivée. `presence.interieur`
fournit la géométrie filtrée et son cache privé ; `salles_interieures` sa
composante interne. `Vue` l'utilise pour candidats, estimations, retours et
bornes ; `_entrees` contient déjà cette carte (`v.salles`). `pnj.parcours` et
`_marcher` partagent le filtre ; `_pas` et `_avancer_de` revalident la
transition courante. Un autre passage intérieur vers la même destination
reste admissible. Le joueur garde son départ volontaire. Les tests 181
déclenchent le départ d'auteur par `presence.franchir`. Aucun scénario ni
fichier réservé aux autres lots n'est modifié, aucune migration.

**Cas réel.** La reconstitution de la base retrouve les **439 événements** de
la chronique 187 à l'identique, joueur à son placement initial. Captures juste
avant Brune **120 min** et Ilse **177 min** : leurs recours reprennent dans
les lieux (beffroi à 122, crypte à 179). Deux minutes entières/découpées et le
rechargement donnent le même état complet et le même rendu. Autre cas : ronde
d'Aubin. Tests aussi de la clé, du cache joueur chauffé, d'une ancienne sortie
copiée, d'une autre route intérieure et du départ joueur, avec/sans cases.

Complément 188 : hameau 2024, joueur dans `chambre_cloche`, captures exactes
de Gorm à **352 min 54,7 s** (entretien du brasero, recherche d'Aubin) et
d'Aubin à **380 min 39,7 s** (prévenir Brune), reconstituées sur la base,
archives du PC fixe absentes. Présents à 354/382 min (crypte/beffroi), état et
rendu identiques après recharge et deux minutes entières/découpées.

**Tests.** Suite unique : **2 297 tests, 265 fichiers, 2 304,410 s**, aucun
échec ni erreur. **16 ignorés** : 15 pour les dépendances MiMo facultatives,
un pour `jsonschema`, absents de cet environnement. **34 ciblés finaux verts**,
dont deux compléments après le passage du fichier et la marche finale.

**Bancs.** **16/16 empreintes de 2 h identiques** à `60617f9` : Relais, mine,
auberge, crue × 1985/7/42/2024 ; chronique, mesures, état complet, repères et
récits/souvenirs compris ; 32 recharges état/rendu identiques. Références
exactes manquantes constituées une seule fois ; aucun temps comparé.
**Cinq nuits hameau de 4 h**, graines 1/1985/7/42/2024 : **zéro PNJ parti,
usurpation ou plantage**, cinq états/rendus rechargés identiques. Deux bascules
isolées ; maxima de passages horaires **24/40/22/19/28**. Aucun constat de
boucle « à expliquer » ; observations `fige_presse` de Gorm (1985) et une
alternance aller voir/autre but (7). Contrôle exact 1985 : Sève part à 192 sur
la base ; pic **20 → 40/h** avec le correctif. Le pic comprend achat, deux
inspections de bruits distincts et ronde ; aucune boucle sans nouvel événement
identifiée, hausse conservée comme point de surveillance.

**Limites.** Aucun but autonome de départ n'est ajouté : une future évacuation
hors des lieux devra annoncer cette conséquence terminale. Départ/retour
d'auteur conservés, aucun temps extérieur simulé. L'absence de toutes les
boucles entre besoins n'est pas garantie. Aucune clé Git configurée : commit
non signé. Aucune fusion ni modification de `main`.

**Livraison locale.** Poussée rejetée par la revue automatique : risque
d'export privé, propriété/destination du remote GitHub non établies par les
instructions de confiance. Commit conservé localement, sans nouvelle tentative,
conformément au brief.
