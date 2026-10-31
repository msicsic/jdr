# Lot 389 — U-T social avis

Branche `codex-ut-social-avis`, base `integration` **`5cc189c9`**, code
**`cf7a421f`**. Implémentation livrée ; validation finale en cours, non fusionnée.

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

Premiers contrôles : **quatre tests distincts verts** (deux de formulaire,
un parcours console et un TUI). Les parcours sur `echoppe` (oui) et
`chambre_cloche` (non) passent après comparaison aux vrais
callbacks web et à la parole typée, puis recharge et trois laps de 13/29/18.
**20 touches jusqu'à la réponse** dans chaque terminal, **21 avec F7** en TUI,
confirmation comprise ; zéro appel au modèle ou analyse de ces choix directs.
Dernière passe ciblée : trois tests, zéro échec/erreur, **80,688 s**.
La campagne finale n'est pas encore certifiée.

`tests/test_avis_terminal.py` ajoute huit tests : projection figée, choix
explicites, lieux inconnus et valeurs/paramètres forgés, revalidation d'un choix
devenu inconnu, homonymes, absence de croyance privée ; puis, dans chaque vrai
terminal, deux lieux/valeurs, disputes contraires sur deux lieux, annulations
et départ du destinataire à réception ou confirmation. Le harnais du 369
contrôle sauvegarde avant publication, absence de modèle et d'analyse,
blocage des gestes pendant le formulaire et absence d'envoi intermédiaire.
Monde, émissions, scène, fiche et regard sont comparés après recharge.
Aucune assertion de sécurité existante modifiée.

Un premier essai a rencontré les refus d'accès du bac à sable aux sauvegardes
temporaires ; les suivants utilisent le Python du dépôt principal hors bac à
sable, à priorité réduite. Une prémisse du nouveau test a été corrigée : un
lieu encore cité dans le contexte reste connu même retiré de `visitees` ; la
contre-épreuve retire désormais la seule source de connaissance d'un lieu
explicitement ajouté au préalable. L'assertion de refus reste inchangée.

Campagne détachée : huit fichiers (avis terminal, information terminal,
avis publics, information publique, TUI, cases TUI, avis parlés, dialogues),
puis empreintes 2 h, crue/Relais × 1985/7/42/2024. Deux travailleurs réduits
au plus, étapes séquentielles. Référence exacte de la base d'intégration,
car `main` local est antérieur aux lots MJ intégrés ; cache commun conservé.
Pas de comparaison de vitesse, suite complète ni Luna.

## Reprise et limites

Bruts : `C:/Users/msics/donjon/artifacts/ut-social-avis-389/`.
`verifier.py` conserve les commandes et empreintes des sources ; `tests.json`,
`empreintes.json` et les journaux portent les résultats détaillés.
**`fin-calcul.json` est écrit en dernier, succès ou échec : le relire avant
clôture.** Les résultats encore attendus ne sont pas déclarés verts.
Le prédicat disponible reste la menace d'eau ; une parole reçue n'établit
jamais la vérité de sa prévision. Fusion laissée au superviseur.
