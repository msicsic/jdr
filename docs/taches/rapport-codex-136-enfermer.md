# Rapport Codex 136 — enfermer et s'évader

Branche `codex-enfermer`, **non fusionnée**, base `bce47d8` : dépendance voulue au
lot 134 `codex-trainer`, non fusionné. Aucun Luna, scénario modifié, fichier réservé
aux lots 133/135 touché, ni modification de `main` ou d'`integration`. Python du dépôt
principal ; deux calculs au plus, priorité réduite.

**Invariant** : `tenir.valider_verrouillage` valide porte/contenant fermé, intact et
clé portée correspondante. Commande, fiche, action typée et manœuvre composée passent
par le même moteur ; les refus portent un `attendu`. `tenir.enfermer` qualifie le
verrouillage comme contrainte envers les personnes crues dans une salle sans autre
issue crue libre. Les PNJ emploient leurs croyances explicites, le joueur sa mémoire
visuelle ; aucun personnage inconnu n'est situé par le repli des objets fixes.
Le registre commun conserve victimes, porte, témoins, souvenirs et relations avant rendu.

Le constat vient d'un essai de porte (`_pas`, `_ouvrir_en_chemin`, `_rate`), sans geôlier
inventé. Appel par l'ouïe commune, puis `tenir.evasion` cherche à quitter la salle dans
le graphe ordinaire : clé, acquisition d'outil, crochetage ou force. Le protecteur alerté
rejoint la salle avec sa clé. `force` partage les dégâts d'outil et d'épaule
(1 + mod FOR positif) ; coup de porte bruyant en trois secondes, coût cohérent,
répété jusqu'au bris ou à la révision du plan. Brisée, elle reste ouverte et déverrouillée.
Valeurs et permissions conservées ; aucun nouveau choix autonome d'enfermer.

**Épreuves** : sur décision utilisateur, le beffroi, ouvert vers la chambre de la cloche,
est remplacé par le bureau et la réserve existants de la mine. Aucune donnée de scénario
retouchée ; `--etat personne:enferme:salle` prépare seulement position et portes fermées
à clé, et refuse une issue sans porte. Lucien appelle, Josse ouvre avec son passe sans
bris ; Bram, privé de sa clé, force à la pioche ; Odon crochète. Le joueur assomme Bram,
le traîne au bureau, contourne son corps, ferme puis verrouille devant Gaspard : mémoire
et méfiance persistées. Réveil, constat et bris suivent. Un laps de 60 secondes entier
ou découpé avec recharges donne le même `data` complet et le même rendu. Deux salles,
présence inconnue, autre issue libre, commande, composition et bruit entendu sont vérifiés.

**Tests** : **159 ciblés finaux verts, douze fichiers**, consolidés sans recompter les
reprises. Suite complète unique : **2 091 tests, 1 094,80 s, huit échecs et une erreur**.
Reprises des défauts nouveaux vertes : portée locale d'`ErreurMonde`, issue sans porte
assimilée à tort à un verrou, puis attentes de voix et de choix de clé adaptées.
Les voix sont observées à leur présentation, avant l'évasion qui change la lumière ;
l'ouïe conserve le contrôle du laps découpé avec bris plutôt que clé.
Les **deux échecs MiMo `6 != 5`**, déjà documentés sur la base, restent non corrigés.
Aucune seconde suite complète ; pas de prétention à une suite entièrement verte.

**Banc 4 h × quatre scénarios × quatre graines : 13/16 strictement identiques**
(état final, empreintes, chronique, mesures, constats). Écarts de crue : 1985, départ de
Gorm au palier à 104 min ; 7, Aubin y passe à 103 au lieu de 104 ; 2024, même avance
pour Ilse. Une étape `frapper` devenue inutile après l'ouverture par un tiers finit
désormais en trois secondes au lieu d'une minute. Contre-épreuve sur les seules branches :
rétablir cette durée seule rend les trois états finaux et chroniques strictement identiques
à la base. Durée commune conservée, aucun correctif de scénario. Minutes-personnes dans
l'eau : 215→155, 60→75, 110→115 ; au sec final, graine 7 : 4→3, graine 2024 : 3→4.
**Aucun plantage, usurpation, violation ni nouveau constat d'audit** ; l'identité des seize
nuits n'est pas acquise. Les seize références absentes ont été calculées une fois et cachées,
sans rejeu de référence. Bruts : `artifacts/enfermer-136/`, dont `identites.json` et les
contre-épreuves. Aucune conclusion de performance sur le poste partagé.

**Limites et livraison** : les valeurs peuvent écarter la destruction d'un bien d'autrui ;
l'évasion n'en garantit pas le succès. Inquiétude `captif`, volonté brisée et validation
narrative Luna restent hors lot. Les scènes Brune/Ilse au beffroi ne sont pas revendiquées.
Aucune clé de signature Git configurée : commit non signé, branche poussée, aucune fusion.
