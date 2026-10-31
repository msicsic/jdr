# Lot 396 — U-T social comptes

Branche `codex-ut-social-comptes`, base `origin/integration` **`1fd48fb5`**,
PC fixe, 31 octobre 2026. **Code réalisé ; validation finale en cours, non fusionné.**

**Invariant et raccord.** La commande `comptes`, annoncée dans l'aide console
et dans Gestes (F7), affiche les lignes et raccourcis de `comptes_publics` du
380 : question sur le dû, réclamation, restitution d'un prêt, règlement d'une
offre déjà publique. Chaque ligne garde montant, objet, débiteur, créancier
et termes de l'offre ; les références publiques distinguent les homonymes.
Le numéro transmet directement le descripteur U-D, sans analyse ni modèle.
La préparation, le verdict moteur et le consentement U-C restent communs
avec le web ; aucune opération comptable n'est implémentée dans l'interface.

`jeu.py` et `donjon/tui.py` ouvrent le même sélecteur `ComptesTerminal`.
Ce petit adaptateur est isolé dans `donjon/comptes_terminal.py`, sur le modèle
du module de fabrication terminal, pour partager le rendu et la sélection
sans charger Textual dans la console. Il copie la projection à l'ouverture,
ne présélectionne rien et garde les termes périmés jusqu'à leur revalidation
par le moteur. Aucun paramètre public ne manque : `dialogues.py` est inchangé,
comme les mécaniques sociales, le consentement et les registres d'esprit.

**Vérification.** Les nouveaux tests utilisent les vrais callbacks JavaScript
du web, la boucle console et le pilote Textual. Ils comparent le monde entier
(seul le texte de saisie dans la conversation diffère), les comptes, les
émissions, la fiche, le regard et la scène après recharge. Les créances
d'Aubin et Brune, les deux prêts homonymes et les offres à deux et trois
pièces exercent les verdicts distincts ; les laps de 60 dixièmes et 13/29/18
emploient l'avancement réel des PNJ avec recharge. Annulation locale ou U-C,
choix invalide et compte périmé à réception ou confirmation sont couverts.
Le harnais contrôle la sauvegarde avant publication et l'absence de mutation
avant confirmation, hors mutation externe explicitement injectée.

Première passe conservée : 10 méthodes, 198,113 s, quatre réussites, deux
échecs et quatre erreurs de harnais. Corrections : API de rendu Textual,
référence publique du prêteur, perception spatiale installée avant la scène
de départ ; la contre-épreuve de péremption compare précisément l'état après
la mutation injectée. Aucun test existant ni assertion de sécurité ancienne
n'est modifié. Les deux tests de formulaire et les deux restitutions TUI
passent à la reprise ; la contre-épreuve console des annulations et six
péremptions passe ensuite en **88,510 s**. Les trois autres méthodes TUI
et les voisins attendent encore le bilan groupé. Parcours nominal : 17 touches
avec confirmation, 18 avec F7 ; annulation U-C : 18/19 ; refus d'un compte
périmé dès la réception : 10/11. Lecture et temps humain non mesurés.

**Empreintes : 8/8 paires identiques**, chronique, mesures et état final complet,
sans plantage : 2 h Relais/auberge × 1985/7/42/2024, **285,934 s**.
Référence exacte `1fd48fb5` : huit nuits manquantes calculées puis rangées
une fois dans le cache commun. Un travailleur réduit, en parallèle de la
première passe des tests ; aucun changement des sources de production depuis.

Validation finale détachée : huit fichiers ciblés et voisins, deux travailleurs
réduits, après l'achèvement des empreintes et des reprises ciblées.
Les scripts enregistrent les empreintes des sources et écrivent leur fichier
de fin en dernier. **Ne pas considérer le lot validé avant
`fin-verification.json` avec `succes=true`.** Aucun banc long, aucune suite
complète ni passe Luna. Aucune comparaison de performance revendiquée.

**Limite et livraison.** Le remboursement volontaire en pièces du 388 n'est
pas un choix de `comptes_publics` : il n'est donc pas ajouté au terminal.
Les dettes de Corvus restent visibles dans les lignes de comptes. Le lot
porte les raccourcis existants, sans éditeur de marché ni nouveau mécanisme.
Bruts et lanceurs : `C:/Users/msics/donjon/artifacts/ut-social-comptes-396/` ;
bilan attendu : `fin-verification.json`. Fusion laissée au superviseur.
