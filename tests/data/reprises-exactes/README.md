# Attentes sauvegardées — lot 118

`auberge-1985-600-attentes.json.gz` : capture réelle du banc auberge,
graine 1985, départ tiré, 600 minutes, code A3 `2fd4c4a`. Elle a été prise
avant la recherche de Lucien par `tools/mesurer_attente_bornee.py --cout`.
Deux efforts sauvegardés y portent la signature historique complète.

`attentes-temoin.json.gz` : issue de `garder(lucien, grenier)` et registre
d'attentes de Lucien après ce choix sur la même capture, produits par A3.
L'effort se réveille (`borne`) car les lectures ont changé depuis la signature
précédente. Le choix immédiatement répété doit attendre sans recherche.

Le test vérifie la représentation exacte du registre contre ce témoin, le
reste du monde, puis la sauvegarde/recharge et les deux rendus du joueur.
La clé transitoire peut être réduite ; le contrat durable de réveil ne doit
changer ni sa représentation ni ses lectures sans décision de comportement.

`etapes-calcul.json` : seuls visites du tas et diagnostics du lot 118.
Enregistrement après assertion stricte que plans, monde, lignes et rendus
restent ceux de `cout-12h/etapes-attendues.json`. Visites mine 5 478 → 4 579,
auberge 8 212 inchangées ; les oracles historiques et du lot 92 c sont conservés.
