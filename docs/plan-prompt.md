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
5. **Fournisseur local dans les objectifs** (raison initiale du chantier) : chaque lot garde un contrat propre dans
   `donjon/sources.py` et `donjon/fournisseurs/`, pour que le préfixe se mette en cache sur Luna comme sur un serveur local.
   Les deux caches diffèrent : selon la trace Luna d'Argon sur `9d53229` (`usage.attribution`), `/v1/responses` met en cache
   `tools` puis `instructions`, jamais l'entrée, et un changement de 7 jetons de `tools` (enum de `faits`) fait tomber le
   cache à 0 ; un serveur local met en cache `instructions` puis l'entrée (85 à 97 % avec `ordonner_faits`). L'invariance du
   schéma (L2) et des consignes (L3) sert les deux ; l'ordre de l'entrée (L1) sert surtout le local.
7. **`cache-kv-local` (`9d53229`, poussée sur `origin`)** a intégré la relecture de `d7913ce` : ordre du schéma, règles
   conditionnelles et `INSTRUCTIONS_RESULTAT` comme sur `main`, consigne de révision en fin d'entrée seulement en relance,
   `sources.py` (`ordonner_faits`, `ordonner_entree`, `voie_cache`), clé de cache par voie, fournisseur `local.py`. **L1 part
   de ce commit**, porté sur l'intégration actuelle.
6. **Schéma et consignes invariants** au long d'une partie ; ce qui n'est pas disponible ce tour est refusé par le moteur
   avec `attendu`, pas retiré du schéma.

## Lots (un invariant chacun, mesurés sur les quatre bancs de référence et les bancs ciblés)

- **L0 (lot 149)** — mesure sans code : taille envoyée par voie après mutualisation, part de chaque composant, préfixe commun
  entre appels successifs d'une même voie, jetons cachés ; ce qui casse le préfixe et dans quelle proportion.
- **L1 (lot 150, porté sur `codex-prompt-prefixe`, non fusionné ; réserve sur le critère des refus)** — préfixe ordonné par voie, depuis `9d53229` : clé de cache par voie, faits et entrée ordonnés du plus stable au
  plus variable, révision en fin d'entrée seulement en relance, fournisseur local ; même contenu des requêtes à l'ordre près.
- **L2 partiel, lot 158, branche `codex-schema-invariant`, non fusionnée** — schéma
  d'interprétation invariant : tous les modes et toutes les branches toujours présents,
  `faits` validé par le moteur, `suite` nullable dans une seule branche ; la question
  de faisabilité exige le geste avant tout ajout. Disponibilités refusées avec `attendu`
  avant audit. **0/92 variations** d'interprétation dans les deux passes Luna ;
  taille accrue, cache supérieur, aucun gain de secondes démontré. Critère des refus
  atteint sur 16 audits (160 appels, perte maximale 1/5). Schéma d'audit narratif
  encore variable, à reprendre dans un lot suivant.
  [Rapport 158](taches/rapport-codex-158-schema-invariant.md).
- **L3, lot 161, branche `codex-consignes-invariantes`, non fusionnée** —
  consignes d'interprétation permanentes, règles des quatre dossiers et de parole
  incluses sans condition de disponibilité ; indication du refus courant dans
  l'entrée. Sur huit captures Relais/atelier, **7/7 → 0/7 variations**, consignes
  moyennes **34 259,75 → 39 910 caractères**. Quatre parcours console identiques
  à la base, état complet et rendu rechargés. Suite unique **2 214 tests,
  16 ignorés, zéro échec/erreur**. **Validation partielle** : campagne
  Luna confiée à l’orchestrateur : « passe Luna faite par l'orchestrateur, à compléter »
  (aucune passe exécutée ici). Aucun gain de temps, cache réel ni critère des refus
  établi pour ce lot.
  [Rapport 161](taches/rapport-codex-161-consignes-invariantes.md).
- **L4 fait, lot 152, branche `codex-dossiers-proches`, fusionnée** — les quatre dossiers passent par
  `espace.objets_proches` (visibilité et `spatial.proche`), installations et outils compris ; les repères éloignés
  restent dans la vue. Les sauvegardes sans coordonnées n'établissent pas de portée au sol. Console et MJ simulé,
  état et rendu rechargés au Relais, à l'auberge et à l'atelier. Dix scènes identiques : `faits` 136 247 → 129 655
  caractères (−4,8 %), franchissements 6/10 → 2/10 et obstacles 4/10 → 2/10. Aucune consigne ni règle de trajet
  modifiée ; **critère Luna des propositions distantes non atteint** (deux actions et un détail encore proposés,
  refusés par le moteur). Le filtre des dossiers ne garantit pas à lui seul les propositions libres de Luna.
  [Rapport 152](taches/rapport-codex-152-dossiers-proches.md).
- **L5 (lot 151, partiellement réalisé sur `codex-portee-locale`, fusionnée)** — refus local de
  `HorsDePortee`, réponse exacte du moteur sans explication ni audit ; aucun déplacement automatique.
  Limite : la préparation s’arrête à la première cible hors de portée ; le recensement de toutes les cibles
  d’une proposition composée n’est pas garanti.
- **L6** — dégraissage des consignes (doublons socle/règles), relances mesurées.
- **L7** — catalogues d'écriture à la demande et surfaces génériques paresseuses.
  À exercer avec le dépôt au sol : la première passe du lot 154 a proposé
  `antichambre_sol`/`cour_sol` comme destinations. Ces surfaces restent hors du
  contrat des contenants ; leur présence dans les désignations est laissée à L7.
- **L8 fait, lot 154, branche `codex-poser-au-sol`, fusionnée** —
  `destination: "sol"` résolu dans le compilateur commun des déplacements et
  prélèvements ; séquences et effets d'improvisation suivent le même contrat.
  L'ancien identifiant de salle courante reste accepté ; autre salle refusée.
  État, scène et carte contrôlés après recharge en console avec MJ simulé.
  Le titre, l'information et le dossier de contre-revue présentent le dépôt
  « au sol, à tes pieds », avec destination publique `sol`, sans exposer la salle
  interne comme lieu du dépôt. Après reprise : **55 tests ciblés verts** ;
  une passe Luna atelier et deux dépôts, **40 appels/13 tours MJ**, deux objets
  posés sans refus (4 appels chacun). Le faux refus de l'atelier de la première
  passe est corrigé à la source de représentation ; aucune consigne d'audit ajoutée.
  [Rapport 154](taches/rapport-codex-154-poser-au-sol.md).

Chaque lot de L1 à L8 : tests ciblés après rechargement, suite complète une fois, Luna **deux passes** des quatre bancs de
référence et des bancs ciblés, critère de refus du lot 95 (pas plus d'un refus juste perdu sur cinq rejeux), appels et
secondes par tour MJ, jetons cachés par voie. Un lot qui touche le fournisseur local le mesure aussi sur un serveur local
quand il est disponible.
