# Tâche Codex 255 : une observation faite ensemble ne se redit pas

Dernier lot du chantier 206 → 235 → 250 (décision de l'utilisateur du 2026-10-28 : s'il ne suffit pas, le chantier est
mis de côté). Branche `codex-sait-observations-c` (lot 250, `9371144`, non fusionnée) : `social.bavarder` ne lit plus le
savoir réel de l'auditeur ; `_utile` suit la preuve d'usage d'un moyen. Rapport : `docs/taches/rapport-codex-250-preuve-usage.md`
sur cette branche ; bruts `C:\Users\msics\donjon\artifacts\usage-250\`.

Le lot 250 retrouve les confidences (Relais 26, mine 54, hameau S 22,75 → 43,75) mais **n'est pas fusionnable** :
- **avertissements redits 0 → 46** (hameau 1985 surtout), confidences du hameau 58 → 122 ;
- **suspects 219 4 → 8** : cinq nouveaux (mine 1985 Lucien et deux Mathe, hameau 1985/2024 Aubin) ;
- à expliquer 51 → 83.

Cause supposée, connue depuis le rapport 206 : **une observation de l'environnement partagé, faite ensemble, est déjà
commune** (une eau vue ensemble, une lumière éteinte sous les yeux des deux) ; l'ancienne lecture de `_sait` masquait ce
manque.

## L'invariant
**Le locuteur tient pour connu de l'auditeur un état qu'il croit que l'auditeur a perçu en même temps que lui : même
lieu et même instant, perception possible pour l'auditeur selon ce que le locuteur en croit (lumière, regard, présence
attestée), ou parole déjà échangée sur cet état. Il ne le redit pas tant que cet état ne change pas.** Aucune lecture de
l'esprit réel de l'auditeur, aucune exception par sorte de nouvelle, scénario ou personnage. Le registre des faits dits
(lots 64/108) reste la seule voie pour ce qui a été dit ; la co-perception s'ajoute comme preuve de connaissance commune.

Vérifie d'abord, sur les bruts, que les 46 redites et les cinq suspects viennent bien de là ; s'ils viennent d'ailleurs,
dis-le et traite la cause commune réelle dans le même esprit (une cause par règle).

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le laptop** (l'utilisateur y travaille), au plus 2 processus,
priorité réduite.

## Base et périmètre
- Travaille sur `codex-sait-observations-c` ; fusionne-y d'abord `origin/integration` (sans rebase ; conflits de
  documentation à réunir ; `social.py` a reçu `recevoir_statuts` par le lot 254, à garder).
- **Fichiers autorisés d'avance** : `social.py`, la preuve de co-perception dans la voie commune de perception
  (`esprits.py`), la validation de sauvegarde ; les tests du chantier et leurs voisins, **arbitrage avec preuve**.
  **Pas** : `planification.py`, `deliberation.py`, `pnj.py`, le MJ, les scénarios.

## Vérification
- Cas réels : une redite du hameau 1985 et un suspect (Aubin) des bruts 250, capturés et rejoués : plus de redite, mêmes
  confidences utiles ; un autre cas de même nature (autre scénario, autre état partagé) ; une observation **non**
  partagée (auditeur absent, dans le noir ou de dos) reste dite. Monde et rendu identiques après rechargement, même laps
  d'un bloc ou découpé.
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache (ta base `integration`), compteur 219 : lancé
  détaché. Critère de fusion : **suspects sans hausse par nuit contre la référence, avertissements redits revenus au
  niveau de la référence**, confidences et S/F/D rapportés (référence → 250 → 255).
- Pas de suite complète.

## Livraison
- Branche `codex-sait-observations-c` poussée. Rapport d'une page `docs/taches/rapport-codex-255-observation-partagee.md` ;
  entrée dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\partagee-255\`. Termine par
  `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
