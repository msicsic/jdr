# Lot 374 — position crue comme hypothèse datée

30 octobre 2026, PC fixe. Branche `codex-position-hypothese`, départ `b83f5a59`
(descendant d'`integration 60f857c5`), non fusionnée. Bruts :
`C:/Users/msics/donjon/artifacts/position-hypothese-374/`.

**Invariant.** Une localisation ancienne d'une autre personne reste un indice,
sans être une présence acquise. `esprits.confiance_position` calcule
`confiance_initiale × 2 ** (-âge / demi_vie)` depuis l'observation d'origine,
sans écriture par tick. `data.positions_hypotheses` sauvegarde le seuil **0,5**
et les demi-vies **15 / 60 / 120 minutes** : mobile, posée, retenue.
La classe vient des seules croyances de l'observateur : repos assis observé,
intention lue de garde/guet, entrave ou inconscience constatée, issues crues
verrouillées. Aucune lecture du déplacement réel hors perception. Les anciens
faits sans classe utilisent « mobile » ; soi, les objets et les feux ne vieillissent pas.

**Contrat commun.** `_lieu_cru` ne fournit plus une position expirée comme certaine ;
`_chercher` conserve son dernier lieu comme première piste, hors des lieux déjà
cherchés en vain. Inspection, appel et question utilisent les mécanismes existants ;
le préfixe incertain coupe l'exécution avant son suffixe. Le seuil calculé et la règle
figurent dans `_entrees`, y compris dans les devis observateurs. `pnj._agir` revalide
les anciens plans sauvegardés ; `croit_present` lit la même hypothèse.
Un geste sans témoin vérifie les témoins incertains, une embuscade sa cible.
Les vérifications suivent un ordre stable plutôt que leurs permutations.
Un préfixe de recherche ne peut pas devenir un terminal de devis de part.
Le ouï-dire de localisation conserve l'origine, la mobilité et une confiance initiale
au plus égale à celle du témoin : un relais ne rajeunit pas l'observation.

**Cas réels et contrôles.** Capture du lot 371, auberge 7, minute **240** :
Mathurine situe Lucien au couloir depuis une voix à **174**, alors qu'il est
au grenier. Le recours demande une inspection, pas une présence supposée.
Autre cas : capture du lot 69, mine 7 à **470**, Bram situe Rémy au baraquement,
alors qu'il est à l'entrée. Dans les deux scènes, la position cachée modifiée ne
change pas le plan. Les variantes parti/resté exécutent l'inspection avec le moteur,
puis contrôlent croyances, échec retenu, monde, rendu et scène après sauvegarde/recharge.
Laps entier/découpé traversant le seuil, nouvelle voix, source datée relayée,
repos observé, règle sauvegardée et discrétion sont également couverts.
**8 nouveaux tests verts**, 4,118 s (`tests-nouveaux.json`) ; le voisin de protection
conserve ses **quinze coups** d'archive, sans changer ses assertions.
La première passe de 89 tests a révélé les défauts de terminal et de posture du
joueur corrigés ensuite ; la reprise finale est **verte : 13 fichiers / 89 tests,
416,677 s**, zéro échec, erreur ou saut (`tests-finaux.json`).

**Mesures encore en cours.** Le premier lanceur a échoué avant les nuits de branche :
le `main` local `c870c8b4` ne fournit pas `agendas.enfants`, requis par l'audit actuel
(`banc.stderr.txt`, `fin-calculs.json`). Aucun défaut du jeu n'est établi par cet arrêt.
Reprise sans relancer les tests : `planification.VERIFIER`, Relais 7, 1 h ; puis
4 h × quatre graines × Relais/auberge/mine/crue, contre `origin/main` (`0bad2272`)
et contre la base exacte `b83f5a59`. Cache conservé, mêmes nuits de branche réutilisées,
deux travailleurs à priorité réduite. `tools/mesurer_position_374.py` produit les deux
comparaisons et leurs relevés d'appels/retours. Ni suite complète ni Luna.
Nouvelle fin écrite en dernier :
`C:/Users/msics/donjon/artifacts/position-hypothese-374/fin-reprise.json`.

**Limites et reprise.** Les demi-vies sont un réglage initial, sans calibration empirique.
L'absence de boucle nouvelle et l'attribution des changements de nuit restent à valider
sur les bruts : **ne pas considérer le lot validé pour fusion avant cette lecture**.
Pour S0/373 : pas de nouveau registre ; `croyances[sujet].lieu` conserve ses champs
actuels et ajoute `mobilite` (`mobile`, `pose`, `retenu`), coefficient initial en
`confiance`, origine des relais inchangée ; les lecteurs utilisent la confiance dérivée.
Recouvrement **372** : `esprits.py` (admission/perception/validation) ; prévoir une
revue de fusion. Pas de fichier de code commun attendu avec 365/369/370 ;
`echanges.py` change uniquement la transmission du renseignement daté.
