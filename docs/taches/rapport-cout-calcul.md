# Rapport : le coût de calcul d'une nuit, sans rien changer à ce que font les PNJ

Branche `cout-calcul`, partie d'`origin/main` 06602a6, poussée sur `origin`, non fusionnée (à fusionner
en dernier : voir « Fusion »). Tâche : `docs/taches/cout-calcul.md`. Détail technique dans
`docs/plan-planificateur.md`, section « Coût de calcul, suite (branche `cout-calcul`) ».

## Contrat tenu

Rien ne change dans ce que décident les PNJ. Pour chaque nuit, `main` puis la branche : empreinte de
la chronique, des mesures (hors comptes de recherches et de choix), du récit, des souvenirs, de l'état
final complet (`monde.data`), des repères du banc (minutes 5, 60, 120, 240, 480 et issue) et des
recherches neuves du planificateur (PNJ, but, nœuds examinés, issue). Outil : `tools/empreintes_nuits.py`
(nouveau ; `jouer` puis `comparer`).

- **32 nuits identiques** sur tous ces points : 4 scénarios × graines 1985, 7, 42, 2024 × départ tiré
  et fixe, 8 h (`artifacts/cout/main-1.json` contre `branche-1.json`, et de nouveau dans chaque passe
  de mesure).
- **Contre-vérification indépendante** par l'outil de Codex (`tools/comparer_bancs.py --empreintes`,
  depuis un worktree détaché d'`origin/codex-outils` 60b8716, `--reference 06602a6 --branche
  cout-calcul`) : « identique : chronique, mesures et état final complet, nuit par nuit », 16 nuits en
  départ tiré, 16 en départ fixe.
- **`planification.VERIFIER` et `spatial.VERIFICATION` à 0,2** sur une nuit de 8 h de chaque scénario
  (graine 42, départ tiré) : sans écart, nuits identiques à `main`. `spatial.VERIFICATION` à 1 (toute
  lecture gardée recomparée) sur deux heures de chaque scénario, après chaque changement de la
  perception : sans écart.
- Suite : 1282 tests (18 sautés, comme sur `main`).

Les nombres de recherches reprises de la mémoire du planificateur et de choix ne sont pas comparés :
ce sont des comptes du calcul. Les recherches neuves (PNJ, but, nœuds, issue) le sont, et sont
identiques.

## Étape 0 : mesurer

Profil de `main` (une nuit de 8 h de chaque scénario, graine 7, départ tiré). `cProfile` grossit les
fonctions à appels très nombreux (une nuit y dure 5 à 6 fois plus) ; les parts ci-dessous viennent d'un
échantillonnage (`py-spy`, 250 à 400 relevés par seconde, sans biais d'appel), en part inclusive de la
nuit :

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| choix du but (`choisir`) | 29 % | 57 % | 32 % | 19 % |
| dont recherches neuves (`_explorer`) | 13 % | 45 % | 23 % | 7 % |
| perception (`percevoir`) | 18 % | 16 % | 27 % | 23 % |
| gestes et marche (`agir`) | 26 % | 13 % | 19 % | 28 % |
| ouïe (`retentir`) | 16 % | 6 % | 10 % | 12 % |
| empreinte de l'état (`etat_vue`, propre) | 8 % | 5 % | 8 % | 8 % |

Postes inattendus : au Relais, ce que le joueur saisit des paroles entendues
(`paroles._connu_du_joueur` : le contexte du MJ recomposé puis passé au lexique, 25 ms par appel)
pesait 13 % ; la vue du planificateur construite pour rien par `enrichir` (l'argent), 8 à 11 % de la
mine ; le corps au temps vécu (`vecu.conditions`) relisait deux fois la signature de la vue.

**PyPy** (3.11, v7.3.22, somme de contrôle vérifiée) : le moteur tourne à une ligne près
(`paroles.py:173`, des guillemets imbriqués dans une f-string, syntaxe 3.12 ; réécrite à l'identique
dans une copie pour l'essai). Mêmes nuits (empreintes identiques), mais plus lent : lancés ensemble,
Relais 7,6 → 12,6 s, mine 19,9 → 28,9 s, auberge 15,0 → 25,9 s (× 0,58 à 0,69), et trois fois plus de
mémoire (mine 91 → 266 Mo). PyPy ne change pas la donne ; la branche reste sur CPython (3.14).

## Étape 1 : reprendre le choix entier — mesuré, non retenu

Une sonde a relevé, pour chaque choix d'une nuit, si ses entrées étaient les mêmes qu'au choix
précédent du même PNJ :
- l'esprit brut n'est presque jamais le même (2 à 73 choix sur 2 700 à 5 300) : les besoins avancent
  au temps vécu à chacun de ses tours, et ils sont lus (seuils, prix d'une faute, pression) ;
- avec une clé abstraite (les besoins remplacés par ce qui en est lu : besoins pressants, prix d'une
  faute par motif, caractéristiques modulées ; croyances par leurs valeurs ; renoncements actifs), 1 à
  12 % des choix seulement se reprendraient (mine 38 sur 4 274, Relais 372 sur 3 075), et ce sont les
  moins chers : 0,02 à 0,25 s de `choisir` sur toute une nuit, alors que la clé elle-même coûte autant
  que le choix (1,6 à 4,5 s) ; sans la minute dans la clé, les mêmes chiffres ;
- le résultat, lui, est le même qu'au choix précédent dans 87 % des cas : ce sont les croyances, les
  souvenirs et les prix d'une faute qui changent, pas l'horloge.

Une reprise du choix entier ne gagnerait donc au plus que 1 à 2 % ; elle n'est pas faite. La sonde
(clé et vérification) est décrite dans le plan ; le mode de vérification demandé existe pour ce qui
est fait (ci-dessous). Même constat pour une reprise partielle des recherches neuves : la plupart lisent
toutes les croyances (mine 456 recherches neuves sur 687), et parmi les autres, celles dont les croyances
lues n'ont pas changé ont changé d'ailleurs (auberge : 126 résultats différents sur 127).

## Étape 2 : les postes lourds

Chaque lecture gardée a son contrôle : `spatial.VERIFICATION` la recompare à un calcul de zéro.

1. **Perception incrémentale** (`esprits._percus_depuis`). Dans un état nouveau, ce que perçoit un PNJ
   se tire de sa perception précédente quand :
   - seuls ont changé des objets qui ne bornent pas la vue (ni porte ni objet opaque) ;
   - lui-même n'a pas changé ;
   - son champ est le même.

   On ne revoit alors que les objets changés (différence des deux empreintes `etat_vue`, objet par
   objet), ce qu'ils portent ou contiennent (la chaîne de leurs lieux) et les objets installés sur un
   support, par le même test que le calcul complet (`_vu_dans_le_champ`, sorti de `_percus`). Le reste
   se voit de même, dans l'ordre exact d'un calcul complet. Deux perceptions sur trois passent par là
   (graine 7 : Relais 53 %, mine 62 %, auberge 67 %, crue 58 %), à environ 50 µs au lieu de 140 à
   175 µs. Le mémo d'un état garde son empreinte ; la différence de deux empreintes et les chaînes de
   lieux se calculent une fois par état et se partagent entre PNJ.
2. **Signatures de la vue héritées** (`esprits._heriter_signatures`). Quand aucun objet changé, ni rien
   de ce qu'il porte ou contient, n'est allumé ni opaque, et qu'aucun n'a changé d'ouverture, l'état
   nouveau partage les signatures de chaque salle de l'état précédent.
3. **Lectures de l'état figé.**
   - Le regard d'un acteur (`spatial._vue`) et la lumière de sa case (`esprits.lumiere_ici`) sont
     gardés dans le mémo de l'état.
   - Après un geste, percevoir, témoigner, relever ce que voit le joueur et noter le temps vécu
     (`pnj._avancer`) se font dans un seul état figé ; le relevé des présences aussi. Une nuit de la mine
     calculait 22 978 empreintes pour 1 550 états distincts.
   - Essayé et retiré : `vecu.conditions` en état figé hors de ce bloc. Mesuré en A/B simultané, × 0,96
     à 0,98 : l'empreinte y coûte plus que ce qu'elle fait retrouver.
4. **Pas et passages gardés.**
   - Un pas d'une case dans un sens (`spatial._pas_possibles`) ne dépend que de la géométrie, des
     obstacles solides de chaque salle et des portes ouvertes ou fermées.
   - Les passages de l'ouïe (`ouie._passages`) ne dépendent que de la géométrie, des portes et des
     appuis verticaux.

   Les deux sont gardés sous ces clés, dans la mémoire propre à la géométrie, d'un trajet ou d'un
   bruit à l'autre.
5. **Le planificateur.**
   - `enrichir` juge les bourses crues sans construire la vue (la mine la construisait à presque chaque
     choix pour conclure qu'il n'y avait rien à prendre).
   - La vue juge prendre, consommer et abîmer le bien d'autrui en un seul calcul du propriétaire
     (`biens.leses`).
   - Les tests de but (`a_mange`, `rechauffe`) ne trient plus les faits (`_premier`).
   - `Etat.apres` reprend les faits de l'état quand un geste n'en ajoute aucun.
   - `_suites` ne cherche un fait terminal nouveau que si l'état suivant a plus de faits.
   - Les flammes fixes et celles d'autrui sont lues une fois par état ; le lieu cru vient d'un
     dictionnaire dédié (`Vue._lieu`).
   - L'utilité d'une part n'est jugée que si son donneur se tient là, seul cas où elle sert.
   - La clé de la mémoire est encodée sans contrôle de cycles (même texte, 20 % plus vite).
6. **Ce que le joueur saisit des paroles.**
   - Le lexique ne cherche pas le motif d'un terme absent du texte, et fait une seule passe (`subn`).
   - Ce que nomme le contexte du joueur n'est calculé qu'une fois par bloc de lecture
     (`paroles.contexte_fige`, autour d'`ecoute.lier` et d'`ecoute.rendre`).
7. **Menus.**
   - `esprits.esprit` ne complète ses champs que s'il en manque un.
   - `Monde.objets` et `Monde.joueur` sont des attributs, remis à jour à chaque affectation de `data`
     (`Monde.__setattr__`), au lieu de propriétés lues des millions de fois.
   - Les imports de quelques fonctions très appelées se font au chargement du module.

Pas de code compilé : la géométrie de la perception ne domine plus (la perception incrémentale et
les lectures gardées y suffisent).

## Mesures

Temps d'une nuit de 8 h au processeur (`process_time`), moyenne par nuit, `main` 06602a6 → branche,
lancés ensemble (2 processus de chaque côté, 4 au plus ; une autre session faisait tourner ses bancs
sur la même machine). Départ tiré : 4 graines, 2 passes. Départ fixe : 1 passe. Entre parenthèses, la
somme des durées des recherches du planificateur (`--diagnostic`).

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| départ tiré | 8,9 → 6,4 s (2,4 → 2,2) | 23,7 → 18,8 s (13,1 → 10,9) | 16,2 → 12,6 s (4,9 → 4,0) | 7,7 → 5,8 s (1,4 → 1,2) |
| départ fixe | 6,8 → 4,6 s (1,4 → 1,1) | 23,6 → 19,6 s (14,3 → 12,4) | 15,9 → 12,6 s (4,8 → 4,2) | 8,9 → 6,9 s (1,6 → 1,5) |
| rapport (tiré) | × 1,39 | × 1,26 | × 1,29 | × 1,33 |
| rapport (fixe) | × 1,49 | × 1,20 | × 1,27 | × 1,28 |

Les deux passes en départ tiré : Relais × 1,36 puis × 1,42, mine × 1,25 puis × 1,28, auberge × 1,27
puis × 1,32, crue × 1,38 puis × 1,29. Les valeurs absolues dépendent de la charge ; les rapports restent.

Pic de mémoire d'un processus (une nuit) : Relais 43 → 42 Mo, mine 91 → 83 Mo, auberge 85 → 77 Mo,
crue 46 → 47 Mo. Les tables gardées sont bornées : 16 tables de pas et 16 relevés de passages par
géométrie ; une dernière perception et son mémo par PNJ.

Choix repris : aucun (étape 1 non retenue). Perceptions tirées de la précédente : deux sur trois
(ci-dessus).

## Limites

- La mine reste dominée par les recherches neuves : Rémy, Josse et Mathe refont chaque minute des
  recherches épuisées ; une recherche neuve coûte à peu près ce qu'elle coûtait par état développé. Les
  écarter sans chercher demanderait d'énumérer à la main ce qui peut atteindre chaque but : fragile, et
  non tenté.
- Un PNJ qui bouge ou se tourne revoit toute sa perception (un tiers des perceptions).
- L'empreinte de l'état (`etat_vue`) se calcule encore à chaque lecture hors d'un état figé : 5 à 8 %
  d'une nuit. Des centaines de points du moteur écrivent dans les objets ; rien ne dit, à moindre coût
  qu'elle, que l'état n'a pas changé.
- L'ouïe (`retentir`) relit la perception de chaque auditeur. Je n'ai pas tiré parti du fait que seule
  l'orientation d'un auditeur change d'un auditeur à l'autre : les rotations temporaires
  (`voix._verrait_en_se_tournant`) le rendent délicat, pour 1 à 2 % au mieux.
- La clé de la mémoire du planificateur (`_entrees`) reste un texte JSON complet. Une égalité de
  structures Python serait plus grossière (`True == 1`, ordre des clés), alors que des croyances se
  testent par identité.
- Toute lecture nouvelle de la perception doit rester couverte par `spatial.etat_vue`, comme avant. Une
  lecture qui dépendrait d'un autre objet que ceux de la chaîne de ses lieux ou de son support devrait
  aussi entrer dans `_percus_depuis`. `VERIFICATION` le signalerait dans les tests.
- PyPy n'a pas été essayé sur la suite de tests, seulement sur le banc : il ne valait pas d'aller plus
  loin.

## Fusion

À fusionner après l'appel négocié et les branches Codex qui touchent `deliberation` et
`planification`. Points à revoir à la fusion :
- `planification` : `Vue.__init__` (jugement du bien d'autrui par `biens.leses`), `Vue.lieu`/`salle`/
  `_lieu`, `flammes_fixes`/`flammes_d_autrui` (lues une fois par état : elles ne doivent dépendre que
  de l'état du plan et de la vue), `_parts` (l'utilité d'une part jugée seulement si le donneur est là),
  `_suites`, `a_mange`/`rechauffe`, `Etat.apres`, `enrichir` ;
- `esprits` : `percus`, `_percus`, `_percus_depuis` (toute lecture nouvelle de la perception doit
  rester couverte par `spatial.etat_vue`, comme avant) ;
- `pnj._avancer` : le bloc figé autour de la perception, des témoins, des présences et de `noter` ;
- refaire sur le `main` final : `tools/empreintes_nuits.py jouer` des deux côtés puis `comparer`
  (32 nuits), et `VERIFIER` et `spatial.VERIFICATION` sur une nuit de chaque scénario.
