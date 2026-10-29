# Tâche Codex 275 : faire venir celui à qui l'on veut demander, quand on ne peut pas aller jusqu'à lui

Le diagnostic 262 (`docs/taches/rapport-codex-262-ilse-demande.md`, fusionné ; captures rechargeables
`C:\Users\msics\donjon\artifacts\ilse-261\snapshot_270.json`, `snapshot_400.json`, `snapshot_600.json`) établit que, dans
la crue (graine 7), Ilse affamée en `chambre_cloche` ne demande jamais une part à Gorm : elle le croit en `antichambre`,
salle connue mais inaccessible pour elle (porte crue verrouillée, ni clé ni crochetage). `planification._parts_calculer`
n'offre `demander` que si le donneur est co-présent, et `_chercher` seulement si son lieu est inconnu. Le jeu possède
pourtant l'appel négocié (`donjon/appel.py`, lots « appel négocié » et 230) : héler, « Qu'est-ce que tu veux ? »,
« J'arrive ! », rendez-vous tenu.

## L'invariant
**Quand une étape sociale (demander, acheter, proposer) exige la présence d'un interlocuteur cru dans un lieu connu
mais inaccessible à l'acteur, et que l'acteur le croit à portée de voix, l'appeler pour qu'il vienne est un moyen de
cette étape, par l'appel négocié commun.** L'appelé décide seul de venir (ses propres priorités, méfiance, chemin cru,
lot 230) ; aucune venue n'est supposée ni aucun accord présumé. L'appel vain est retenu comme les autres (recherches,
lots 37 et 69) : pas de rappel par simple délai. Même règle que le joueur qui hèle. Aucune exception par personnage,
lieu, scénario ou objet ; aucune lecture de la position réelle de l'appelé.

Lot de 30 à 45 minutes. Pas de Luna, pas de suite complète (le superviseur la lance). **Poste : le laptop**, deux
processus au plus, priorité réduite.

**Fichiers attendus** : `donjon/planification.py` (`_parts_calculer`, `_chercher` ou un raccord commun des étapes sociales
à distance), `donjon/appel.py` en raccord si nécessaire. Ne touche pas `agendas.py`, `signes.py`. `deliberation.py`
seulement en raccord minimal (lots 266 et 273 non fusionnés y travaillent) ; dis-le dans le rapport si tu y touches.

## Vérification
- Capture réelle crue 7 à 270 (Ilse, Gorm) rechargée : Ilse hèle, Gorm répond selon ses priorités ; s'il vient, la demande
  a lieu après l'arrivée ; s'il refuse ou ne vient pas, l'appel est retenu sans rappel par délai. Un autre cas de même
  nature (autre scénario ou autre étape : achat, proposition). Contre-épreuves : interlocuteur hors de portée de voix
  (aucun appel), lieu inconnu (le chemin existant `_chercher` reste seul), appel vain retenu. Monde, rendu et scène
  identiques après recharge et laps entier/découpé.
- **Tous les fichiers de tests qui exercent `planification._parts_calculer`, `_chercher` et `appel`** (trouve-les par
  recherche des appelants) ; pas de suite complète.
- Banc rapide 4 h, cinq scénarios (`relais`, `mine`, `auberge`, `crue`, `crue_hameau`) × quatre graines, référence de
  l'intégration à ta base (en cache si présente, sinon calculée une fois), sonde actuelle (lots 265/271) : suspects 219
  par nuit sans hausse, appels et retrouvailles, richesse S/F/D (fonction `cats` du lot 183). Calcul long détaché.

## Livraison
- Branche `codex-appeler-donneur` poussée (sinon commit local, et dis-le). Rapport d'une page
  `docs/taches/rapport-codex-275-appeler-donneur.md` ; entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans
  `C:\Users\msics\donjon\artifacts\appeler-275\`. Termine par `LOT TERMINÉ` (résumé d'une ligne),
  `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
