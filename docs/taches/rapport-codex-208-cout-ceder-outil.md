# Lot 208 — Surcoût de la conservation des outils

Diagnostic seul, 27 octobre 2026 : `1a3359a` contre `74a4bc4`
(`origin/codex-ceder-outil`), branche `codex-cout-ceder-outil` contenant
`c6c2de6`. **Aucun jeu modifié, aucun Luna ; un calcul à la fois, priorité
réduite.** Bruts, scripts et analyse détaillée exclusivement dans
`C:/Users/msics/donjon/artifacts/cout-208/`.

**Coût attribué.** `tools/mesure_cout.py`, mine fixe 1985, 4 h : recherches
698 → 987, neuves 423 → 510, nœuds 6 684 → 10 558, choix 2 333 → 2 336.

| PNJ × but | Recherches | Nœuds |
|---|---:|---:|
| Odon, fermeture coffre de paie | 2 → 114 | 78 → 2 262 |
| Rémy, fermeture garde-manger | 3 → 180 | 57 → 1 338 |
| Odon, faim | 7 → 8 | 1 079 → 1 495 |
| Autres | 686 → 685 | 5 470 → 5 463 |

Les deux devis de fermeture portent **89,4 % des nœuds supplémentaires**.
Par heure, recherches/nœuds : 347/4 009 → 389/4 950 ; 201/1 368 → 250/1 764 ;
43/383 → 127/1 217 ; 105/924 → 218/2 606 (`mine-cout.json`, `attribution.json`).

Chaîne : `choisir → plan_recours → recours → offre_sensee → promesse_autonome
→ _devis_proposition → devis_service → devis_pulsion → chercher`.
Les **1 359 appels de `valeur_bien` sont tous hors recherche**. À min 1,
l'offre des crochets d'Odon disparaît ; Rémy propose des pièces plutôt que sa
lampe. Sans offre exécutée, `executer` n'alimente pas `recours_propositions` :
les recours négatifs redemandent leurs devis. C'est principalement une
répétition de recherches après auto-refus, pas une évaluation dans chaque nœud.
`74a4bc4-mine-1985-4/trace.json` donne les appels ; `search-odon-*.json` et
`search-remy-*.json` capturent les mondes hypothétiques des services ;
`final.json`, le monde joué. Chronique, récit, souvenirs et empreintes restent
identiques à la mesure sans cette instrumentation supplémentaire.

**Écarts et intention.** Poêle : scène exacte de `test_ressources`, crue 7
sans souci, recharge par blocs, reproduite. Brune conserve sa torche au lieu
de la vendre ; les échanges suivants divergent, puis elle prend du bois et
rallume le poêle : à 270 min, éteint/0 → allumé/49, planches 2 → 1.
Conservation voulue, parcours indirect, aucun bois inventé. **Lanterne : ancien
écart non reproduit**, cause ouverte : trois tests du fichier
`test_gestes_par_noeud` verts sur chaque commit, six graphes inchangés ;
variantes préparée/directe identiques après recharge. Aucune assertion adaptée.

Crue 2024 **tirée**, 4 h : trois retours nouveaux retrouvés. Ilse 33/34 :
aide → aucune intention → aide ; `_secours_crus` perd puis retrouve Brune dans
la perception, supprimant/recréant le candidat. Aubin 82 : abri → aucune
intention → abri ; candidat sécurité absent puis présent, seuil précis restant
à attribuer. Captures `*-crue-tire/ilse-32.json`, `aubin-81.json`, relectures
`revalidation-crue.json`. Ce sont des effets de revalidation, pas des exigences
de l'invariant de cession. Suspects 253 → 3 ; sans recours 0 → 60 min pour
cette graine (distinct de la moyenne historique 15 → 30). Baisse sociale :
offres d'outils supprimées et occasions indirectes perdues ; mine 1985,
propositions 10 → 8, lectures 57 → 50, confidences 16 → 16. Relais et autres
graines non réaudités.

**Petit lot proposé, un invariant : mêmes dépendances crues, même résultat
de recours réutilisé, même négatif.** Dans `pnj_propositions.recours`, conserver
l'absence d'offre acceptable avec les dépendances des devis/valeurs : capacités,
doublons, besoins, droits, liens, engagements et accès. Prouver l'invalidation
sur Odon, Rémy et un moyen nouvellement disponible, sauvegarde/rendu compris.
Attendu : moins de devis, mêmes refus et trajectoires ; gain exact non mesuré,
retour au coût de base non garanti. Un cache de valeur par choix ne supprime
pas ces recherches ; évaluer seulement à la remise désaccorderait plan et
exécution. Aide/abri relèvent d'un autre lot.

**Décision utilisateur :** reprise de 202 sous réserve de coût/stabilité,
arbitrage capacité/compensation/ambition et horizon de flamme. Aucune garantie
générale ni fusion recommandée. Captures contrôlées après sauvegarde/recharge :
état, `regarder`, `scene_percue`. Pas de suite complète pour ce diagnostic.
Les essais initiaux de crue fixe ont conservé nuits/captures mais perdu leur
trace détaillée à la sérialisation ; les conclusions utilisent la passe tirée
complète. Détails et limites dans `analyse-detaillee.md` des bruts.
