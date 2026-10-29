# Lot 329 — G20, signes et attitudes rendus par le moteur

Branche `codex-g20-signes`, **non fusionnée**, base
`origin/codex-g5-perception c4cd83f` (lot 323). Aucune fusion avec integration.

**Invariant de la voie portée.** Une description typée de signes n'apporte
aucune phrase du MJ : dans le mode `dialogue` existant, `texte.signes_de`
sélectionne les références publiques des personnages visés. Le moteur rend
leurs signes actuels et leurs impressions, toujours présentées comme faillibles.
`signes.textes` est commun à cette réponse et à `rendu.regarder` ; aucun nouveau
jet, geste, sentiment certain ou intention privée n'est produit. Une cible hors
de vue sans signe perceptible passe par le constat et le souvenir bornés de G5.
Les références privées, inconnues et les sélections mal formées sont refusées
avec un `attendu`, puis corrigées par le protocole commun.

**Écriture.** `narration.consigner` recalcule la sélection sur le monde courant,
avant la mémorisation de la conversation, la sauvegarde et l'affichage dans
`jeu.py`. Une préparation ancienne ne fige donc pas un signe disparu. La réponse
ainsi produite ne passe par aucun audit narratif ni extraction d'attitude.
La prose libre garde tous ses contrôles actuels. Le code d'extraction du lot 176
n'est pas présent dans cette base non fusionnée : aucun contrôle existant n'a
été retiré de la prose libre. Son banc `attitudes` et sa préparation sont repris ;
l'étape de repos utilise le constructeur commun actuel `_etape`.

**Vérification sans réseau : 119 tests, neuf fichiers, tous verts**, zéro échec,
erreur ou saut, 24,457 s cumulées, deux travailleurs à priorité réduite. Les huit
nouveaux tests couvrent Ilse et Gorm du banc 176, un autre PNJ (Brune), plusieurs
personnages, les impressions incertaines, la perte de signe et d'impression entre
préparation et écriture, la perte de vue, les identités inconnues et la correction
de sélection. Monde, esprits, lectures, horloge et paroles restent inchangés par
une description seule. Texte, scène, carte et état complet contrôlés après
recharge ; présence du texte sur disque vérifiée au moment de son affichage.
Les fichiers concernés de narration, schémas, G5, relances et bancs sont verts.
Ni suite complète ni banc PNJ.

**Luna : passe unique préparée**, `gpt-6-luna`, `signes-ecart`, `signes-guet`,
`attitudes`, sur copies, coffre principal via `SEUIL_AUTH`. Lancement détaché,
priorité réduite, deux processus au plus ; `fin-luna.json` écrit en dernier même
en cas d'échec. Résultats à lire avant clôture. Référence historique `c9459ce`,
passe 1, lue dans les archives existantes pour les deux scripts de signes,
sans relance de référence ; aucune référence Luna `attitudes` disponible dans
ces archives ni dans le cache partagé. Pas de comparaison de temps entre charges.

**Limites et intégration.** La fidélité de la sélection à toute saisie libre
reste le travail du MJ ; cette garantie porte sur le rendu typé, pas sur toute
prose française. Aucun bénéfice Luna revendiqué avant lecture de la passe.
Recouvrements possibles avec 328/G6 : `donjon/mj.py` (schéma et admission des
descriptions), `donjon/rendu.py`, `donjon/narration.py`, `jeu.py` ; conserver les
deux rendus et l'ordre écriture → mémorisation → sauvegarde → affichage.
Bruts : `C:/Users/msics/donjon/artifacts/g20-329/`, notamment
`tests-cibles.json`, `references.json`, `luna-a-jouer.txt`, `luna-branche/` et
`fin-luna.json`. Livraison sur origin, sans fusion.
