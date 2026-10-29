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

**Vérifications acquises.** Première passe : **45 tests verts** (planification,
appel négocié, contact sous le but), **39,573 s**, deux processus réduits. Puis
les six premières régressions nouvelles : **6 vertes**, **16,387 s**. Une
septième couvre la négociation après refus. Une passe de vingt fichiers ciblés
incluant les sept scènes est lancée ; le complément des importeurs directs de
la planification et de l'appel est enchaîné au calcul détaché. Ce sous-ensemble
explicite ne constitue pas la suite complète.

**Calcul demandé, encore à valider.** Référence `7b58eb0` résolue une fois,
cache commun réutilisé quand disponible ; vingt nuits de branche, cinq scénarios
× quatre graines, 4 h, sonde 265/271 actuelle. Référence puis branche,
deux travailleurs réduits au plus, après les tests. `comparaison.json` conserve
les nuits, `bilan.json` compare les suspects 219 **nuit par nuit**, les appels,
les retrouvailles et S/F/D avec la fonction `cats` exacte du lot 183.
**Aucune absence de hausse ni amélioration naturelle n'est encore affirmée.**

Bruts et lanceur : `C:/Users/msics/donjon/artifacts/appeler-275/` ;
**`fin.json` écrit en dernier**. Un échec des tests arrête le calcul avant le
banc ; un plantage ou une hausse des suspects rend `ok=false`.
Limites : la portée est une estimation sur les croyances (position inconnue :
calcul sans cases), l'appelé garde ses priorités et son chemin propres ; aucun
accord ni résultat universel garanti. Lot à reprendre au fichier de fin avant
validation et fusion.
