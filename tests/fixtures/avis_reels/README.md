# Captures du lot 88

Crues 500 et 2024, départ tiré, joueur passif à la galerie de ronde, base
`c9245dd`. Profils, tirages et état mécanique inchangés.

Les relevés initiaux (`artifacts/88/mesurer.py`, `diagnostic-*.json`) isolent
le filtre `_sait`. La première capture de chaque nuit est reprise jusqu'à
la première occasion de confidence que ce filtre empêchait, juste avant
`social.bavarder` : Aubin à 72 min 25,5 s (500), puis à 102 min 25 s (2024).
Avant ces instants, aucun nouvel avis n'a encore été exprimé.

Chaque `.json.gz` contient le `Monde.data` complet, chargé puis réellement
sauvé/rechargé par les tests. Le joueur reste à distance des locuteurs : il
entend des voix, sans saisir les mots. Les tests contrôlent cette perception,
les avis conservés, les preuves propres des auditeurs et l'identité de l'état
complet pour dix minutes en bloc ou en tranches de quinze secondes rechargées.
