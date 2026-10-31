# Lot 409 — S1k, refus retenus (première partie)

31 octobre 2026 · `codex-s1k-refus-recours` · base exacte `integration 64e3b2b4`.
Livraison partielle cohérente autorisée par le brief ; **S1k reste ouvert pour les recours**.

**Invariant porté.** Le registre historique `refus`, ses demandes, raisons, dates,
causes, offres et contre-offres passent par `donjon/memoire.py`. La vue
`reponses_retenues` rend des copies profondes ordonnées, sans création d'esprit,
apprentissage, acquittement ni péremption. `retenir_refus` et `oublier_refus`
conservent les façades de `deliberation`, la séquence des crochets, le remplacement
de la demande gratuite par l'achat et les clés et l'ordre sauvegardés.
Les admissions copient les détails imbriqués ; aucun retour mutable n'est exposé.

Les opérations nommées associent la cause interrogée à la dernière réponse,
acquittent une contre-offre de service effectivement accomplie, lèvent les refus
sociaux du bénéficiaire ayant constaté le service et installent les refus dans
un devis isolé. La validation et celle des contre-offres sont également portées.
Les lecteurs de `planification`, `pnj_propositions`, `agendas`, `relations`,
`propositions`, `echanges` et deux outils utilisent la vue. La révision du repère
de localisation était déjà dans la porte de croyances du 397.

**Politiques conservées.** `deliberation.tient`, `moyens_crus` et
`pnj_propositions.refus_tient` gardent leurs décisions. Une perte de moyen, une
date de regard rafraîchie ou le seul temps ne lèvent pas les refus matériels,
offres et contre-offres qui ne l'étaient pas auparavant. Les refus d'humeur
gardent leur délai historique de 120 minutes ; aucune garantie contraire n'est
ajoutée. Les choix, paroles, délais, tirages et publications au choix réussi
ne sont pas remaniés. Aucun registre nouveau ni appel au modèle.

**Contrôle et vérification.** Inventaire AST dédié : **64 → 27 expressions**
hors `memoire`, dont la seule déclaration exacte de schéma et 26 homonymes
(causes/répliques, diagnostics, résultats de banc et propositions du MJ).
Zéro accès direct au registre des refus restant. Les cinq registres de recours
ont leur inventaire fermé : **85 → 84**, l'écrivain de `demande_refusee` se
déplaçant avec la rétention du refus. Contre-épreuves : clés indirectes, alias,
boucles, méthodes détachées, retours, créations et mutations.
Les nouveaux tests contrôlent copies et admissions, projection, ordre des
réponses à minute égale, survie à 45 épisodes et au temps/perte de fortune,
validation, puis la capture historique d'Ilse (crue 7, minute 353) et une autre
fourniture. État complet, ordre JSON, lignes, rendu, scène et émissions sont
comparés après recharge et deux minutes entières ou quatre tranches.
**Premiers résultats :** cinq nouveaux tests verts (capture réelle et seconde
fourniture comprises) ; 65 tests métier/socle exécutés, deux sous-échecs d'une
même méthode `offre_sensee` reproduits à la base exacte sans modification
d'assertion. Une erreur de recharge `refus_retenus` (Hugues/Mathurine sur la même
case) reste à attribuer par rejeu de cette seule méthode sur la base.
Tests voisins et empreintes lancés par `run409.py` ; **calcul en cours**,
conclusion attendue dans `fin.json`, écrit en dernier. Celui-ci conserve les
rouges existants dans son champ `succes`, sans les masquer. Les résultats
complets restent à lire ; aucune identité des empreintes n'est encore affirmée.

**Bruts et suite.** `C:/Users/msics/donjon/artifacts/s1k-409/`.
Empreintes lancées : 2 h × graines 1985/7/42/2024 × Relais/mine/auberge/crue,
référence exacte en cache, deux travailleurs réduits au plus, côtés successifs.
Pas de suite complète ni Luna. Aucun fichier attendu du 407 n'est touché ;
le calcul du 402 reste indépendant. Dernière actualisation : `origin/integration`
à `64e3b2b4`, pas de fusion supplémentaire requise à ce stade.
Restent `demande_refusee`, `recours_propositions`, `recours_services`,
`recours_intermediaires`, `service_en_cours`, leurs écrivains et validations.
Le contrôle AST reste syntaxique et local, sans preuve de tous les flux
interprocéduraux possibles de Python.
