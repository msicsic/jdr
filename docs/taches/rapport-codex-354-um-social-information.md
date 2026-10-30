# Lot 354 — U-M social information

Branche `codex-um-social-information`, base intégration `57c9771d`, **terminée, non fusionnée**.

## Invariant et changement

Le formulaire choisit un interlocuteur perçu (voix comprise), l'acte d'information
et ses paramètres connus de Corvus. `information_publique` ne transporte que des
couples identifiant/nom : aucune position du sujet, croyance d'autrui ou possession
cachée. Le lieu annoncé reste un choix explicite, sans valeur présélectionnée.
`parole_information` produit contenu typé et mots sans analyser de texte ;
`preparer_information` est l'entrée U-D commune vers les transactions de parole,
G16 et U-C : préparation sur copie, révalidation, sauvegarde avant affichage.
Une affirmation attend « tenter » ou « annuler » ; les questions sont légères.

## Raccord autorisé et recouvrement

Deux extensions au brief ont été autorisées explicitement : neuf lignes dans
`jeu.py` appellent cette fonction ; `preparer_parole` reçoit l'adresse structurée
interne après contrôle exact du contenu canonique. Les deux entrées rejoignent les
mêmes validateurs de destinataire, de portée, de contenu et de réception. Les règles
de réponse, d'audience et de localisation ne changent pas ; aucun MJ ou compilateur
n'est modifié. **Fichier commun avec 353 : `jeu.py`**, bloc des descripteurs.
Le récapitulatif masque aussi les identifiants privés des ressources choisies.
Il distingue référence explicite et recherche lexicale : apprendre un objet ne
réinterprète pas les mots d'une recherche textuelle après l'aperçu U-C.

## Vérification et mesures

**112 tests distincts / dix fichiers verts**, zéro erreur, échec ou saut :
**24/24 rejoués en 506,990 s** (douze tests du lot, G16 et compréhension),
88 résultats conservés après contrôle des sources. Le premier bilan consolidé
comptait 111 tests, une erreur G16 introduite par le rendu : « bois » devenait une
référence après l'aperçu, exigeant une seconde confirmation. La correction conserve
le rendu textuel antérieur ; le cas réel et deux recherches après apprentissage
passent, sans modifier l'oracle G16. Les passes intermédiaires rouges restent archivées.
Le contrôle AST conserve toutes les autres fonctions de `paroles.py` et atteste
le chemin textuel du récapitulatif identique à la base, hors branche explicite U-D.

Les quatre actes passent par les vrais callbacks Node et la boucle de jeu au Relais
et à l'auberge : voix qui se nomme, croyances fausses, méfiance, homonymes, référence
masquée, annulation, départ à réception et à confirmation. Contenus, rapports,
monde, mots entendus, scène, fiche et regard sont comparés après recharge ;
la sauvegarde précède l'affichage, avec zéro analyse du clic et zéro appel au modèle.
Le harnais réinstalle la mémoire perceptive comme la vraie boucle et normalise
seulement tuples/listes JSON ; tous les champs mécaniques restent comparés.

**17 mesures Node : une saisie évitée par acte ; 6 clics** pour l'identité,
**8** pour ressource/localisation, **11** pour annoncer un lieu, confirmation comprise.
Deux clics par liste déroulante : ouverture et choix ; temps humain non mesuré.

## Limites et livraison

**Demander la localisation d'un objet reste indisponible**, limite explicitement
acceptée et affichée : la règle actuelle réserve cet acte aux personnes. Dire où
se trouve un objet connu est une affirmation typée ; aucune réplique libre du PNJ
n'est inventée. Pas de Luna, suite complète ou banc PNJ ; deux travailleurs réduits
au plus. Bruts : `C:/Users/msics/donjon/artifacts/um-social-information-354/`.
La fin rouge `fin-calcul.json` reste intacte ; **`fin-cloture.json` : `ok=true`**,
avec `contrats-cloture.json`, `mesures-cloture.json` et les empreintes des sources.
Aucun calcul actif ; branche poussée, fusion et suite complète laissées au superviseur.
