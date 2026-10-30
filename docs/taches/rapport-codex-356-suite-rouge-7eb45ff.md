# Lot 356 — attribution de la suite rouge de `7eb45ff`

Branche `codex-suite-rouge-7eb45ff`, base `integration df03dc2f`.
**En cours : bissection v2 analysée ; compléments et validation des harnais détachés, `fin-complements.json` attendu.**

L'invariant recherché est la fiabilité de la suite : un test doit continuer à
contrôler son comportement historique, y compris l'état sauvegardé et le rendu,
en passant par le consentement lorsque celui-ci est requis. Les 143 échecs et
18 erreurs de la suite originale couvrent 61 fichiers. Leur origine n'est pas
présumée commune.

Le calcul rejoue uniquement les méthodes initialement rouges, dans des copies
natives du code et des tests de chaque révision. Deux processus de test au
maximum, priorité réduite ; aucun modèle, banc ou suite complète. Le témoin
initial est `9e0f86f0` (fusion du lot 339), la borne rouge `7eb45ff9`.
Les révisions qui modifient seulement la documentation sont écartées ; après
bissection, le parent direct de chaque première révision rouge est aussi rejoué.
Les absences de méthode, sauts et erreurs de chargement restent inconclusifs.
Les incidents déjà rouges au témoin 339 déclenchent une recherche en amont
sur les parents directs, jusqu'à une borne verte ou inexploitable.

Un essai du lanceur a reproduit l'échec de
`PersonnagesTests.test_portrait_connu_sans_personnage_accessible_ni_fuite_a_distance`
sur `7eb45ff9` : absence du refus `ErreurMonde` attendu. Ce résultat ne suffit
pas encore à qualifier l'attente ou à désigner une fusion.

Bruts et copie du lanceur :
`C:/Users/msics/donjon/artifacts/suite-rouge-356/`.
Fichier de fin attendu : `fin-complements.json` ; les résultats sont persistés
par fichier dans `attributions/` et par révision dans `rejeux/`.
Le lanceur vivant est conservé dans `artifacts/suite-rouge-356/bissection.py`
du worktree ; le dernier lanceur est `continuation.py`, décrit dans `lancement-complements.json`.

**Défaut du premier lanceur.** `fin-bissection.json` signalait seulement la
fin des rejeux, pas une attribution aboutie. L'ajout de `tools/` avant le
chargement du namespace `tests` faisait masquer celui-ci par `tools/tests.py` :
154 incidents restaient inexploitables. Les traces correspondantes sont
conservées dans `rejeux-invalides-import/`, sans valeur d'attribution.
Le lanceur suit désormais le même ordre d'import que `tools/tests.py` ;
un rejeu d'audience a chargé les sept méthodes sélectionnées et reproduit
les neuf incidents attendus. Une erreur d'encodage de l'impression console
du smoke-test est survenue après l'écriture complète de son JSON UTF-8.

**Première adaptation prouvée.** La gravure de
`test_contre_revue_corrige_deux_effets_omis_avant_affichage_et_sauvegarde`
est verte sur le parent direct `dc6da621`, rouge à la fusion U-C `37dccfa3`.
Le harnais fournit désormais `tenter` avant de quitter ; aucune assertion,
réponse de modèle simulée ou donnée de monde n'a changé. Le même parcours
contrôle toujours la contre-revue, la révision sauvegardée, le résultat vu et
la description de la marque après chargement ; le chant du même test reste
couvert. Le fichier entier passe : **14 tests**, **4,776 s**, zéro incident
(`artifacts/suite-rouge-356/improvisation-adaptee.json` du worktree).

**Reprise après v2.** Les 161 incidents ont un résultat de rejeu ; 148 ont une
bascule verte/rouge prouvée sur parent direct, en 12 653,186 s. Répartition :
U-C `37dccfa3` 61 ; G5 `49608db0` 34 ; ouï-dire `c9b972b7` 28 ; G16 `17212940`
15 ; mandat joueur `f091c64b` 4 ; G6 `64130fa1` 2 ; demander cause `8d439542`
2 ; reprise de demande `6be4bace` 1 ; G7 `d20fce9b` 1. Une bascule rouge
n'est pas en elle-même une preuve d'attente périmée : cette qualification
demande encore le rapport de conception et l'examen de la trace.

Les treize autres incidents : neuf sous-cas MiMo sautés faute de `jsonschema`,
deux imports invalides du premier lanceur dont la forme de trace n'avait pas
été invalidée par v2, et deux méthodes vertes isolément (enfermer, prêt).
Le complément conserve les preuves déjà acquises, rejoue MiMo avec les
dépendances déclarées dans `requirements-mimo.txt`, invalide les deux imports
restants et rejoue les deux derniers fichiers entiers. Dépendances installées
seulement dans `artifacts/suite-rouge-356/dependances` du worktree.

Intégration courante `origin/integration 19c9b6da` fusionnée sans rebase dans
`47769f26`, conflit documentaire seul, entrées des deux côtés conservées.
Douze autres fichiers de tests ont reçu uniquement des confirmations de saisie
ou un import du harnais existant ; aucune assertion ni réponse simulée changée.
La phase suivante valide quatorze fichiers complets (les treize adaptés et
`test_avis_joueur`, déjà adapté par G18), puis écrit `fin-complements.json`.
Elle conserve une preuve AST de toutes les assertions et les empreintes des
sources. Des attentes G16 ou de faisabilité et des régressions distinctes
peuvent rester dans ces fichiers ; aucun résultat vert n'est présumé.

À la reprise : lire `fin-complements.json`, `validation-harnais.json` et
`assertions-harnais.json`, qualifier chaque incident et compléter
l'annexe `attribution-codex-356-suite-rouge.md`, rechercher en amont les incidents
déjà rouges au témoin si la recherche automatique reste inconclusive, puis adapter exclusivement les harnais prouvés concernés
par le consentement, sans modifier leurs assertions. Rejouer les fichiers
adaptés sur l'intégration courante, mettre à jour ce rapport et pousser la
branche. Les régressions du moteur restent pour des lots séparés.
