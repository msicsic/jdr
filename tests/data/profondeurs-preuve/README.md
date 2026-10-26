# Captures du lot 92 c

Moteur de référence `9810f4a`, auberge 1985 tirée, mesures du lot 92 b.
Copies de captures d'`artifacts/aller-utile-92b/`, aucune sauvegarde utilisateur.

- `joss-622-epuise.json.gz` : recherche de faim sans plan, graphe coupé à
  profondeur 8 ; le certificat le rejoint à 6.
- `tilo-566-epuise.json.gz` : petit graphe épuisé de quinze états.
- `joss-622-plan.json.gz` : autre choix à la même minute, plan positif conservé.
- La mine réutilise `../cout-12h/mine-1985-480.json.gz`.

`contrats.json` est produit par `tools/rejouer_preuves_92c.py` contre l'archive
de `9810f4a` : plans et état projeté canoniques, coût flottant hexadécimal,
empreintes du monde complet et de `regarder`/`scene_percue` après recharge.
Les comptes de recherches ne font pas partie du contrat : la complétion doit
précisément éviter leurs reprises inutiles.

`etapes-calcul.json` adapte uniquement les trois empreintes de calcul de l'oracle
du lot 72. Génération gardée : `tools/rejouer_preuves_92c.py --depot .
--oracle-etapes --sortie tests/data/profondeurs-preuve/etapes-calcul.json`.
L'outil refuse d'écrire si plans, nombre d'appels, monde, lignes joueur ou rendus
diffèrent de l'oracle historique ; celui-ci n'est pas modifié.
