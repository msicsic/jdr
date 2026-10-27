# Plan — le prompt du MJ : stable, borné à la perception, prêt pour un modèle local

Décidé le 2026-10-27 avec l'utilisateur, d'après la revue d'Argon (taille du prompt et stabilité du préfixe KV) et la
branche d'essai `cache-kv-local` (`9d53229`, non fusionnée). Objectif : le **temps avant réponse** du MJ, sur Luna
(`gpt-6-luna`) comme sur un serveur local OpenAI-compatible ; pas le coût en jetons pour lui-même.

## Constat (vérifié dans le code à `b5a23bb`)

- Le schéma de l'outil d'interprétation varie à chaque tour : liste des modes selon les catalogues disponibles,
  composition de `proposition.anyOf`, et `faits.items.enum = list(faits)`, les clés du dossier du tour.
- Les consignes varient selon la salle : `REGLES` de l'atelier, du franchissement, des obstacles et de l'espace ajoutées
  quand leur dossier existe ; ces dossiers sont calculés pour toute la salle, pas pour ce qui est à portée.
- `schema_faits_suite` est une copie de `SCHEMA_FAITS` plus `suite`, proposée avec lui. La mutualisation `$defs` du lot 93
  en replie une partie à l'envoi : les tailles se mesurent **après** elle.
- Les surfaces génériques (`<salle>_murs`, `_sol`, `_plafond`) sont envoyées comme objets complets à chaque tour.

## Décisions

1. **Le moteur garde ses salles** (secteurs de l'eau, de l'acoustique, de `trajet_estime`, croyances des PNJ). Côté MJ et
   joueur, la salle n'est plus une unité de capacité ni une frontière : aucune règle ni aucun dossier (`atelier`,
   `franchissements`, `passages_obstacles`, `espace`) ne dépend de la salle ; tout est borné à la perception et à la
   proximité (`spatial.proche`), comme `espace.dossier`. Un objet perçu mais pas adjacent n'est qu'un repère visuel, sans
   dossier technique.
2. **Poser au sol** : `destination: "sol"` (la case de Corvus), plus `salle.id`.
3. **Surfaces génériques paresseuses** : non envoyées comme objets complets tant qu'elles ne sont ni ciblées ni porteuses
   d'un détail établi ; le contrat « un élément d'ambiance ciblé est matérialisé ou déclaré non manipulable » reste tenu.
4. **Portée : refus local déterministe**, pas de déplacement automatique (le joueur déplace Corvus : le trajet a un coût en
   temps, bruit et lignes de vue). Une action refusée sur `HorsDePortee` répond par `reponse_du_moteur(exc)`
   (« Approche-toi de … »), comme une question de faisabilité, sans appel d'explication ni audit.
5. **Fournisseur local dans les objectifs** : chaque lot garde un contrat propre dans `donjon/sources.py` et
   `donjon/fournisseurs/`, pour que le préfixe se mette en cache sur Luna comme sur un serveur local.
6. **Schéma et consignes invariants** au long d'une partie ; ce qui n'est pas disponible ce tour est refusé par le moteur
   avec `attendu`, pas retiré du schéma.

## Lots (un invariant chacun, mesurés sur les quatre bancs de référence et les bancs ciblés)

- **L0 (lot 149)** — mesure sans code : taille envoyée par voie après mutualisation, part de chaque composant, préfixe commun
  entre appels successifs d'une même voie, jetons cachés ; ce qui casse le préfixe et dans quelle proportion.
- **L1** — clé de cache par voie (reprise de la seule partie correspondante de `cache-kv-local`) : mêmes requêtes.
- **L2** — schéma invariant : tous les modes et toutes les branches toujours présents, `faits` validé par le moteur,
  `suite` nullable dans une seule branche ; la question de faisabilité garde son contrat.
- **L3** — consignes invariantes : règles d'atelier, d'obstacles, de franchissement et d'espace condensées dans le socle.
- **L4** — dossiers bornés à la perception et à la proximité ; repère sans affordance pour ce qui est loin.
- **L5** — refus local de `HorsDePortee`, sans appel au MJ.
- **L6** — dégraissage des consignes (doublons socle/règles), relances mesurées.
- **L7** — catalogues d'écriture à la demande et surfaces génériques paresseuses.
- **L8** — `destination: "sol"`.

Chaque lot de L1 à L8 : tests ciblés après rechargement, suite complète une fois, Luna **deux passes** des quatre bancs de
référence et des bancs ciblés, critère de refus du lot 95 (pas plus d'un refus juste perdu sur cinq rejeux), appels et
secondes par tour MJ, jetons cachés par voie. Un lot qui touche le fournisseur local le mesure aussi sur un serveur local
quand il est disponible.
