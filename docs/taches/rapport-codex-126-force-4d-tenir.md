# Rapport Codex 126 — prises, liens et issues différées

Branche `codex-force-4d-tenir`, **non fusionnée**, base `28fa4b2`. Aucun appel à Luna,
aucune modification de `main`, d'`integration` ou des fichiers réservés aux lots 122/124.
Python du dépôt principal ; au plus deux processus de calcul à priorité réduite.

**Invariant réalisé pour saisir, ligoter, délier et se libérer** : `tenir.py` valide la
même règle pour le joueur et les PNJ ; les gestes longs enregistrent une issue sérialisable
dans `gestes_en_cours`. L'horloge traite leur échéance exacte, même sans événement PNJ à
cet instant. `pnj.finir_gestes` revalide conscience, contact, état de la victime et lien
avant toute mutation. Un coup ou l'inconscience retire l'issue ; une aide qui délie annule
aussi l'essai personnel de libération devenu sans objet.

La prise oppose FOR à FOR/DEX (10 par surprise), interdit les pas, coûte −2 aux coups et
cesse lorsque celui qui tient entreprend un autre geste que frapper/parler. Les liens
interdisent déplacement et gestes des mains. Ligoter demande un lien intact porté et une
victime sans défense, rendue ou tenue par un autre ; délier demande 10 s, couper d'une lame
3 s, se libérer DEX contre 18 après 10 min. L'entrave reste sur la victime et ne peut être
employée ou déplacée ; elle revient à celui qui délie. Le contrat passe par moteur,
opérations composées, déplacement d'objet, portage et passage commun, pas seulement par
les commandes. Les refus ajoutés portent un `attendu` en identifiants.

Les protecteurs rejoignent un protégé ligoté perçu puis le délient ; les captifs tentent
de se libérer. Aucun choix autonome de saisir ou ligoter. Les nouvelles contraintes
utilisent le registre des témoins et le souvenir `subi` existants ; délier et se libérer
ne fabriquent pas de témoins de faute. Prise et liens sont visibles après rechargement,
sans exposer d'auteur inconnu. Les fiches locales précèdent les tentatives et les issues
du joueur sont rendues après leur enregistrement.

**Vérifications** : suite complète unique, **2 063 tests, deux échecs MiMo, aucune erreur**,
223 fichiers, deux processus réduits, **1 072,38 s**. Les mêmes deux échecs `6 != 5` sont
reproduits dans les deux fichiers concernés sur une archive intacte de `28fa4b2` (13 tests).
La suite n'est donc pas entièrement verte ; aucun échec nouveau établi. Après les derniers
ajustements, **63 tests ciblés verts**, quatre fichiers, un processus réduit, **26,14 s**.
Les scènes couvrent Brune (avec la vraie ficelle de l'atelier) puis Aubin assommés/ligotés/déliés,
saisie de face et par surprise, pas refusé,
dégagement, Gorm déliant Aubin puis Ilse, libération seule réussie/ratée, joueur ligoté,
lien physique d'un mètre, réveil/coup/inconscience/perte du contact ou du lien interrompant
le ligotage ; rotation incluse dans l'échéance et coupe en trois secondes ; réussite/échec
de libération dans le journal du joueur. Le ligotage donne les mêmes `data` complètes et
le même rendu après recharge et découpage du laps ; les autres parcours sont rechargés.
**Banc rapide : 4 h × Relais/rixe × 1985/7/42/2024, 8/8 états finaux (SHA-256) et
chroniques identiques à la base**, aucun plantage, usurpation, violation ou ligotage
spontané. Six alertes `fige_presse` de chaque côté, inchangées. Référence absente du cache :
huit nuits jouées une fois puis rangées ; aucun rejeu de référence. Bruts : `artifacts/tenir-126/`.

**Limites** : livraison partielle expressément permise par le brief ; **traîner reste à
faire**. Le reste de 4d (enfermer, forcer les portes, captivité prolongée) reste également
hors de cette partie. Le secours à un protégé ligoté perçu est une réaction locale avec
approche commune ; le planificateur réservé n'est pas modifié. Le schéma du danger durable
de 4c reste limité aux coups/poussées : les prises et liens passent par `subi`, les témoins
et les réactions corporelles, sans élargir ce schéma situé dans `esprits.py`, fichier exclu
du lot. Aucune garantie narrative
sémantique supplémentaire, aucune migration générale d'anciennes parties revendiquée.
Poste partagé et conditions de charge différentes : aucune conclusion de performance.

Aucune clé Git de signature configurée sur ce poste : commits non signés.
