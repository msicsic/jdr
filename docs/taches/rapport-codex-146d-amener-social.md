# Lot 146 d — livraison partielle : fermeture d'un passage hors service

Branche `codex-amener-social-d`, **non fusionnée**, base `bd11a3d`.
Le lot se limite au correctif moteur préalable autorisé par le brief.

**Invariant.** Une manœuvre préparée avant la destruction ou le dégondage du
battant ne peut pas le refermer. `pnj._executer_effet` écrivait directement
`ouverte=False`, contrairement à la préparation joueur. La prochaine copie
(`Monde.copier`, notamment dans les devis d'engagement) levait alors
`Passage incohérent`. `portes.valider_fermeture` porte maintenant les mêmes
préconditions matérielles pour le joueur et le PNJ : absence de cale, intégrité
positive, battant attaché. Chaque refus a une seule cause et son `attendu`.
Le PNJ échoue sans annoncer une fermeture et constate l'état qu'il a touché.
Le contrôle de sauvegarde reste strict ; aucune réparation tardive de l'état.

**Preuve ciblée.** Deux scènes de crue rechargées, graines 2024 et 42,
battant brisé par `force.briser` ou dégondé par la stabilisation des fixations,
avec promesse de fermeture déjà enregistrée. Le geste est effectivement à
portée. Réinjection en mémoire de la seule fonction de la base : les deux
variantes échouent sur `Passage incohérent` à la copie suivante. Correctif :
copie, devis et recharge réussissent ; passage ouvert/déverrouillé, croyance
actualisée, absence de fausse chronique « ferme », état complet et rendu
identiques après recharge, battant brisé/dégondé visible. **25 tests ciblés
verts**, dont les engagements de déplacement, les fins et routes d'amener et
les correctifs voisins.

**Vérifications finales.** Suite complète unique : **2 204 tests, 251 fichiers,
1 250,899 s**, deux échecs MiMo historiques `6 != 5`, zéro erreur/ignoré.
**12/12 empreintes 2 h identiques** à `main` `812ebe5`, Relais/mine/auberge,
chronique, mesures et état complet ; références relues sans rejeu.
Crue 4 h × quatre graines : **4/4 états complets identiques** à la référence
cachée `ef65e55`, aucun arrêt/usurpation ni nouvelle boucle ; mêmes constats
`voir_alterne` (42) et `eau_longue` (2024). Galerie **3/8**, eau **128,75 min**,
attente urgente sans recours **60 min**, maximum horaire des passages **13,25**
en moyenne, inchangés. **`VERIFIER` + spatial 0,2 : crue fixe 42 et 2024,
2 h chacune, sans arrêt** (111,78 et 113,75 s).
Deux processus de calcul au plus, priorité réduite ; le dernier fichier de la
suite a chevauché les empreintes à un seul travailleur. Temps cachés non comparés.
Bruts : `C:\Users\msics\donjon\artifacts\amener-146d\`.

**Limites et reste.** Le fil historique crue 2024/120 du lot 146 c est perdu
et n'est pas reconstitué ; la reproduction prouve un mécanisme capable de
produire exactement l'erreur, pas qu'il était l'unique cause de ce fil.
Pas de sous-buts sociaux réintroduits, ni d'agenda d'évacuation ajouté aux
données. Plus proche/portée vocale, avis, demande autonome, refus durable et
réveil, accompagnement et épreuve collective vers la galerie restent à faire.
La recherche peut encore proposer une fermeture selon une ancienne croyance ;
le présent lot garantit son refus matériel, pas l'absence de toute répétition
de plan. Aucun succès d'évacuation n'est revendiqué. Aucun Luna ni fichier MJ
réservé modifié. Aucune clé de signature Git configurée : commit non signé ;
branche seule poussée, `main` intacte.
