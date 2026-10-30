# Tâche Codex 374 : la position crue d'une personne est une hypothèse datée

Lot à part du [plan de l'esprit social](../plan-esprit-social.md) (§ 4.1, § 10, décision 9 du § 13 : « le vieillissement
des faits qui changent, d'abord la position crue des personnes, qui doit devenir une hypothèse datée à vérifier avant
d'agir, est un petit lot à part »). Aujourd'hui une croyance de position ne vieillit pas : une personne vue il y a trois
heures est encore crue là, et le planificateur la tient pour vraie.

Lis `AGENTS.md`, `docs/etat-dev.md` (court), le plan (§ 2.1, 4.1, 10) et, par mot-clé dans `docs/historique-lots.md`
(sans le lire en entier), les lots qui ont fait la localisation crue (211, 221 « où est-il », 226 contact sous but, 313
contact de position inconnue, 37/69 recherche et indices).

## Invariant (un seul)
**La position crue d'une personne (autre que soi) est une hypothèse datée : sa confiance décroît avec l'âge de
l'observation selon une règle commune (plus vite pour qui bouge, plus lentement pour qui est cru assis, gardant un poste
ou enfermé, d'après les seules croyances de l'observateur) ; au-delà d'un seuil, un plan qui a besoin de la trouver ou
d'éviter qu'elle le voie la vérifie d'abord par les moyens existants (aller voir, appeler, demander où elle est) au lieu
d'agir comme si elle était là.** Aucune lecture de la position réelle ; une observation nouvelle (vue, voix reconnue,
ouï-dire daté) refait l'hypothèse ; même laps découpé, même monde ; la règle est dans `data` et dans les entrées de la
recherche (`planification._entrees`). Les objets et les feux ne sont pas dans ce lot.

## Vérification
- Cas réel : un PNJ qui agit sur une position vue longtemps avant (chercher dans les bruts des bancs récents, ou la
  capture d'auberge du lot 371) ; un autre cas de même nature dans un autre scénario ; la personne effectivement partie
  et effectivement restée ; monde, croyances et rendu après recharge.
- Tests ciblés et voisins (localisation, recherche, contact, protection, témoins). Banc rapide 4 h, quatre graines,
  Relais, auberge, mine, crue (`tools/comparer_bancs.py --reference main`, cache) : changements de comportement expliqués,
  aucune boucle nouvelle (appels ou allers-retours de vérification) ; `planification.VERIFIER` sur une nuit courte.
  Pas de suite complète, ni Luna.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/esprits.py` (croyance de position), `donjon/planification.py`
(entrées, vérification avant d'agir), `donjon/deliberation.py` si le choix doit lire l'hypothèse. Le lot 373 (S0,
conception de la mémoire, documentation seule) inventorie aussi cette croyance : signale-lui la forme retenue dans ton
rapport. Lots en cours : 365, 369, 370, 372 ; signale tout recouvrement. Deux processus au plus, priorité réduite,
calculs longs détachés.

## Livraison
- Branche `codex-position-hypothese`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-374-position-hypothese-datee.md` ; entrée « non fusionnée » de 8 lignes
  au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\position-hypothese-374\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
