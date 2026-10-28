# Tâche Codex 235 : reprise du lot 206, dire ce qui est nouveau et utile pour l'auditeur

Le lot 206 b (branche `codex-sait-observations`, dernière livraison `0ba27d3`, rapport
`docs/taches/rapport-codex-206-sait-observations.md` sur cette branche) fait décider `social._auditeur` avec les seules
croyances du locuteur, sans lire le savoir réel de l'auditeur. C'est juste, mais trop restrictif : confidences
Relais/mine/auberge/crue/hameau **27/104/48/49/92 → 6/12/6/6/27** sur 20 paires de 4 h, avertissements redits 6 → 0 ;
**13 échecs et une erreur** introduits dans la suite ; suspects 4 → 5 ; deux boucles nouvelles (Mireille/Mathurine
auberge 2024, agenda de Brune hameau 2024).

**Décision de l'utilisateur (2026-10-28) : reprendre.** Garder la règle (le locuteur ne lit jamais l'esprit de
l'auditeur), mais rétablir les confidences utiles : ce que le locuteur croit **nouveau ET pertinent** pour l'auditeur.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste : le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. D'autres lots
calculent sur ce poste : au plus 2 processus, priorité réduite.

**Départ** : branche `codex-sait-observations-c` depuis `integration` ; fusionne `origin/codex-sait-observations`
(`0ba27d3`). Depuis sa base sont entrés notamment 226, 230 (rendez-vous tenus : la boucle Mireille/Mathurine est
peut-être déjà résolue, à vérifier) et 218. **Fichiers** : `social.py` (`_auditeur`, `_nouveau`, `bavarder`, `_a_dire`),
les fonctions d'esprits déjà ouvertes par 206 pour les observations communes, et leurs tests. **Pas** : `ouie.py`,
`echanges.tenu` (lot 233), `biens.py` (lot 232), `signes.py` et `pnj.agir` (lot 234), `deliberation.py`, le MJ.

**Bruts dans `C:\Users\msics\donjon\artifacts\sait-235\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

## Ce qu'on te demande
1. Classer les confidences perdues (mine surtout, 104 → 12) : celles qui étaient des redites (à garder perdues) et celles
   qui étaient nouvelles pour l'auditeur selon le locuteur et touchaient un de ses besoins, biens, charges, agendas ou un
   danger qui le concerne (à rétablir). Un tableau court par sorte.
2. **Invariant** : le locuteur dit un fait s'il croit que l'auditeur ne l'a ni vu, ni entendu, ni appris de lui, et si ce
   fait touche, selon ses propres croyances, ce que l'auditeur a, veut, garde ou risque. Une observation de
   l'environnement partagé, faite ensemble et sue telle, est commune. Une confirmation ou un détail sans conséquence
   nouvelle (centimètre d'eau de plus) n'est pas une nouvelle. Aucun lexique, aucune règle propre à un scénario.
3. Les treize échecs et l'erreur : chacun classé (défaut corrigé par l'invariant, prémisse de scène à expliciter avec
   preuve, ou préexistant reproduit sur l'intégration). **Aucune assertion affaiblie sans preuve**, aucune capture
   réancrée sans la dire.

## Vérification
- Tests après rechargement : un cas réel d'une confidence utile rétablie, un autre de même nature, une redite toujours
  tue, même laps d'un bloc ou découpé, monde et rendu rechargés.
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache, compteur 219 et S/F/D : confidences entre le
  niveau 206 b et la référence, avertissements redits sans hausse, suspects sans hausse, pas de boucle nouvelle. Dire les
  chiffres tels qu'ils sont.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
- Branche `codex-sait-observations-c` poussée (pas `main`). Si la poussée est bloquée par la revue, laisse le commit local
  et dis-le.
- `docs/etat-dev.md` : « Branche `codex-sait-observations-c`, non fusionnée ».
- Rapport d'une page `docs/taches/rapport-codex-235-sait-observations-c.md`.
