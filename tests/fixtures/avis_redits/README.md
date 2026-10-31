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

Portage du lot 395 : la capture crue précède `faits_initiaux` (360). Sa
migration ancre la torche portée éteinte, sans reconstruire son histoire.
Le test déclare donc la vue allumée antérieure de Brune à 97 (allumage par
Brune attesté dans la chronique), puis la laisse percevoir l'état éteint
actuel à 140 ; l'extinction par Brune est attestée à 104. L'annonce déjà
faite à Aubin à 122 reste suivie. Ni objet, ni besoin, ni jet, ni audience
ne sont modifiés ; la confidence éventuelle reste une décision du moteur.
Sur décision utilisateur du 395, l'épreuve positive désactive le souci
spontané d'autrui dans la copie de scène (comme les lampes du 375), pour
écarter ses buts concurrents. Une épreuve séparée garde les profils d'origine
et vérifie l'absence de redite sans rallumage appris. La transmission spontanée
dans la nuit réelle n'est pas prouvée. La capture brute reste intacte.
Le test minier conserve le harnais historique du 375 ; les tests de provenance
du 360 s'exécutent sans ce harnais.
