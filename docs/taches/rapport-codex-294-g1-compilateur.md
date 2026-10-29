# Lot 294 — G1, compilateur public

29 octobre 2026 — `codex-g1-compilateur`, **non fusionnée**, base `230e7b3`,
code mesuré `7525f83`. **Analyse terminée ; invariant G1 non atteint, portage
non prêt à fusionner.** Aucun calcul actif ni rejeu Luna.

`compilateur.py` raccorde le libre aux contrats canoniques sur sélection du
contexte public ; `normaliser_proposition` copie sans réparer le sens,
`paroles.section_contenu` dérive le contrat, `sources` distingue le cache.
Copies, fidélité, contre-revue, G2/G4 conservés. **Aucun retour à l'ancien
interprète** ; réponses PNJ, descriptions, faits/qualifications gardent leurs
voies et contrôles transitoires. **172 tests / quinze fichiers verts**.

**Une passe, six scripts, référence exacte jouée puis cachée**, variantes
successives, un travailleur réduit : 91 saisies/variante, 30 tours MJ,
61 sans modèle. Aucun incident réseau, arrêt ou échec de recharge signalé.

| Mesure | Référence → lot |
|---|---|
| Appels ; appels/tour MJ | 99 → 98 ; 3,30 → 3,27 |
| Secondes/tour ; médiane | 9,82 → 9,95 ; 9,13 → 8,39 |
| Compilations corrigées comprises ; tours recompilés | 36 → 43 ; 5 → 11 |
| Admission au premier coup ; fidèle au contrat, lecture manuelle | 22/30 → 18/30 ; 20/30 → 14/30 |
| Refus de validation ; tours concernés | 8 → 14 ; 6 → 9 |
| Obstacles / relances narratives ; replis détectés | 9 → 9 / 8 → 5 ; 0 → 1 |
| Abandons explicites hors vrais obstacles du monde | 1 → 3 |

Admission ne prouve pas fidélité : mission en `propos` exclue de la référence,
deux questions devenues paroles et relecture superflue exclues du lot ; recherche
de traces non certifiée dans chaque variante. **Après refus : 3 → 8 tours
corrigés**. Référence : parole récupérée, refus correct retrouvé, écoute perdue.
Lot : mission et fredonnement admis mais infidèles, coup corrigé avec refus
parasite, cinq intentions non récupérées. Corrections de description :
deux demandes récupérées dans la référence, trois dans le lot.

| Famille | Écarts contre la référence |
|---|---|
| Perception/rappel/ambiance, relais | Odeur devenue parole ; consigne connue remplacée par lecture INT 12/2 min non exécutée ; ambiance récupérée après deux relances. 15 → 23 appels, 4,08 → 12,63 s/tour. |
| Gestes/opérations | Fredonnement sans son ; mauvaise opération sous poutre ; visibilité parasite avant bon refus du coup ; pied-de-biche remplacé par brasero. Vol composé devenu improvisation inventant « Gorm a le dos tourné », refusée sur la portée avant admission. Écoute toujours perdue, repli nouveau. |
| Mission, crypte/24 | **Typée et jouée après correction**, mission vide puis `anneau_veilleur` ; engagement moteur proposé à **22 pièces**, ni accepté ni payé, rendu/recharge valides. **Infidèle** : demande de prix devenue `negocier/0` au plafond, contre 20 dans la référence. Script : 25 → 25 appels. |
| Parole ouverte, echanges | Gardien abandonné sans parole, message « Réponse du MJ sans contrôle narratif. », contre question corrigée puis prononcée. 11 → 9 appels, baisse due à l'échec. |
| Ressources/comptes | Bois, nourriture, réclamations conservés. Achat de planche : réplique vide, mauvais objet, part devenue objet ; ni parole ni achat. Ressources 12 → 12 appels, soir-appel 22 → 15, baisse comprenant l'abandon. |
| Avis | Trois avis typés conservés ; avis-joueur 14 → 14 appels. |

Abandons : écoute commune, gardien et achat en plus ; le compteur de replis
sous-estime les échecs. Refus par cause : portée 3 → 3 (brasero parasite),
cible introuvable 1 → 3, personne inconnue 1 → 1, couverture d'écoute 1 → 1 ;
référence : écoute mal formée 1, impossible prématuré 1 ; lot : difficulté 2,
mauvaise opération 1, mission vide 1, parole mal formée 1, propriété inconnue 1.

**Taille/cache**, compilations avec corrections : entrée JSON moyenne
21 609 → 14 807 caractères ; entrée fournisseur **22 572 → 11 082 jetons**,
préfixe caché **11 812 → 4 700 jetons/appel**, **52,3 → 42,4 %**.
Au nominal : 22 617 → 11 011 jetons, dont 11 170 → 4 139 cachés. Deux scènes
sans réseau : environ −45 % de requête totale, consignes 40 364 → 3 547
caractères, schéma presque inchangé. **Aucun gain global de vitesse observé** ;
une passe ne démontre pas une causalité de délai.

Aucune suite relancée ni correction des tests préexistants du lot 295.
Requête d'interprétation aussi concernée dans `test_websocket_jeu`,
`test_fournisseurs_jeu`, `test_cache_kv_local`, `test_parole_corrections`,
`test_sans_message_technique`, `test_luna_noms` ; seul `test_cache_kv_local`
déjà adapté ici, à coordonner. `test_restes_fusions` ne passe pas par le MJ.

Bruts : `C:/Users/msics/donjon/artifacts/g1-294/`, douze parties JSON/HTML sous
`20261029-150541-9580/`, `fin-luna.json` : `ok=true`. Calculs et preuves :
`analyse-passe.json`, `tours-analyses.json`, `mission-jouee.json`, script
`analyser_passe.py`, `rapport-detaille.md`. **Raccord livré, fidélité et
récupération défaillantes : un correctif général borné reste nécessaire.**
