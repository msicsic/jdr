# Lot 344 — U-M corps

Branche `codex-um-corps`, base `origin/integration 78766d9`, **non fusionnée**.

## Invariant et changement

Le menu d'une personne perçue propose les gestes corporels du moteur avec
choix explicites de méthode, de moyen et de direction. Le catalogue commun
`gestes_publics.formulaires_corps` pilote la page ; il ne teste aucune
aptitude. Les moyens viennent de la projection publique existante, jamais
de l'inventaire privé d'un PNJ. Les homonymes gardent leurs références et
leurs numéros de choix. La surprise reste une défense calculée, pas une
méthode imposable.

`commandes.proposition_descripteur` revalide les références exactes puis
construit la même proposition que la commande locale. Les commandes
`assommer`, `riposter`, `se rendre à` et `fuir` complètent cette parité.
Les réactions sont proposées seulement sur les auteurs de
`defense.dangers_vus` encore perçus, et partent sans approche automatique.

Un raccord dans `moteur.py`, nécessaire en plus des fichiers d'interface
prévus, applique la gravité des effets U-C à la famille portée et expose
« Compris » dans sa fiche. Il conserve le descripteur jusqu'à la
confirmation : toute référence perdue, tout état ou plan modifié impose
de choisir de nouveau le geste et relire l'aperçu, même sans nouvelle
révision. Annuler ne publie aucun effet. Les sauvegardes et résultats
passent par la boucle existante. Aucun changement du MJ, de `jeu.py`,
de `tui.py`, de `force.py`, de `combat.py` ou de `tenir.py`.

## Vérification et mesures

Vérification ciblée en cours, à priorité réduite, deux travailleurs au plus ;
`fin-validation.json` sera écrit en dernier après les compléments et les
mesures. Les lancements en bac à sable ont échoué sur les droits des
temporaires Python ; relance avec accès disque. Aucun bilan vert annoncé.
Scènes : scripts réels `force-4b-frapper`, `force-4b-assommer`,
`force-4c-fuir`, ligature 4d et seconde situation à l'auberge. Les parcours
comparent plan, effet, texte et monde/scène/fiche/carte après recharge,
avec analyseur interdit au clic et modèle instrumenté interdit d'appel.
Les quatorze parcours de mesure couvrent treize gestes et la méthode
assommer : une saisie remplacée par parcours ; clics réels du menu puis
confirmation comptés séparément, approche éventuelle en sus. Les chiffres
définitifs et les limites des tests restent à lire dans les bruts.

## Limites et intégration

Une offre n'est pas une promesse de réussite : le moteur refuse les moyens
inadéquats et les préalables manquants. L'inconscience ne rend pas tous
les gestes impossibles : frapper une personne sans défense est une règle
existante, conservée. Un changement après l'aperçu invalide en revanche
le consentement. Les gestes propres à Corvus (« mes liens », « me
dégager », « fuir ») gardent leur cible moteur propre, la personne du
menu servant de contexte perçu.

Recouvrement explicite avec **343/G7 : `moteur.py`** ; les rendus de
déplacement devront être conservés à la fusion. Documentation commune
avec 338/341/342 ; aucun fichier de leurs mécaniques modifié. U-T corps
reste à faire. Ni Luna, ni suite complète, ni banc PNJ : ce lot ouvre une
entrée d'interface vers les règles existantes. Bruts :
`C:/Users/msics/donjon/artifacts/um-corps-344/`.
