# Lot 355 — E4, accord initial daté

Branche `codex-e4-accord-date`, base `origin/integration 9b66d5a`, PC fixe
(`msi-desktop`). Code mesuré : `60f340b`.

**Invariant.** Le terme typé existant `part` ou `tache` peut porter `limite`,
instant absolu en dixièmes. Le moteur refuse toute autre clause temporelle,
le prêt daté, le maintien continu et un échange daté sans pièces présentes,
avec un `attendu` qui désigne une seule cause. La limite n'est jamais recalculée.
`echanges.proposer` conserve les contrôles ordinaires du marché et raccorde le
jugement E3 du contractant, puis le paiement et l'obligation E1 dans sa transaction.
Pour une part, le devis porte sur la pièce détachée, sur copie ; une remise
immédiate n'exige aucune durée future. Une durée indéterminée refuse la garantie,
sans supprimer la clause ni interdire une nouvelle proposition sans limite.

**Fonctions.** `propositions` partage schéma, validation et mots des termes.
`_juger_termes_dates`, `_remettre_part`, `engager` et `_vendre` réemploient les
moyens, avances, ventes et remboursements existants ; une source de pièces
explicitement choisie est conservée. `remettre` clôt les obligations du joueur
comme celles des PNJ. `agendas.prendre` archive les termes initiaux
avec la référence ; `accord_deja_conclu` reconnaît la même soumission pendant
l'engagement et après sa clôture E2. La recharge contrôle parties, prestation,
limite, avance et absence de doublon ; le contrôle AST couvre ce nouveau stockage.
Le rendu moteur des comptes, des promesses et des émissions donne les termes,
le paiement présent, la limite absolue et le temps restant. Les refus de délai
gardent leur raison publique et leur attendu privé. Dans `paroles.py`, seul
`_proposer` change : aucun transport d'adresse ni autre fichier réservé modifié.

**Épreuves.** 151 tests dans 18 fichiers ciblés/voisins : **146 verts**, cinq
échecs reproduits sur la base intacte `9b66d5a` (quatre dans `test_taches_payees`,
un dans `test_comptes_naturels`, provenance du texte depuis G16). Aucun nouvel
échec. Les 14 épreuves E4 finales et les six tests du socle passent ; dernier
groupe de remises : 44 tests verts en 38,014 s, deux processus à priorité réduite.
Huile Odile → Joss, huile Gaspard → Rémy,
feu du Relais, verrou du garde-manger et planches Aubin → Corvus : acceptation,
refus, délai impossible/indéterminé/passé, brouillon sans effet, double soumission
avant/après clôture, paiement sur source, accord inverse avec attente explicite,
corruption sauvegardée, réalisation T−1/T/T+1 et remboursement unique. La part
fournie par Corvus est close à sa remise présente ; sans devis autonome,
sa livraison future ne reçoit aucune garantie datée.
État, comptes, scène et paroles sont comparés après recharge ; livraison et
expiration passent en bloc et par laps découpés. Le test E1 vérifie désormais
que le temps restant diminue, tandis que la limite absolue reste identique.

**Banc rapide terminé.** 4 h, graines 1985/7/42/2024, Relais/auberge/mine,
deux processus à priorité réduite : **12/12 nuits identiques à la base exacte
`9b66d5a`**, chroniques, mesures et empreinte de l'état final complet. Audits,
relevés, boucles et état final d'audit également identiques ; seules les durées
de calcul diffèrent. Aucun plantage ni nouvelle alerte : zéro avis non justifié,
27 à expliquer, deux répétitions, deux `fige_presse`, un `noir_long` et un
`voir_alterne`, tous déjà présents sur la base. Les douze nuits divergent du
`main` publié `0bad227` dès la minute 0 ; ses neuf avis à expliquer deviennent
27 sur l'intégration, sans contribution d'E4. Références `main` relues du cache,
base calculée une fois, branche relue du cache pour la seconde comparaison ;
aucun rejeu ni comparaison CPU. Les deux commandes terminent avec code 0.
Bruts : `C:\Users\msics\donjon\artifacts\e4-355\` (`synthese-tests.json`,
`tests-base.json`, `banc-main.json`, `banc-base.json`, `synthese-bancs.json`,
`analyse-bancs.json`) ; `fin-bancs.json` confirme la fin sans erreur.

**Limites.** Cette livraison raccorde les propositions typées ; choix direct E5,
compilation libre E6, cycle durable des offres PNJ E7 et renégociation restent à
porter. Les mêmes parties et mêmes termes, dont la même limite absolue,
désignent une seule soumission : ils ne commandent pas une deuxième part.
Le devis reste subjectif et ne garantit pas la réussite ni une priorité sur la
survie. Les nuits ordinaires n'introduisent pas spontanément de délai ; aucun
gain autonome PNJ n'est annoncé. Ni suite complète, ni Luna, ni banc long lancés.
Les cinq échecs anciens restent hors de ce lot.
