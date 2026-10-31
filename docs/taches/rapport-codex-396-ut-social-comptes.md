# Lot 396 — U-T social comptes

Branche `codex-ut-social-comptes`, base `origin/integration` **`1fd48fb5`**,
PC fixe, 31 octobre 2026. Code de production vérifié : **`28239716`**.
**Lot terminé et validé, non fusionné.**

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

**Dix nouveaux tests verts en 633,931 s**, avec **36 parcours mesurés**, 18
par terminal. Parcours nominal : 17 touches avec confirmation, 18 avec F7 ;
annulation U-C : 18/19 ; refus d'un compte périmé dès la réception : 10/11.
Deux abandons locaux supplémentaires n'envoient rien. Lecture et temps humain
non mesurés. La première passe rouge du harnais est conservée : corrections
de l'API Textual, de la référence publique et de la perception initiale ;
les péremptions comparent précisément l'état après la mutation injectée.

**Bilan groupé initial : 89/90 verts en 1 345,082 s**, huit fichiers, zéro
erreur ou saut. L'unique rouge est `test_conversation_accord_et_paiement_actualisent_la_fiche`
de `test_tui.py`, qui attendait un paiement immédiat après `remettre anneau`.
Il se reproduit sur l'archive exacte de la base `1fd48fb5` : même attente
de minute 1 à la minute 0 (`preuve-base-tui.log`, 62,209 s de test).
L'adaptation au consentement déjà requis par les lots [380](rapport-codex-380-um-social-comptes.md)
et [394](rapport-codex-394-don-consentement.md) ajoute l'aperçu à minute 0,
compare tout l'état hors conversation avant transfert, puis soumet `tenter`.
Les assertions anciennes de récompense payée, 44 pièces, possession de
l'anneau et sauvegarde restent intactes. Méthode adaptée : **verte en 2,112 s**.
La reprise du fichier TUI entier passe : **28/28 en 133,299 s**, sans erreur
ou saut. Avec les 62 tests inchangés des sept autres fichiers, **90 méthodes
distinctes sont vertes**, dont les dix nouvelles. Aucun code de production
n'a changé ; aucun autre test ni assertion de sécurité ancienne n'est modifié.

**Empreintes : 8/8 paires identiques**, chronique, mesures et état final complet,
sans plantage : 2 h Relais/auberge × 1985/7/42/2024, **285,934 s**.
Référence exacte `1fd48fb5` : huit nuits manquantes calculées puis rangées
une fois dans le cache commun. Un travailleur réduit, en parallèle de la
première passe des tests ; aucun changement des sources de production depuis.

Validation groupée détachée à deux travailleurs réduits ; preuve sur base et
reprise TUI ensuite, deux travailleurs réduits au plus. `fin-verification.json`
rouge reste intact ; **`fin-cloture.json` : `succes=true`** compose les 62 tests
inchangés des sept fichiers et la reprise des 28 TUI. Ses sept contrôles
valident les résultats, les sources de production et la seule adaptation
documentée de `test_tui.py`. Aucun calcul restant, aucun banc long, aucune suite
complète ni passe Luna. Aucune comparaison de performance revendiquée.

**Limite et livraison.** Le remboursement volontaire en pièces du 388 n'est
pas un choix de `comptes_publics` : il n'est donc pas ajouté au terminal.
Les dettes de Corvus restent visibles dans les lignes de comptes. Le lot
porte les raccourcis existants, sans éditeur de marché ni nouveau mécanisme.
Bruts et lanceurs : `C:/Users/msics/donjon/artifacts/ut-social-comptes-396/` ;
bilan final : `fin-cloture.json`. Branche poussée ; fusion laissée au superviseur.
