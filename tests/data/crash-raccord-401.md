# Capture réelle du raccord, lot 401

`crash-raccord-401.json.gz` conserve le monde préparé, le rapport moteur et la
réponse auditée de `gpt-6-luna` avant le plantage `KeyError: '0'`, sur la base
`integration 4c160145` le 2026-10-31 (laptop). Banc `echanges`, graine 1985,
saisie « je dis à tous que l'eau monte et qu'il faut garder le feu ».

Les deux répliques fixées commencent par une désignation en minuscule. Le
découpage de leur jointure par un espace fusionne leurs segments ; chaque
réplique isolée est pourtant présente dans les faits du moteur.

`monde_avant` est reconstruit depuis la capture du tour précédent, avec
admission de sa réponse et reprise de l'historique effectivement affiché.
Sa préparation par `paroles.preparer_parole` a été comparée intégralement au
monde et au rapport capturés. Le test rejoue la saisie dans la boucle de jeu,
avec proposition et réponse simulées, puis relit le monde et l'affichage.

Bruts : `C:/Users/msics/donjon/artifacts/crash-raccord-401/`, notamment
`captures-luna.json.gz`, `capture-crash.json.gz` et `preparer_fixture.py`.
L'empreinte SHA-256 de la source figure dans `provenance` de la capture.
