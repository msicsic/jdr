# Tâche Codex 266 : rester près d'un proche qui a peur (3d, volet peur)

Le volet 3d livré par le lot 197 (`docs/taches/rapport-codex-197-empathie.md`, fusionné) couvre la faim et le froid
perçus d'autrui ; **la peur est restée hors lot**. Règle à appliquer, `docs/plan-relations.md` § 6.4 : un besoin
d'autrui perçu devient un but de l'empathique, envers qui il n'est pas hostile, pondéré par
empathie × (affection + 20) / 100, après ses propres besoins pressants et avant la routine ; pour la peur : **rester
près de lui** (la compagnie qui rassure). Le lot 53 (peur transmise, `docs/taches/rapport-codex-53-peur-transmise.md`)
établit déjà qu'un proche en détresse perçue ne rassure pas ; ici, c'est l'empathique calme qui vient rassurer.

## L'invariant
**La peur d'autrui, perçue par les signes et lectures communs (jamais lue dans son esprit), ouvre chez qui s'en soucie
le même recours de secours que la faim et le froid : rejoindre l'effrayé et rester à portée, ce qui compte comme
compagnie rassurante pour lui par la règle existante (`deliberation.autour`, écart de sécurité au temps vécu).** Le
but se tient tant que la peur reste perçue ; il cesse sur peur perçue disparue, détresse propre, péril, ou palier
supérieur, sans délai inventé. Même seuil de souci que 197 (altruisme + empathie + affection ≥ 100, rancune exclue).
Aucune exception de personnage ou de scénario ; aucune donnée de scénario ajoutée.

Points de contrat à tenir (notes du 197) : terminal de proximité commun (pas une case inventée), maintien et fin
explicites, coûts de déplacement et lectures dans `_entrees` (clé de mémoire, graphes, certificat) ; un compagnon déjà
présent et calme ne bouge pas ; aucun effet si l'effrayé est cru ailleurs sans localisation (le contact passe alors par
le sous-but commun du lot 226, `rejoindre`, sans position réelle lue).

## Vérification
- Scènes rechargées : Ilse effrayée (après un coup, ou dans le noir) et un empathique qui la rejoint, sa sécurité qui
  baisse ensuite au temps vécu ; autre cas de même nature (mine ou auberge) ; contrôle : personne sans souci ne bouge,
  rancune exclue, peur disparue → fin ; monde, rendu et scène identiques après recharge, même laps d'un bloc ou découpé.
- Tests ciblés des fichiers que le changement concerne (`test_empathie*`, `test_peur_transmise*`, `test_signes`,
  `test_echelle_choix`, `test_dynamique_besoins`) ; **pas de suite complète** (le superviseur la lance).
- Banc rapide : 4 h, cinq scénarios × quatre graines, référence en cache ; compteur 219 par nuit (aucune hausse de
  suspects ni nouvelle alternance), secours de peur comptés, minutes de sécurité urgente apaisées. Calcul long détaché.

Lot de 30 à 45 minutes. **Poste : le PC fixe**, au plus deux processus à priorité réduite. Pas de Luna.
Fichiers attendus : `donjon/deliberation.py` (candidats et fin), `donjon/planification.py` (terminal et lectures),
éventuellement `donjon/signes.py` en lecture ; ne touche pas `agendas.py` ni `echanges.py` (lot 260 en cours).

## Livraison
- Branche `codex-rester-pres` poussée (sinon commit local, et dis-le). Rapport d'une page
  `docs/taches/rapport-codex-266-rester-pres.md` ; entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans
  `C:\Users\msics\donjon\artifacts\rester-266\`. Termine par `LOT TERMINÉ` (résumé d'une ligne),
  `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
