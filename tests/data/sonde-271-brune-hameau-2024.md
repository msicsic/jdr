# Réveils historiques de Brune — sonde 271

`sonde-271-brune-hameau-2024.json.gz` conserve des états et épisodes bruts
produits par le moteur réel, sans Luna, au commit `d7302a4` (parent immédiat
de la fusion 303). Scénario `crue_hameau`, graine 2024, départ tiré, joueur
`chambre_cloche`, appel du banc avec `2/60` h ; le pas d'attente du banc
termine à cinq minutes. Captures après les choix à 591 et 929 dixièmes.

Les épisodes comprennent les entrées observées, les décisions, les paliers
et les faits exécutés de la sonde. Aucun classement d'analyse ni preuve
`possession_nouvelle` / `lieu_cru_change` précalculée n'est enregistré.
Le test recalcule ces deux preuves avec la sonde courante, puis contrôle
les entrées, l'état complet, le rendu et la scène après recharge.

Bissection sur les fusions depuis `c293d3f` (271) : retour 929 présent au
parent `d7302a4`, absent à `8406756` (303). À 479, Maël croit le lieu de
Brune inconnu ; le 303 prépare le service par une question à Aubin sur sa
localisation. Cette parole supplémentaire change légitimement la suite de
la nuit. La fixture sépare le contrat de classement de cette évolution ;
un autre test conserve l'identité avec/sans sonde de la nuit actuelle.

Reproduction et bruts :
`C:/Users/msics/donjon/artifacts/hachage-316/capturer.py`,
`capture-avant-303.json.gz`, `capture-apres-303.json.gz`,
`fin-bissection.json`. Le générateur observe `deliberation.choisir` et copie
`monde.data` après les deux choix ; il n'altère ni état ni épisodes.
JSON transforme les tuples de l'API `percus` en listes : le test restaure
ce seul type, comme la fixture Aubin du lot 276.
