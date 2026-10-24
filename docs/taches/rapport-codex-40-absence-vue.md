# Lot 40 — Vue courante et résultat d'une recherche

Branche `codex-absence-vue`, **non fusionnée**, base d'intégration `8443458`, brief
`f6968e7`. Correctif `c5f0b77`, signature SSH vérifiée. 24 octobre 2026.

## Invariant et fonctions

`MJ._echanger` fournit `perception.objets_visibles` : seuls les objets `visible=true`,
en références publiques. `narration.INSTRUCTIONS_AUDIT` admet l'absence limitée à cette vue
comme mécanique, source `perception`, même en réponse à une demande de recherche.
Cela ne prouve ni une salle vide ni un résultat de fouille. Au-delà (porte, contenant fermé,
noir, traces), une perception exécutée reste obligatoire. Un objet accessible au toucher
n'est pas nécessairement vu. Contrat documenté ; scénarios, modèle, prompt d'interprétation
et fichiers réservés à l'autre lot inchangés.

## Vérifications

- Console/MJ simulé/recharge : atelier 9 et 12, antichambre, porte, coffre fermé, noir.
  État et rendu contrôlés ; texte admis sauvegardé, texte refusé absent après recharge.
  Les quatre tests du lot 34 restent verts. Ciblés : **55 tests verts**.
- Empreintes Relais **2 h × 4 graines**, contre `8443458` : chronique, mesures et état final
  complet identiques. Quatre références manquantes calculées une fois et rangées dans le cache.
- Suite complète unique (`tools/tests.py --processus 3`) : **1 704 tests, 16 ignorés**,
  aucun échec ni erreur, **1 291,2 s**, priorité réduite.
- Luna `gpt-6-luna`, copies, priorité réduite, **une passe** par `tools/banc_multi.py`.
  `main` `42bb9c0` lu du cache, clé vérifiée avec son outil historique ; aucun rejeu.
  L'instrumentation actuelle ajoute les promesses et une préparation de relations inutilisée ici.

| Script | Appels/tour MJ main → lot 40 | Tours MJ main → lot 40 |
|---|---:|---:|
| atelier | 3,91 → 3,36 | 11 → 11 |
| crypte | 2,67 → 2,33 | 9 → 9 |
| luna-restes-ambiance | 4,00 → 2,00 | 3 → 3 |
| signes-noir | 3,50 → 2,00 | 2 → 1 |

Ensemble : **86 → 66 appels**, 3,44 → 2,75 appels/tour (25 → 24 tours MJ),
13,7 → 13,0 s/tour, replis 1 → 0. Lot 40 : **zéro refus `invention_protegee`**,
donc zéro refus d'absence visible de cette nature (six dans le constat d'intégration,
zéro sur `main`). Quatre obstacles narratifs dans l'atelier ; aucune erreur technique ou de recharge.

Textes affichés :

- Atelier 9 (**6 appels**, `main` 2) : « Tu aperçois la perche de bois 3 dans la cour.
  La hache et le couteau à lame fine sont aussi avec toi ; tu les portes, et tu ne
  distingues pas d’autres outils dans la cour. » L'audit cite bien `perception` pour l'absence.
- Atelier 12 (**4 appels**, `main` 2) : « Sous tes yeux, le sol de la cour est en pierre.
  Tu ne sais pas si une pierre détachable s’y trouve ni si elle pourrait caler une échelle ;
  le mur est encore à quelques mètres, hors de portée de main. »
- Crypte, écoute (**2 appels**, `main` 4) : « Tu tends l'oreille contre la porte de la crypte :
  rien de particulier ne te parvient. » Proposition puis contre-revue, résultat moteur direct,
  **trois minutes enregistrées** ; aucune écoute fictive validée en dialogue.

## Limites

Le classement reste sémantique : atelier 9 et 12 conservent six et quatre appels (voix
d'auteur, outils portés omis, « aucune pierre » opposée au sol en pierre). L'ambiance
conserve « aucun son ambiant n’a été signalé ». Ces défauts restent ouverts. Une passe,
des temps de cache et plusieurs lots entre les versions ne mesurent pas le gain propre au correctif.

Bruts et comparaison reproductible : `artifacts/codex-40-*`,
`artifacts/analyser-codex-40.py`, `artifacts/bancs-multi/20261024-175516-56464/` du worktree.
Pas de seconde passe Luna ni de banc long ; `main` inchangée.
