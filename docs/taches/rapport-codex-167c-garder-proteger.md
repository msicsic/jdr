# Lot 167 c — responsabilités de protection, livraison partielle

Branche `codex-garder-proteger-c`, **non fusionnée**, base `1aba0df`, code
`13fde5f` et `5f69840`. Livraison partielle expressément permise par le brief :
**A4b reste inachevé**. Bruts exclusivement
`C:/Users/msics/donjon/artifacts/garder-167c/`. Aucun Luna ni fichier MJ réservé.

**Invariant livré.** Une responsabilité de protection a les mêmes conséquences
qu'elle provienne du profil ou d'un agenda. `deliberation.proteges` réunit les
deux sources sans doublon et conserve l'ordre historique du profil.
`agendas.proteges` lit les déclarations sans les activer ; sommeil conservant
la responsabilité, échéance et état terminal la retirant. Appels, cris reconnus,
défense, interposition, devoir, réanimation, perception des atteintes, témoins
et secours aux liens partagent cette lecture. Les raccordements nécessaires
touchent aussi `esprits.py`, `ouie.py`, `pnj.py` et `tenir.py` : aucun nouveau
geste ni règle propre à un scénario. La mort crue abandonne avec sa cause,
dans la publication différée du choix ; position inconnue non terminale et
absence de renaissance. L'interposition d'une personne utilise le poste commun.

**Épreuves.** Déclarations uniquement dans les données des tests, aucun agenda
historique ajouté. Gorm/Ilse : appel réel entendu, course, affichage au joueur
et recharge ; même laps de trois minutes entier/découpé, monde et rendu
identiques. Deux autres configurations d'interposition (marchand puis Aubin
protégeant Brune), poste réellement rejoint et avertissement enregistré et
entendu après recharge. Fins crues sur Ilse et Brune, responsabilité unique
avec profil et agenda, lecture et devis sans mutation, publication différée.
Sélections finales : **36 puis 38 tests verts** (recouvrement entre sélections).
Une erreur initiale du test de fin (croyance de lieu sans salle/case) corrigée.
Suite complète unique : **2 255 tests, 260 fichiers, 1 302,232 s**, deux
échecs MiMo historiques `6 != 5` (`test_restes_fusions` et
`test_fournisseurs_jeu`), zéro erreur ou ignoré ; aucune seconde suite.

**Mesures.** **16/16 empreintes 2 h identiques** à la base d'intégration :
Relais/mine/auberge/crue × quatre graines, chronique, mesures et état complet.
Référence calculée et cachée une seule fois, aucun rejeu de référence.
Banc Relais 4 h × quatre graines : toutes les mesures identiques, passages
horaires maximaux moyens **6,25 → 6,25** (5–8), zéro usurpation, violation,
bascule ou plantage ; trois constats historiques `fige_presse` de chaque côté.
`VERIFIER` + spatial 0,2, Relais fixe 1985, 2 h : monde complet et rendu
identiques après sauvegarde/rechargement. Coût Relais fixe 1985, 4 h :
**265 recherches / 129 neuves / 3 058 nœuds** inchangés ; CPU indicatif
3,42/3,28 s, sans conclusion de vitesse sur poste partagé. Ces nuits historiques
ne mesurent pas le coût d'un nouvel agenda actif ni un suivi vocal.

**Reste et limites.** Le suivi à portée de voix n'est pas livré : sans poste
d'interposition disponible, le projet dort explicitement avec la raison
`suivi vocal non pris en charge`, tout en restant responsable des secours.
Il manque un terminal commun de proximité vocale avec déplacement et coût
cohérents ; rejoindre seulement la salle ou détourner une parole ne le garantit
pas. Restent aussi la fin sur départ cru du protégé, les fins de `garder`
pour bien rendu/perdu/détruit et l'interposition d'un lieu sans objet (le
contrat actuel exige une charge localisée et un poste d'accès en cases).
Aucune garantie nouvelle sur les manières, l'hystérésis ou tous les accès.
La preuve de fin porte ici sur une croyance de mort installée en données,
pas sur une campagne de morts autonomes. Aucune clé Git de signature
configurée : commits non signés. Branche seule poussée, `main` intacte.
Deux travailleurs réduits au plus pour ce lot ; une jonction temporaire
redirigeait aussi les traces automatiques des tests hors du worktree,
puis a été retirée. Aucun brut local restant.
