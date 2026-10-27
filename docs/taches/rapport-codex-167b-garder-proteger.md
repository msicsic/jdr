# Lot 167 b — garder, livraison partielle

Branche `codex-garder-proteger-b`, **non fusionnée**, base `f5eb72b`
(code de référence `6d87361`), code `57cf8fe` puis `70717fb`. Livraison partielle autorisée
par le brief : **A4b n'est pas achevé**. Aucun Luna ni fichier MJ réservé.
Bruts exclusivement `C:/Users/msics/donjon/artifacts/garder-167b/`.

**Invariant livré.** Une même charge déclarée par une pulsion et un agenda
ne coûte qu'une fois. `deliberation.charges_gardees` alimente les lieux gardés,
les menaces, `defense.charges` et `planification.prix_gardes` (ensemble de lieux,
maximum par lieu). L'agenda `garder` vise un objet ou un lieu avec le plan
commun `garder` ; pour l'objet, l'interposition est son premier sous-but
lorsqu'une approche vue la permet. La routine de garde de la pulsion visant
le même objet est supprimée, sans supprimer ses autres conditions à rétablir.
Le poids accepte une charge sans destinataire humain. Sommeil sans plan,
réessai sur croyance nouvelle et publication différée du lot 146 b conservés.
L'échéance abandonne avec cause et ne réactive pas l'agenda. Une garde tenue
reste active ; une position inconnue ne prouve jamais une perte.

**Vérification.** 29 ciblés distincts verts : 28 dans cinq fichiers (8,39 s),
puis le test de réveil supplémentaire dans la suite finale. Cas réel
Anselme/ballot avec agenda seul, deux autres gardiens, joueurs et PNJ
approchants : poste, avertissement et conséquences relationnelles après
rechargement. Monde complet et rendu identiques après laps entier/découpé ;
devis sans mutation, publication différée de l'échéance et cause persistante,
lieu sans objet, prix identique avec pulsion seule, agenda seul ou les deux.
Première passe : deux échecs (priorité de l'interposition corrigée ; assertion
de test ignorant les protégés du profil adaptée). Aucun agenda de départ
historique ajouté : les épreuves sont déclarées dans les données des tests.

**Mesures.** 16/16 empreintes 2 h identiques à la base d'intégration : Relais,
mine, auberge, crue × quatre graines, chronique, mesures et état final complet.
Cette référence isole le lot des changements déjà intégrés depuis `main` ;
seuls les manques du cache ont été calculés, aucune référence rejouée.
Banc rapide auberge 4 h × quatre graines : toutes les mesures identiques,
passages horaires maximaux moyens **13,75 → 13,75** (12–15), zéro plantage,
violation, usurpation ou bascule ; seul constat historique `noir_long`, inchangé.
VERIFIER + spatial 0,2, auberge fixe 1985, 2 h : monde complet et rendu
identiques après sauvegarde/rechargement. Coût auberge fixe 1985, 4 h :
**201 recherches, 190 neuves, 4 220 nœuds**, inchangés ; CPU indicatif
**9,88/9,91 s** sur poste partagé, sans conclusion de vitesse.
Ces bancs portent sur `57cf8fe`, sans agenda historique nouveau. `70717fb`
complète seulement le réveil d'une garde endormie par l'interposition,
avec un test de publication différée ; la suite finale porte sur ce code.
Le coût d'un agenda de garde actif n'est pas isolé par ces nuits historiques.
Suite complète unique : **2 246 tests, 258 fichiers, 2 209,27 s**, zéro erreur
ou ignoré, deux échecs MiMo historiques `6 != 5` (`test_fournisseurs_jeu`,
`test_restes_fusions`), déjà documentés sur la base. Aucune seconde suite.

**Reste.** La sorte `protéger`, le suivi à portée de voix et l'appel sur
agenda ne sont pas livrés. Pour `garder`, les fins pour bien rendu, perdu ou
détruit restent à définir sur les connaissances du porteur ; seule l'échéance
est vérifiée. L'interposition pour un lieu sans objet n'est pas réalisée.
Les limites du lot 167 (accès contournable, perception et poste admissible)
demeurent. Pas de garantie supplémentaire sur les manières ou l'hystérésis.
Un seul travailleur réduit pour cohabiter avec le lot 169. Deux journaux
automatiques des tests à chemins fixes ont été déplacés dans `generes-auto/`
du dossier de bruts ; les écritures suivantes ont été redirigées vers ce
dossier externe par une jonction, retirée en fin de suite. Aucun brut local
restant. Vérification au-delà du créneau pour conserver un seul travailleur.
Aucune clé de
signature Git configurée ; commits non signés. Branche seule poussée,
sans fusion ni modification de `main`.
