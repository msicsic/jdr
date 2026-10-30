# Lot 369 — U-T social information

Branche `codex-ut-social-information`, base d'intégration `e0826efc`, **terminée, non fusionnée**.

## Invariant et changement

Console et TUI choisissent les mêmes destinataires et paramètres publics que le
formulaire web du lot 354. La commande `information`, annoncée dans la console
et l'onglet Gestes (F7), ouvre `InformationTerminal` dans `dialogues.py` :
destinataire, acte, puis champs du catalogue `formulaires_information`.
La projection `information_publique` est copiée à l'ouverture ; les références
publiques distinguent les homonymes. Aucun lieu annoncé n'est présélectionné.

Le dernier choix transmet le descripteur U-D à `preparer_direct` dans `jeu.py` :
mêmes transactions de parole, réponses G16,
consentement et révalidation. Une affirmation attend « tenter » ou « annuler » ;
les questions sont immédiates. Les étapes intermédiaires et l'annulation du
formulaire n'envoient aucune commande au moteur.

Production : `jeu.py`, `donjon/tui.py`, `donjon/dialogues.py` seulement.
Catalogue, `paroles.py` et descripteur U-D inchangés : aucun recouvrement avec 365.

## Vérification et mesures

**79 tests distincts validés / six fichiers, zéro échec, erreur ou saut** :
77 succès conservés, puis **2/2 repris verts en 114,198 s**. Les 71 tests
existants (581,962 s) sont inchangés : TUI 28, cases 5, U-M information 12,
G16 8 et dialogues 18. La première passe des huit nouveaux tests (828,566 s)
portait deux échecs de harnais : le témoin web déplaçait le destinataire avant
le chargement, perdant le souvenir perceptif conservé par le terminal.
Le départ intervient désormais à la préparation dans les deux voies.
Seules les deux méthodes concernées ont été rejouées ; les empreintes et l'AST
attestent la production, les autres tests et les assertions de comparaison inchangés.

Les vrais callbacks web Node, la console et la TUI Textual comparent
descripteurs, contenus typés, rapports, monde, croyances, paroles, scène et
fiche après recharge ; la sauvegarde précède la publication.

Scènes : voix qui se nomme, deux localisations crues fausses, ressources
possédées ou absentes, affirmation, homonymes dans un second scénario,
méfiance, annulations et départ à réception ou à confirmation.
**32 parcours mesurés**, seize par terminal : **16–29 touches**, commande
`information`, Entrée et confirmation comprises ; **17–30 avec F7** en TUI.
Sans annulation ni départ : 16–28. Lecture et défilement non chronométrés.
**Zéro appel au modèle et zéro analyse de texte sur ces choix directs.**

Refus d'accès aux répertoires temporaires : reprise hors bac à sable,
priorité réduite, deux travailleurs au plus. Ni Luna, banc ni suite complète.
Bruts : `C:/Users/msics/donjon/artifacts/ut-social-information-369/`.
Le `fin-calcul.json` rouge initial et l'incident d'import du premier lanceur
de reprise sont conservés. **`fin-cloture.json` : `ok=true`**, avec résultats,
mesures et empreintes ; aucun calcul actif.

## Limites et livraison

« Où est » reste réservé aux personnes ; annoncer la position d'un objet connu
reste possible. Une réponse entendue ne prouve pas sa vérité. Le moteur revalide
les choix affichés à l'exécution et après confirmation.
Branche poussée ; fusion et vérifications d'intégration laissées au superviseur.
