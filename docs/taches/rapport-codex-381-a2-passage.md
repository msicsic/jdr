# Lot 381 — A2, passage

31 octobre 2026 — branche `codex-a2-passage`, base de travail `origin/integration`
au brief `c63dd5637648523997cc7a3f32966fd63fec6b06`, non fusionnée.

**Invariant.** `donjon/contrats_passage.py` décrit le passage local dessous/dessus,
l'assemblage installé, l'appui mobile, la poussée et la demande de passage.
Les compilateurs, les schémas d'interprétation et de suite après admission de
faits, les raccourcis et « Compris » réemploient ce contrat. Une méthode légale
pour une autre opération ne remplace plus le côté, l'appui ou le destinataire.
Les références non vides restent vérifiées dans le monde par les mécaniques.

**Changement.** Le schéma corrèle opération, champs neutres, références et
méthodes. Le refus nomme champ, valeur reçue et valeurs acceptées ; la
canonisation existante du support redondant reste admise. Le plan dit qui
se déplace et quel accès est utilisé. Gabarit, équipement, réception, durées,
jets, accord, prix et conséquences sociales ne changent pas. Un prix non
numérique ou un sujet extérieur aux destinataires reçoit un refus de forme
au lieu d'une offre nulle ou d'un acte ignoré.

**Preuves.** `relais/20` (poutre) et table de l'auberge : compilation simulée,
vraie boucle console/PontWeb, faisabilité sans action puis exécution, état et
« Compris » sauvés avant affichage et relus après recharge. Dessous/dessus puis
deux minutes en bloc ou huit tranches de quinze secondes avec recharge : monde
complet et vues identiques. Raccourcis/étapes explicites, appui mobile/assemblage,
demande/poussée à Brune puis Ilse, simples propos sans passage, champs voisins
refusés sans mutation et schéma émis sont vérifiés. Le test du sujet tiers attend
désormais le refus explicite et conserve l'absence de déplacement, renforcée
par l'identité du monde entier. Le test sonore filtre ses propres branches.
Le nouveau test de poussée vérifie le recul enregistré, le récit sauvegardé et
les vues rechargées : son attente initiale de seuil encore libre était fausse.
Les réactions peuvent ramener la victime pendant les 3 s, comme le couvre déjà
le test historique. Aucun code du jeu n'a changé depuis `0e3be7f5`.

**Mesures.** Passe de onze fichiers : **138 tests, 1 644,00 s, deux échecs,
aucune erreur ni test ignoré** (`tests-finaux.json`). Les quinze parcours
corps/passage au terminal sont verts ; ils ne sont pas relancés. Après correction
du seul test décrit ci-dessus, **47/47 tests verts en 73,30 s**, dont les huit
nouveaux tests et les trois fichiers voisins de parole (`tests-sociaux.json`).
L'autre échec, `test_cas_reel_acceptee_elle_s_ecarte_vraiment`, attend « Tu avances
d'un pas. » ; **le même échec et le même texte réel sont reproduits sur la base
exacte `c63dd563`** (un test, 4,33 s, `test-base.log`). Son assertion reste intacte :
les voisins ne sont donc pas tous verts. Aucune nouvelle régression connue.
**Empreintes identiques** sur huit nuits de 2 h par version, Relais/auberge,
1985/7/42/2024 : chronique, mesures et état final complet, **zéro divergence et
zéro plantage** (`empreintes.json`). Référence figée `c63dd563`, calculée une fois
puis rangée dans le cache partagé ; branche `a8f9e2ad`, sans cache. Même
`PYTHONHASHSEED=0`, référence puis branche ; aucun gain de vitesse revendiqué.
La branche locale `main`, ancienne, n'est pas utilisée pour comparer d'autres
intégrations. Bruts dans `C:/Users/msics/donjon/artifacts/a2-passage-381/`.
L'ancien `fin.json` constate l'arrêt avant le banc ; **`fin-reprise.json` clôt la
reprise** : `tests_sociaux=0`, `base=1` (échec ancien attendu), `empreintes=0`,
`erreur=null`. Copie de base supprimée. Deux travailleurs à priorité réduite.
Ni suite complète ni Luna. Lot livré, non fusionné.

**Limites.** La fidélité du choix de Luna n'est pas garantie ; les revues restent
en place, A4/A6 hors lot. « Enjamber » et « escalader » sélectionnent dessus
comme auparavant ; la forme détermine la manière montrée et exécutée. L'ancienne
API `proposer_action` garde son schéma transitoire (A3) et ses contrôles moteur.
`moteur.py`, `mj.py` et `paroles.py` raccordent les actions seules et les paroles.
Aucun registre d'esprit, changement de revue ou raccord libre ; pas de
recouvrement avec 374/378/380. `etat-dev.md` est partagé ; 375 doit tenir compte
de l'évolution des schémas et de l'ancien attendu de rendu.
