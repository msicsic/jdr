# Cas réels du lot 108

Captures de la base `a73a35d`, départ tiré, graine 2024, joueur passif
en `chambre_cloche` (crue) ou `galerie` (mine). Prises après l'attente
du moteur, minutes 140 et 70, sans modification des profils ni des jets.
Scripts et traces : `artifacts/avis-108/capturer.py`, `diagnostiquer.py`,
`diagnostic-*.json` ; sources de la base extraites par `git archive`.

La crue ne montre pas une répétition indue : Gorm voit la torche rallumée
à 241 entre les annonces 146 et 242, et à 382 avant celle de 444.
Les annonces minières de 76 et 79 portent sur `lampe_rechange_2` puis
`lampe_rechange_1`, deux objets distincts de même nom.
Les tests conservent ces annonces et contrôlent monde, chronique et rendu
rechargés, sur le même laps d'un bloc ou découpé.
