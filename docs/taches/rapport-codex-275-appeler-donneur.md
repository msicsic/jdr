# Lot 275 — Appeler un interlocuteur inaccessible

Branche **`codex-appeler-donneur`, non fusionnée**, base `7b58eb0` (code de
l'intégration `ac63223`). Aucune donnée de scénario modifiée, aucun appel Luna.

**Invariant.** Une étape sociale peut chercher le contact par l'appel négocié si
son interlocuteur est localisé, inaccessible et cru à portée de voix. Le préfixe
ne réalise ni venue, ni demande, ni acquisition ; la suite est replanifiée après
contact réel. Les échecs emploient le registre commun des recherches, sans délai
de rappel. Aucune position réelle du tiers n'entre dans la décision de l'appeler.

**Code.** `planification._appeler` estime la propagation sonore commune sur les
portes crues, la position connue du tiers et le centre de l'inspection locale.
`_chercher` et `rejoindre` raccordent ce moyen aux contacts ; `_parts_calculer`,
`_parts_remises` et les acquisitions d'objets portés y donnent accès aux demandes
et achats admissibles. L'inspection existante appelle `pnj.appeler` puis le
contrat négocié, sans nouvelle opération ou nouveau mode. `_couper` conserve la
frontière d'incertitude. La remise de nourriture déjà exécutée par le moteur est
également accessible à celui qui veut manger lui-même : attendre à une réserve
inaccessible ne doit pas être son seul devis. Le lot n'invente aucune livraison.
Raccord supplémentaire nécessaire dans **`pnj_propositions.recours`** : une
négociation après refus peut préparer le contact ; la contrepartie se décide
ensuite, sans offre présumée. **Ni `deliberation.py`, ni `agendas.py`, ni
`signes.py` modifiés.**

**Scènes.** La capture exacte crue 7, minute 270, est conservée en fixture
compressée. Ilse hèle Gorm ; il répond « Ici, viens ! », elle répond de même ;
aucune venue promise, appel retenu. Dans la variante où la porte est réellement
déverrouillée et où seul Gorm le sait, il promet de venir ; les retrouvailles
précèdent la demande, l'achat et le repas. Autre scénario : Hugues cherche à
acheter sa lanterne à Anselme après un refus de prêt ; le préfixe s'arrête à
l'appel et la méfiance conserve la lanterne chez Anselme. Contre-épreuves :
pièce sans ouverture acoustique, localisation inconnue, positions réelles cachées
modifiées, délai seul, recours de négociation. Mondes, rendus et scènes vérifiés
après recharge ; cinq minutes entières et découpées comparées intégralement sur
la capture et sa variante de venue.

**Arrêt instruit.** Le premier `fin.json`, `ok=false`, signale l'arrêt sur les
tests, **avant complément et banc**. Passe ciblée : 182 tests, 179 verts, une
assertion et deux erreurs, **591,132 s**, deux processus réduits. Les deux
épreuves existantes passent sur la base exacte `7b58eb0` (preuves conservées) :
les écarts sont donc liés au lot, pas des dettes préexistantes. Dans l'épreuve
de coût de `_chercher`, la cible était déjà localisée et joignable : la scène
précise maintenant qu'elle est perdue de vue, conformément à l'objet du test.
Pour Hugues, la trace base/branche est identique jusqu'au bruit nouveau du
couloir à **16 min**, qui rouvre ce lieu dans les deux versions. La branche
peut ensuite appeler à **18 min** Anselme localisé par Mathurine à 3 min,
contrairement à la base dépourvue de ce moyen. L'ancien oracle « jamais deux
appels dans un lieu, tous avant 12 min » était trop fort : chaque répétition
doit désormais consommer une **réouverture positive**, avec vérification de
l'absence de marqueur vain avant chaque cri et recharge monde/rendu/scène.
Enfin le test nouveau de négociation stockait à tort `besoin=faim` sur un refus
de bien ; celui-ci est indexé par objet, le besoin étant porté par son parent.
Ces **trois corrections portent sur les tests**, sans nouvelle règle du jeu.
Les **9 vérifications concernées passent**, **17,515 s**, puis les trois
fichiers complets : **47 tests verts, 36,518 s**. Les 17 fichiers déjà verts ne
sont pas rejoués : agrégat sourcé **182/182 verts**, sans temps de campagne
reconstitué (`test-cibles-275-verifie.json`). Avec les **45 tests verts**
initiaux (39,573 s), **227 tests distincts acquis**. Le complément des
importeurs directs est lancé séparément ; aucune suite complète ni Luna.

**Banc non encore exécuté ; critère « aucune hausse de suspects par nuit »
non établi.** Référence `7b58eb0` résolue une fois,
cache commun réutilisé quand disponible ; vingt nuits de branche, cinq scénarios
× quatre graines, 4 h, sonde 265/271 actuelle. Référence puis branche,
deux travailleurs réduits au plus, après les tests. `comparaison.json` conserve
les nuits, `bilan.json` compare les suspects 219 **nuit par nuit**, les appels,
les retrouvailles et S/F/D avec la fonction `cats` exacte du lot 183.
**Aucune absence de hausse ni amélioration naturelle n'est encore affirmée.**

Bruts et lanceur : `C:/Users/msics/donjon/artifacts/appeler-275/` ;
**`fin.json` écrit en dernier**. Le premier arrêt est archivé séparément. La
reprise exécute le complément puis le banc, et signale tout échec de tests,
plantage ou hausse des suspects par `ok=false`.
Limites : la portée est une estimation sur les croyances (position inconnue :
calcul sans cases), l'appelé garde ses priorités et son chemin propres ; aucun
accord ni résultat universel garanti. Lot à reprendre au fichier de fin avant
validation et fusion.
