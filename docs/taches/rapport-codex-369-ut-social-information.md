# Lot 369 — U-T social information

Branche `codex-ut-social-information`, base d'intégration `e0826efc`, non fusionnée.

## Invariant et changement

Console et TUI choisissent les mêmes destinataires et paramètres publics que le
formulaire web du lot 354. La commande `information`, annoncée dans la console
et l'onglet Gestes (F7), ouvre `InformationTerminal` dans `dialogues.py` :
destinataire, acte, puis champs du catalogue `formulaires_information`.
La projection `information_publique` est copiée à l'ouverture ; les références
publiques distinguent les homonymes. Aucun lieu annoncé n'est présélectionné.

Le dernier choix transmet le descripteur U-D exact à `preparer_direct`, déjà
raccordé dans `jeu.py` : mêmes transactions de parole, réponses G16,
consentement et révalidation. Une affirmation attend « tenter » ou « annuler » ;
les questions sont immédiates. Les étapes intermédiaires et l'annulation du
formulaire n'envoient aucune commande au moteur. La TUI reçoit uniquement la
projection publique, sans référence au monde mutable.

Trois fichiers de production changent : `jeu.py`, `donjon/tui.py`,
`donjon/dialogues.py`. Ni le catalogue, ni `paroles.py`, ni le descripteur U-D
ne changent : aucun recouvrement de code avec le lot 365 annoncé.

## Vérification et mesures

Validation ciblée en cours : nouveaux tests `test_information_terminal.py`,
tests existants TUI/cases inchangés, U-M information, G16 et dialogues.
Le harnais utilise les vrais callbacks web Node, la console et la TUI Textual.
Il compare les descripteurs, contenus typés, rapports, monde, croyances,
paroles entendues, scène et fiche après recharge ; il vérifie également la
sauvegarde avant publication et interdit l'analyse de texte et les appels MJ.

Scènes : voix qui se nomme, deux localisations crues fausses, ressources
possédées ou absentes, affirmation, homonymes dans un second scénario,
méfiance, annulations et départ à réception ou à confirmation. Mesures des
touches enregistrées avec la commande d'ouverture, Entrée et confirmation ;
F7 compté séparément. La lecture et le défilement ne sont pas chronométrés.

Les premiers lancements dans le bac à sable ont rencontré des refus d'accès
aux répertoires temporaires ; reprise hors bac à sable, priorité réduite,
deux travailleurs au plus. Ni Luna, banc PNJ, ni suite complète.
Bruts : `C:/Users/msics/donjon/artifacts/ut-social-information-369/`.
Deux passes ciblées restent en cours après la poussée `de4cc369` ; consolidation
détachée, `fin-calcul.json` écrit en dernier (résultats, mesures et empreintes).
À la reprise : lire ce fichier et les traces, corriger tout échec avant clôture.

## Limites et livraison

« Où est » reste réservé aux personnes, comme au web ; annoncer la position
d'un objet connu reste possible. Une réponse reçue ne garantit pas la vérité
du contenu. Le formulaire conserve ses choix affichés ; le moteur revalide
leur admissibilité au moment de la parole et après confirmation.
La fusion et les vérifications d'intégration restent au superviseur.
