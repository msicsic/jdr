# Tâche Codex 250 : reprise du lot 235 — une nouvelle est utile si l'on sait que l'auditeur se sert de ce moyen

Le lot 235 (branche `codex-sait-observations-c`, `942a3c2`, base `adb52c4`, non fusionnée) retire la lecture du savoir
réel de l'auditeur dans `social.bavarder` (`_sait`) et ne fait dire que ce que le locuteur croit nouveau **et** utile à
l'auditeur (`social._utile`). Le diagnostic 249 (`docs/taches/rapport-codex-249-confidences-perdues.md`, fusionné ;
bruts `C:\Users\msics\donjon\artifacts\confidences-249\`) établit :
- presque toutes les confidences perdues à la mine et au Relais n'avaient aucun usage décisionnel : leur perte est
  légitime ;
- **une perte utile démontrée** : Josse → Mathe, mine 1985 à 141, biscuits épuisés ; sans cette nouvelle, Mathe ne
  peut plus éviter, à 191–193, de demander ces biscuits pour nourrir Rémy. `_utile` est faux faute de lien entre Mathe
  et ce moyen : **il manque l'usage d'un moyen pour aider un tiers, hors engagement actif** ;
- les huit assertions rouges du 235 sont des attentes périmées (classement au rapport 249), à conserver dans des
  scènes aux prémisses explicites, jamais affaiblies.

Décision de l'utilisateur (2026-10-28) : reprise ciblée.

## L'invariant
**Un moyen concerne l'auditeur s'il fait partie des usages que le locuteur sait que l'auditeur fournit ou recherche,
pour lui-même ou pour autrui ; cette preuve d'usage est retenue par le contrat commun de perception et de parole
(geste vu, parole entendue, service rendu ou demandé), vaut pour ce moyen, ses moyens équivalents et leurs supports
crus, et tombe à son démenti.** Le locuteur ne lit ni la faim future, ni le plan, ni le savoir privé de l'auditeur ; pas
d'analyse de formulation, pas de cas « nourriture », aucun acteur ni scénario particulier.

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le laptop** (l'utilisateur y travaille) : au plus 2 processus,
priorité réduite.

## Base et périmètre
- Reprends la branche `codex-sait-observations-c` et fusionne-y `origin/integration` (sans rebase) ; le travail du 235
  reste, la preuve d'usage s'y ajoute.
- **Fichiers autorisés d'avance** : `social.py` (`_utile`, `bavarder`), l'enregistrement de la preuve d'usage dans la
  voie commune de perception/parole (`esprits.py`, `social.py`, `echanges.py` en raccord pour les services rendus ou
  demandés), sa validation de sauvegarde ; les huit tests rouges du 235 et les fichiers de tests voisins dont une
  attente de trajectoire change, **arbitrage autorisé avec preuve** (prémisse explicite, aucune assertion affaiblie).
  **Pas** : `planification.py`, `deliberation.py`, le MJ, les scénarios.
- Le défaut d'admission du service de Mireille (auberge 2024, 226) n'est pas de ce lot.

## Vérification
- Cas réel : capture mine 1985 à 141 (bruts 249) : Josse dit l'épuisement des biscuits à Mathe, Mathe ne prévoit plus de
  les demander à 191–193 ; un autre cas de même nature (autre moyen, autre scénario, aide à un tiers vue ou entendue).
  Monde et rendu identiques après rechargement, même laps d'un bloc ou découpé. Une nouvelle sans preuve d'usage reste
  tue.
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache (`origin/integration` à ta base), compteur 219 :
  lancé détaché. Rapporter confidences par scénario (référence → 235 → 250), S/F/D, suspects sans hausse.
- Pas de suite complète.

## Livraison
- Branche `codex-sait-observations-c` poussée. Rapport d'une page `docs/taches/rapport-codex-250-preuve-usage.md` ;
  entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\usage-250\`.
  Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
