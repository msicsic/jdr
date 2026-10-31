# Lot 392 — Connaissances explicites des scènes

Branche `codex-scenes-connues`, base `integration` : `ed5d9765` (laptop).
Correction livrée ; **vérification des cinq fichiers en cours, lot non validé**.

**Invariant.** Une scène qui suppose que Corvus peut désigner une référence ou
voir son nom la déclare connue ; le savoir privé d'un PNJ et une coïncidence
lexicale ne l'établissent pas. Aucun code du jeu, registre d'esprit, prompt ou
scénario modifié. Aucun changement du contrat de connaissance du 365.

**Attribution des trois méthodes Q2 du 390.** Reproduction sur la base : trois
échecs de sous-tests et une erreur. Dans `garde_ouidire`, seule la branche
Relais échoue : `crypte` n'est ni visitée, ni déclarée connue, ni apprise dans
la mémoire de Corvus. Le témoin et le gardien connaissent le lieu ; le rendu
public masque donc correctement sa référence. Le coffre de l'auberge est déjà
connu. Le test déclare désormais explicitement le lieu dans sa variante nommée.
Dans `mandat_joueur`, le banc suppose connus `brasero` et `echoppe`, tous deux
inconnus après préparation ; le fanal a déjà un souvenir visuel. Le fichier de
**banc de test** déclare les deux souvenirs dans `preparation.connus`, aussi
pour son premier tour « amener dans l'échoppe ». Le parcours sans jet forcé
conserve ses assertions de refus initial, information, acceptation et sauvegarde.

**Données historiques.** Comparaison récursive des sept données contractuelles
au commit `2d696f65` : seuls deux champs diffèrent, exactement ceux du 365 :
`relais.connus` passe de `[]` à `["cloche"]` ; `auberge.connus` passe de `[]` à
`["atre", "coffre_marchand", "lits_dortoir"]`. Les deux SHA-256 sont actualisés
avec ces champs inclus ; aucun savoir ni autre champ n'est exclu du hachage.
Les cinq autres empreintes et l'inverse de l'agenda 306 restent identiques.
Une assertion nomme les listes exactes de connaissances pour les sept scènes.
Les valeurs anciennes, nouvelles et chemins complets sont dans `diagnostic.json`.

**Chaîne complète et contre-épreuves.** La salle réelle du Relais et le coffre
de l'auberge sont éprouvés connus puis inconnus : parole effective, transmission
de croyance au gardien, état physique intact, sauvegarde/rechargement, monde
complet et rendus console/web identiques. Sans souvenir, la référence reste
irrésoluble et son nom absent des rendus rechargés. Deux mandats, avec sujet
objet et destination, sont refusés avec `attendu` sans souvenir et sans mutation ;
le souvenir déclaré permet ensuite la proposition enregistrée, sans déplacer
son référent. Fiche, comptes et scènes sont comparés après rechargement.

**Mesures.** Les quatre méthodes ciblées passent, **4/4 en 24,815 s** ; les
assertions supplémentaires d'absence du nom dans les rendus passent ensuite
(une méthode, quatre variantes, 12,087 s). Le premier lanceur a masqué le
namespace `tests` ; l'essai suivant a rencontré le refus Windows des temporaires
dans le bac à sable. Reprise hors bac à sable, sans adaptation du moteur.
La passe finale détachée porte sur `test_garde_ouidire`, `test_mandat_joueur`,
`test_occasions_scenarios`, `test_catalogue_connu` et `test_information_terminal`,
deux travailleurs au plus, priorité réduite. Sa fin est écrite en dernier dans
`C:/Users/msics/donjon/artifacts/scenes-connues-392/fin-verification.json` ;
`tests.json` contiendra les résultats et durées. Pas de suite complète, Luna ou
empreintes de simulation, conformément au brief sans changement du jeu.

**Limites.** La passe finale reste à lire avant validation et fusion. Ce lot
ne change ni l'admission d'une parole contenant un référent inconnu ni la
migration des mentions en prose anciennes. Bruts dans
`C:/Users/msics/donjon/artifacts/scenes-connues-392/`. Fusion au superviseur.
