# Tâche Codex 230 : qui dit « Ici, viens ! » attend celui qui vient

La suite complète de l'intégration `881db69` échoue depuis le lot 221 (bissection,
`C:\Users\msics\donjon\artifacts\integ-225\suite.log`) sur ce test :
`tests.test_constater_rumeurs.ChercherQuelquUnTests.test_le_joueur_qui_ne_les_connait_pas_n_entend_que_des_voix`.

Le joueur y entend une troisième voix : `entendus` contient `mathurine`. Le relevé de l'orchestrateur sur
l'intégration montre un défaut de contrat ; 221 n'a fait que le révéler en changeant les trajets de Mireille :
- Mathurine (pèlerine, auberge) hèle quelqu'un dont elle ignore le nom (« quelqu'un ? », `social._qui`).
- Mireille répond « Ici, viens ! » : elle reste et attend. Mathurine répond « J'arrive ! ».
- Mireille repart aussitôt à ses affaires : Grenier → Couloir → Salle commune → Cuisine → Cellier.
- Mathurine rappelle. On compte **cinq cycles appel / « Ici, viens ! » / « J'arrive ! » en quelques minutes**,
  avant « Mireille retrouve Mathurine, comme convenu ».
- Mathurine ne reçoit plus les vivres qu'elle obtenait sur `bd45f65`.

Contrat du lot 60 et de l'appel négocié (`docs/plan-ouie.md`, « L'appel négocié ») :
- on dit « Ici, viens ! » quand on ne peut pas ou ne veut pas bouger ;
- qui l'a dit attend l'arrivée de l'autre, sauf urgence (palier supérieur) ;
- une attente rompue se dit ou se retient.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste : le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres
lots calculent sur ce poste (195, 228) : au plus 2 processus, priorité réduite.

**Fichiers** : `appel.py`, `deliberation._attendre_qui_vient`, `attendre_l_appelant`, le choix de la réponse
(« Ici, viens ! » ou « J'arrive ! ») et leurs tests. **Pas** :
- les fonctions de renoncement du lot 225 (lot 229) ;
- `planification.py` (lot 218) ;
- `biens.py`, `echanges.py`, `pnj_propositions.py` (lot 228) ;
- `ouie.py` (lot 195) ;
- le MJ.

**Bruts dans `C:\Users\msics\donjon\artifacts\rendez-vous-230\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

Lis `AGENTS.md`, puis les rapports :
- 60 (rendez-vous) ;
- 221 ;
- 226 (contact comme sous-but, fusionné sur l'intégration : appeler et rejoindre sous le but parent).

Lis ensuite `appel.py` et les deux fonctions d'attente.

## L'invariant
**Une réponse à un appel engage selon ce qu'elle dit :**
- **Qui répond « Ici, viens ! »** ne le dit que s'il compte rester. Il reste jusqu'à l'arrivée, jusqu'à l'échéance
  réglée sur la distance, ou jusqu'à un palier strictement supérieur.
- **S'il part quand même**, le rendez-vous est clos et l'appelant le sait : il ne le croit plus là.
- **Qui a promis « J'arrive ! »** va au lieu convenu sans rappeler tant que le rendez-vous tient. Il ne rappelle
  qu'après l'avoir trouvé vide.

Même règle pour le joueur et pour tout PNJ ; aucune règle propre à Mireille, Mathurine ou l'auberge.

## Vérification
- Reproduire d'abord la scène du test (`mireille_cherche_odile`, joueur au grenier) sur l'intégration ; compter les
  appels et les réponses. Dire si le défaut existe déjà sur `bd45f65` dans une autre scène.
- Tests après rechargement :
  - la scène réelle : au plus un cycle d'appel tant que le rendez-vous tient ;
  - un autre cas de même nature (autre scénario, autre paire) ;
  - un départ urgent qui clôt le rendez-vous ;
  - le même laps d'un bloc ou découpé ;
  - monde et rendu rechargés identiques.
- Le test historique retrouve son intention : le joueur n'apprend aucun nom. Sa liste exacte d'`entendus` ne s'adapte
  que si la troisième voix est légitime, preuve à l'appui.
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache, avec le compteur 219 et les
  appels, réponses et retrouvailles : aucune usurpation, aucun plantage, aucune boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
- Branche `codex-rendez-vous-tenu` poussée (pas `main`). Si la poussée est bloquée par la revue, laisse le commit local
  et dis-le.
- `docs/etat-dev.md` : « Branche `codex-rendez-vous-tenu`, non fusionnée ».
- Rapport d'une page `docs/taches/rapport-codex-230-rendez-vous-tenu.md`.
