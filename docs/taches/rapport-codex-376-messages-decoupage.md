# Lot 376 — Perceptions indépendantes du découpage

Branche `codex-messages-decoupage`, base `origin/integration 2887c541`, PC fixe
`MSI-DESKTOP`. Bruts : `C:/Users/msics/donjon/artifacts/messages-decoupage-376/`.

**Cause et contrat.** La capture `evaluation-echeance-371/auberge/accord.json`
reproduit des messages différents pour trois minutes d'un bloc ou minute par minute,
malgré le même état final. Le bilan comparait les extrémités de chaque action et
écrasait les passages intermédiaires ; les minutes de combustion n'étaient pas
observées aussitôt. Les souvenirs visuels, portraits et signes spontanés dépendaient
également de la fin d'action : un visage vu avant l'extinction pouvait être oublié.

`pnj._observer_presences` rend maintenant les transitions réellement perçues,
aux événements, minutes et issues corporelles. Un passage bref conserve son
apparition et sa disparition ; une extinction dit une perte de vue, sans départ
inventé. La même collecte alimente les mémoires publiques existantes et le bilan
des signes. `bilan_presences` clôt seulement les transitions restantes. Aucun
nouveau registre d'esprit, aucune condition liée au scénario.

Les sons se rendent à leur événement avec `ecoute.rendre_evenement`, avant
qu'un regroupement de fin d'action ou la file bornée puisse les perdre. Le fond
inchangé est comparé au dernier bruit perceptible de la file déjà sauvegardée ;
les paroles restent distinctes. Le moteur ne répète pas les sons déjà traités et
ne déduplique plus les phrases de toutes les tranches d'attente entre elles.

**Preuves.** `reproduction.json` et `reproduire.py` gardent le rejeu avant/après
de la base sur la capture réelle et le Relais : auberge différente avant, mêmes
messages après ; états et rendus rechargés identiques entre bloc et découpage
dans les deux scènes. Les régressions couvrent aussi les frontières 599/600/601,
les transactions du moteur avec journal, l'attente publique interrompue et un
déplacement entièrement caché. Les transactions neutres de durée contrôlée
exercent `_executer_simple` ; les numéros d'action du journal et de provenance
des paroles sont seuls neutralisés pour leur comparaison d'état.

**Adaptations voulues des tests.** `test_presences.py` abandonne le résumé
« une ligne au plus par personnage », incompatible avec la composition des laps.
Les attentes de passages vus, regard tourné, rendu et journal rechargé restent
contrôlées. Dans `test_signes.py`, une impression perçue avant la disparition
reste dans le fil : aucune impression après cette disparition ni dans la
projection courante du personnage devenu invisible. Les cas noir/dos/cible
cachée et les contrôles de provenance des voix restent inchangés.

**Vérification.** **114 tests verts**, douze fichiers concernés, zéro échec,
erreur ou saut, **146,3 s** (`tests-final.json`).
Empreintes 2 h, auberge et Relais, graines 1985/7/42/2024, référence de la base
d'intégration : lancées après les tests, deux travailleurs, priorité réduite,
cache partagé conservé ; fin attendue `fin-empreintes.json`. Pas de suite
complète ni Luna. La référence choisie isole le lot des autres fusions depuis `main`.

**Limites et intégration.** Le fil peut être plus long qu'un résumé d'action.
Les mémoires publiques et lectures spontanées sont désormais alimentées pendant
le laps : l'identité des empreintes complètes avec l'ancienne version n'est donc
pas présumée ; les écarts devront être lus avec la chronique et les mesures.
Les libellés de durée et les interruptions restent ceux de chaque commande.
Recouvrement à surveiller : `moteur.py` avec 369 et les correctifs du 375 ;
aucune modification des registres des lots 374/377 ni de S0/S1. Fusion au superviseur.
