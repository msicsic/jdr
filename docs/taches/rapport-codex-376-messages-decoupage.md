# Lot 376 — Perceptions indépendantes du découpage

Branche `codex-messages-decoupage`, base `origin/integration 2887c541`, PC fixe
`MSI-DESKTOP`. Bruts : `C:/Users/msics/donjon/artifacts/messages-decoupage-376/`.

**Cause et contrat.** La capture `evaluation-echeance-371/auberge/accord.json`
reproduit l'écart bloc/minute par minute : le bilan comparait les extrémités de
chaque action, écrasait les passages et omettait l'observation immédiate des minutes
de combustion. Souvenirs, portraits et signes dépendaient aussi de la fin d'action.

`pnj._observer_presences` rend maintenant les transitions réellement perçues,
aux événements, minutes et issues corporelles, puis alimente les mémoires publiques
existantes et les signes. Une extinction dit une perte de vue sans départ inventé.
`bilan_presences` clôt les transitions restantes. Aucun nouveau registre d'esprit
ni condition de scénario.

`ecoute.rendre_evenement` rend chaque son avant regroupement ou éviction de la file.
Le fond inchangé se compare au dernier bruit perceptible sauvegardé ; les paroles
restent distinctes. Le moteur évite les doubles rendus et ne déduplique plus toutes
les phrases des tranches d'attente entre elles.

**Preuves.** `reproduction.json` / `reproduire.py` : auberge différente avant,
mêmes messages après ; état et rendu rechargés identiques entre bloc et découpage
à l'auberge et au Relais. Tests : frontières 599/600/601, transaction moteur/journal,
attente publique interrompue, déplacement caché. Les transactions neutres de durée
contrôlée exercent `_executer_simple` ; seuls les numéros d'action du journal et
de provenance des paroles sont neutralisés pour leur comparaison d'état.

**Adaptations voulues.** `test_presences.py` remplace « une ligne par personnage »
par les transitions perçues. `test_signes.py` conserve l'impression vue avant la
disparition, interdit toute impression après celle-ci et dans la projection actuelle
de l'absent. Noir/dos/cible cachée, provenance vocale et journal restent contrôlés.

**Vérification.** **114 tests verts**, douze fichiers concernés, zéro échec,
erreur ou saut, **146,3 s** (`tests-final.json`).
Empreintes **2 h × 4 graines × auberge/Relais**, référence `2887c541` lue dans
le cache, deux travailleurs, priorité réduite : **8/8 nuits sans plantage ni
usurpation**. Identiques sur chaque paire : empreintes physiques à 5/60/120 min
et issue, chronique, mesures, récit, souvenirs des PNJ, constats d'audit, avis,
refus de contact et approches. Les états complets ne concordent que sur **2/8**
nuits (auberge 1985/7) : écart sur auberge 42/2024 et les quatre Relais. Le code
1 du comparateur signale cette divergence stricte, pas un plantage. Aucun temps
CPU comparé au cache. `empreintes.json`, `analyse-empreintes.json` et
`fin-empreintes.json` gardent les résultats ; ni suite complète ni Luna.

**Limites et intégration.** Le fil peut être plus long qu'un résumé d'action.
Les mémoires publiques, lectures spontanées et journaux changent volontairement.
Préfixes de cinq minutes des six nuits : objets/joueur, esprits et chronique
identiques ; journal seul au Relais, état entier identique à l'auberge (`prefixes/`).
**Limite : les états complets finaux de 2 h ne sont pas archivés par le comparateur ;
les six écarts finaux de hash ne sont donc pas intégralement attribués.** Les
indicateurs ne prouvent pas l'identité de toutes les données internes finales des
PNJ. Aucune référence de deux heures rejouée pour cette attribution (`analyser.py`).
Les libellés de durée et les interruptions restent ceux de chaque commande.
Recouvrement à surveiller : `moteur.py` avec 369 et les correctifs du 375 ;
aucune modification des registres des lots 374/377 ni de S0/S1. Lot livré avec
cette limite de vérification explicite ; branche poussée, fusion au superviseur.
