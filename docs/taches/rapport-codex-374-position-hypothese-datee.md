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
Une inspection engagée reste tenue sous le même motif, but et demande, tant que sa
piste tient : une nouvelle localisation, un échec ou une fin connue libèrent le préfixe.
La recomposition du parent ne remet plus ses préparatifs devant cette inspection.
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

**Première mesure analysée (`6614e692`).** `planification.VERIFIER` vert, Relais 7,
1 h, **37,982 s**. **16 nuits × 4 h**, quatre graines, Relais/auberge/mine/crue :
zéro plantage et usurpation. Comparaisons contre `origin/main` (`0bad2272`) puis la
base exacte `b83f5a59` ; mêmes nuits de branche relues du cache, jamais rejouées.
La référence locale `main c870c8b4` était incompatible avec l'audit (`agendas.enfants`),
trace conservée, pas de nouvelle tentative sur cette référence.
Contre la base, appels totaux **6→5 / 13→45 / 9→29 / 35→36** ; deux retours suspects
nouveaux (Lucien mine 1985, Brune crue 2024), non certifiés par les seuls relevés.
La lecture révèle surtout une régression **crue 42 : 112 passages d'Aubin en une heure**.
De 18 à 33, chaque recomposition réinsère un aller à la réserve avant l'inspection
d'Ilse : `diagnostic-crue-42.json` et capture `crue-42-18.json.gz`.
Correction commune dans `verification_en_cours` et `deliberation.choisir` : le
préfixe incertain progresse jusqu'au constat, sous réserve de la revalidation du
parent, des refus et des urgences. La capture corrigée retrouve Ilse par la vue à
**19**, **8 passages en six minutes**, monde/rendu et textes identiques en bloc/découpé.
**20 ciblés verts**, 16,830 s ; passe finale **13 fichiers / 90 tests** en cours,
puis nouveau banc et VERIFIER sur la correction, références existantes en cache.
Résultats dans `apres-progres/` ; fin écrite en dernier :
`C:/Users/msics/donjon/artifacts/position-hypothese-374/fin-contact.json`.

**Limites et reprise.** Les demi-vies sont un réglage initial, sans calibration empirique.
L'absence de boucle nouvelle reste à valider sur la mesure après correction :
**ne pas considérer le lot validé pour fusion avant cette lecture**. Ni suite complète ni Luna.
Pour S0/373 : pas de nouveau registre ; `croyances[sujet].lieu` conserve ses champs
actuels et ajoute `mobilite` (`mobile`, `pose`, `retenu`), coefficient initial en
`confiance`, origine des relais inchangée ; les lecteurs utilisent la confiance dérivée.
Recouvrement **372** : `esprits.py` (admission/perception/validation) ; prévoir une
revue de fusion. Pas de fichier de code commun attendu avec 365/369/370 ;
`echanges.py` change uniquement la transmission du renseignement daté.
