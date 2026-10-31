# Tâche Codex 436 : repenser G20 (attitudes et signes) pour débloquer G8 (conception)

G20 (`docs/plan-refonte-mj.md`, ligne G20) est « livré non validé » : le lot 329 (branche `codex-g20-signes`, non
fusionnée ; rapport `docs/taches/rapport-codex-329-g20-signes.md` sur cette branche) faisait choisir à Luna une sélection
typée des personnages dont le moteur rend les signes, mais Luna n'a jamais choisi cette sélection et accolait les gestes
aux répliques. G8 (producteur d'ambiance en fond, puis G9, G10, G11, U-A) dépend de G20 : l'ambiance cosmétique ne doit
contenir « aucune parole/attitude inventée ». Le lot 176 (attitudes extraites par l'audit narratif) a été abandonné.

Depuis, la refonte a choisi les **actions directes** pour les gestes courants (décisions du 2026-10-29,
`docs/conception-valeur-llm.md` § 8) : `observer <personnage>` est déjà local et rend les signes et impressions par le
moteur, sans modèle (lot 3c, puis G5/G6). Lis `AGENTS.md` (contrat du MJ : « Mécanique » liste les signes perçus ;
« Ambiance »), `docs/etat-dev.md` (court), `docs/conception-refonte-mj.md`, `docs/conception-valeur-llm.md`, le plan de
refonte (G20, G8 à G11, U-A) et le rapport 329.

## Question (une seule)
**Quelle est la plus petite garantie qui remplace G20 et suffit à G8 : une attitude affichée au joueur vient toujours
d'un signe ou d'une impression encore perçus, rendue par le moteur ; la prose libre et l'ambiance n'en affirment aucune.**
Évalue au moins : (a) attitudes seulement par la voie directe (`observer`, regard, bilan du moteur) et garde
déterministe qui retire de la prose cosmétique toute attribution d'attitude à un PNJ nommé ou désigné (sur le modèle des
gardes de noms et de voix) ; (b) sélection typée par Luna (329) ; (c) autre voie que tu trouves. Pour chacune : ce
qu'elle garantit, ce qu'elle ne garantit pas, coût en appels, ce qu'elle retire au joueur, contrôles existants
retirables. Mesure sur les fils existants (329, bancs `signes-*`, `attitudes`, captures) sans modèle si possible :
combien de réponses actuelles contiennent une attitude, combien la garde (a) retirerait à tort ou laisserait passer.

## Contraintes
**Conception seule : aucun code du jeu modifié** (un prototype de garde dans `artifacts/` est permis pour mesurer).
Poste : le laptop. Lots en cours : 402 (calcul), 431 (admission préalable), 435 (S1o). Deux processus au plus,
priorité réduite. Pas de passe Luna sauf une courte si indispensable pour trancher.

## Livraison
Branche `codex-g20-repense`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-436-g20-repense.md` : options,
mesures, **recommandation** et brief du lot de réalisation (invariant, fonctions, vérification) ; si une décision de
l'utilisateur est nécessaire (par exemple retirer quelque chose au joueur), formule-la en une question avec ta
recommandation. Entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche
entre accents graves). Bruts dans `C:\Users\msics\donjon\artifacts\g20-repense-436\`. Termine par `LOT TERMINÉ`,
`CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
