# Lot 356 — attribution de la suite rouge de `7eb45ff`

Branche `codex-suite-rouge-7eb45ff`, base `integration df03dc2f`.
**En cours : bissection corrigée détachée le 2026-10-30, `fin-bissection-v2.json` attendu.**

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
Fichier de fin attendu : `fin-bissection-v2.json` ; les résultats sont persistés
par fichier dans `attributions/` et par révision dans `rejeux/`.
Le lanceur vivant est conservé dans `artifacts/suite-rouge-356/bissection.py`
du worktree ; son chemin de dépôt est enregistré dans `lancement-v2.json`.

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

À la reprise : lire le fichier de fin, qualifier chaque incident et compléter
l'annexe `attribution-codex-356-suite-rouge.md`, rechercher en amont les incidents
déjà rouges au témoin si la recherche automatique reste inconclusive, puis adapter exclusivement les harnais prouvés concernés
par le consentement, sans modifier leurs assertions. Rejouer les fichiers
adaptés sur l'intégration courante, mettre à jour ce rapport et pousser la
branche. Les régressions du moteur restent pour des lots séparés.
