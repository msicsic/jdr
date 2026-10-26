# Rapport Codex 145 — tuer et les biens du mort (4e)

Branche `codex-force-4e-tuer`, **non fusionnée**, base `4c57020` (brief récupéré par
avance rapide). Aucun Luna, aucun fichier réservé aux lots 142 à 144 modifié ;
`main` et `integration` intacts. Python du dépôt principal, deux calculs au plus,
priorité réduite. Aucune clé de signature Git configurée : commit non signé.

**Invariant.** `tenir.valider`, `commencer`, `finir` et `preparer`, reliés au moteur
et au geste PNJ, ne donnent la mort qu'à l'échéance sauvegardée, après revalidation :
auteur conscient, cible vivante inconsciente ou ligotée au contact, arme portée
intacte ou mains nues. Cinq ou trente secondes, plus rotation, sans jet. Coup,
inconscience, réveil sans liens ou perte des conditions interrompent l'issue. Les
refus portent leur `attendu`, avec candidats perçus et références publiques.
Commande locale `tuer <personne> [avec <arme>]` ; aucun choix autonome ajouté.

La victime consciente crie par l'ouïe commune ; le registre conserve la lutte
bruyante. Témoins, souvenirs et relations passent par la violence commune ; les
verbes manquants complètent `social.GESTES`. « A tenté de tuer » ne promet pas une
issue encore interrompable. `corps.mourir` conserve l'auteur, la dépouille et ses
biens ; découverte et nouvelle de mort restent distinctes, sans coupable inventé.
L'horloge retire ses références locales à l'esprit mort pendant le laps. L'approche
de secours omettait l'argument `lignes` de `_marcher` : argument rétabli.

**Épreuves rechargées.** Brune ligotée tuée par le joueur : cri retenu par Ilse,
témoin, méfiance, parole de mort émise et reçue par Aubin avec confiance de ouï-dire.
Joss inconscient tué sans témoin puis découvert sans auteur attribué. Brune prend
un bien sur Aubin mort : propriété et faute conservées, témoin, aucun esprit défunt.
Joueur tué par PNJ : fin persistante, commande refusée. Refus libre et outil invalide,
absence de fuite dans les candidats ; réveil et interruption de l'auteur ; PNJ tuant
un autre PNJ, rendu ; même état complet et rendu après laps continu ou découpé et
rechargé. Les protecteurs sont endormis dans la scène de meurtre pour exercer son
issue sans secours, sans modifier les règles.

**Mesures.** 62 ciblés verts sur cinq fichiers (18,10 s), puis reprise finale des
huit tests `test_tuer` verte (0,89 s). Banc 4 h × quatre scénarios et rixe × quatre
graines : **20/20 identiques**, état complet (SHA-256), récit, souvenirs, chroniques,
mesures, relevés, boucles et constats ; temps exclus. Zéro mort, plantage, violation
ou usurpation. Vingt références manquantes jouées une fois et cachées. Aubin mort,
4 h/1985 au Relais puis à rixe : trois découvertes chacun, aucun plantage/usurpation.
Suite complète unique : **2 132 tests, 237 fichiers, 1 774,48 s, deux échecs MiMo,
zéro erreur ni ignoré**. Les deux échecs `6 != 5` sont reproduits sur
l'archive intacte de `4c57020` (13 tests, 10,23 s). Bruts : `artifacts/tuer-145/`.

**Limites.** La suite tourne à un processus pour cohabiter avec le banc ; les
compléments de rendu, de refus et de tests ajoutés après son lancement ont leur
reprise ciblée finale. Aucune seconde suite ni conclusion de performance. La saisie
et la narration Luna restent à **4f**, sans garantie sémantique nouvelle. Aucun PNJ
ne choisit de tuer ; la prise testée ne prouve pas un choix spontané. La découverte
visuelle d'un protégé mort relance déjà le devoir de 30 ; aucun choix de but ni
nouvelle réaction au ouï-dire ajouté. Aucune migration générale. Branche poussée,
sans fusion.
