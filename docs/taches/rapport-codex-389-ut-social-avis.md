# Lot 389 — U-T social avis

Branche `codex-ut-social-avis`, base `integration` **`5cc189c9`**, code
**`cf7a421f`**. **Lot terminé et validé, non fusionné**, le 2026-10-31.

## Invariant et changement

Console et TUI proposent la commande `avis`, annoncée dans l'aide console et
l'onglet Gestes (F7). Le formulaire choisit explicitement le destinataire,
l'acte, le lieu connu et la prévision oui/non. Son dernier choix transmet le
descripteur U-D `information / avis / sujet / valeur` du web ; « tenter »
confirme la parole. Aucun lieu ni aucune valeur présélectionnés.

`AvisTerminal` reprend le sélecteur `InformationTerminal` avec le catalogue
`formulaires_avis` du 386. Le petit raccord de `dialogues.py`, en plus de
`jeu.py` et `tui.py`, évite de recopier les champs ou leur validation dans les
interfaces. La projection est copiée à l'ouverture ; les références publiques
distinguent les homonymes. `preparer_direct`, U-C et G18 restent les seuls
chemins d'admission, réception, dispute et sauvegarde avant publication.
Pas de changement de `paroles.py`, de mécanique sociale ni de registre d'esprit.

## Vérification et mesures

**92 tests distincts validés, huit fichiers**, sans échec, erreur ni saut restant.
Première passe : **90/92 verts en 1 510,903 s** ; les deux erreurs TUI étaient
des `PermissionError` Windows au remplacement atomique des sauvegardes, avant
ouverture de l'interface. Reprise exacte de ces seules méthodes : **2/2 verts
en 21,864 s**, sans changement de code, de test ni d'assertion. Le premier bilan
rouge reste intact ; `fin-cloture.json` compose les succès et vérifie les
empreintes des sources inchangées. Aucun calcul actif.

Les **huit nouveaux tests passent en 403,199 s** : projection figée, choix
explicites, lieux inconnus et valeurs/paramètres forgés, revalidation d'un choix
devenu inconnu, homonymes, absence de croyance privée ; puis, dans chaque vrai
terminal, deux lieux/valeurs, disputes contraires sur deux lieux, annulations
et départ du destinataire à réception ou confirmation. Le harnais du 369
contrôle sauvegarde avant publication, absence de modèle et d'analyse,
blocage des gestes pendant le formulaire et absence d'envoi intermédiaire.
Les vrais callbacks web et chaque terminal conservent sujet/valeur sur
`echoppe` et `chambre_cloche`, avis positif/négatif et disputes contraires,
puis recharge et trois laps de 13/29/18. Monde, émissions, scène, fiche et
regard sont comparés. **14 parcours mesurés**, sept par terminal : **20 touches
jusqu'à la réponse**, **21 avec F7** en TUI ; annulation : 21, ou 22 avec F7.
Deux abandons de formulaire supplémentaires ne soumettent rien. Confirmation
comprise, lecture/défilement non chronométrés. Zéro modèle ou analyse des choix.

Un premier essai a rencontré les refus d'accès du bac à sable aux sauvegardes
temporaires ; les suivants utilisent le Python du dépôt principal hors bac à
sable, à priorité réduite. Une prémisse du nouveau test a été corrigée : un
lieu encore cité dans le contexte reste connu même retiré de `visitees` ; la
contre-épreuve retire désormais la seule source de connaissance d'un lieu
explicitement ajouté au préalable. L'assertion de refus reste inchangée.

Voisins verts : information terminal 9, avis publics 5, information publique 12,
TUI 28 (dont les deux reprises), cases TUI 5, avis parlés 7 et dialogues 18.
**Empreintes : 8/8 paires identiques**, chronique, mesures et état final complet,
sans plantage : 2 h crue/Relais × 1985/7/42/2024, **429,614 s**. Référence
exacte `5cc189c9`, car `main` local précède les lots MJ intégrés ; huit nuits
manquantes rangées une seule fois au cache commun. Zéro avis non justifié,
cinq avis à expliquer identiques, sans certification supplémentaire.
Deux travailleurs réduits au plus, étapes séquentielles ; aucune comparaison
de vitesse, suite complète ni Luna.

## Livraison et limites

Bruts : `C:/Users/msics/donjon/artifacts/ut-social-avis-389/`.
`verifier.py`, `tests.json`, `empreintes.json` et les journaux portent les preuves ;
`reprise.json` et `reprise.log` conservent les deux reprises exactes.
**`fin-cloture.json` : `succes=true`**, sources et assertions conservées.
`fin-calcul.json` rouge initial et les restes de sauvegardes refusées sont gardés.
Le prédicat disponible reste la menace d'eau ; une parole reçue n'établit
jamais la vérité de sa prévision. Branche poussée ; fusion laissée au superviseur.
