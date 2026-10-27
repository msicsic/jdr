# Rapport Codex 147 — Luna et les gestes de force

Branche `codex-force-4f-luna`, **non fusionnée**, base `cee0201` récupérée par
avance rapide depuis `integration`. `main` et les fichiers réservés au lot 146
intacts. Python et coffre du dépôt principal ; parties exclusivement sur copies.
Aucune clé Git de signature configurée : commits non signés.

**Contrat.** `consignes.INTERPRETATION` décrit saisir, ligoter, délier, se libérer,
traîner, tuer et verrouiller, par la voie typée existante, fiche avant tentative.
Enfermer se compose par la porte réelle ; aucun état de captivité inventé.
`ACTIONS` alimentait déjà le schéma ; aucun nouveau mode, scénario ou mot-clé de
correction. L'audit commun classe explicitement l'état corporel comme mécanique.
`dialogues.interlocuteurs` filtrait déjà morts et inconscients ;
`narration.consigner` recalcule les locuteurs audibles avant toute écriture.

Le faux refus de traîner révèle un dossier incomplet : le titre indiquait le
sens du pas mais pas le lieu rejoint par le corps. **Seule exception au périmètre
des gestes : `tenir.preparer` ajoute cette conséquence à `plan.information`**, lu
par la fiche et la contre-revue. Le corps rejoint la case de départ de l'auteur,
dans son lieu actuel ; aucun nom de destination inconnue divulgué, aucune règle
de déplacement changée. Deux seuils réels, dont le cas Luna, sont rejoués et
rechargés. `banc_parties` accepte désormais le scénario existant `rixe`.

**Vérifications.** Console avec MJ simulé : les sept gestes nouveaux, Brune et
Aubin ; traînage au Relais et à l'auberge, verrouillage du bureau et de la réserve.
État et rendu relus après sauvegarde ; mort et évanouissement inventés absents de
l'affichage, liens et blessures sans fondement refusés. Paroles refusées pour
deux morts ou inconscients, même avec un audit antérieur favorable.
Les 70 tests existants ciblés sont verts ; six nouveaux tests verts, dont la
reprise finale **16 tests, 17,78 s** avec les dix tests de traînage. Les premières
reprises ont corrigé des erreurs de fixtures (caractéristique hors borne, lien
déplacé par un geste interdit), sans assouplir le moteur.
Suite complète unique : **2 154 tests, 241 fichiers, 1 205,71 s, deux échecs
MiMo historiques `6 != 5`, aucune erreur ni test ignoré**. Leur reproduction sur
les bases intactes est déjà documentée dans les rapports 142/145 ; pas de rejeu.
La suite a été lancée avant le complément de destination, vérifié par les
16 ciblés finaux ; aucune seconde suite complète.
Empreintes 2 h, Relais/rixe/mine/auberge × quatre graines : **16/16 identiques**
à `2d504ae` (même code du jeu que `cee0201`), chronique, mesures et état complet.
Les seize références manquantes ont été jouées une fois puis cachées ; branche
jouée ensuite, sans comparaison de temps. Aucun plantage ni divergence.

**Luna, une passe.** Six `force-4f-*` et les cinq 4b/4c, `gpt-6-luna`, une
exécution à la fois, priorité réduite : **49 appels, 19 tours MJ, 2,58 appels/tour,
9,13 s/tour** (173,46 s d'appels). Huit saisies sur onze typées en deux appels ;
les récits après « tenter » comptent séparément (deux à quatre appels).
Zéro repli, incident technique, erreur de recharge ou nouvel état corporel
inventé constaté. « Je l'achève » devient `tuer`, mort seulement après tentative ;
ligotage et question d'assommement donnent leur fiche puis leur issue.
Le premier banc enfermer n'avait fait aucun appel (porte fermée, Bram non vu) :
la scène corrigée, porte ouverte, est la seule passée à Luna pour cette demande.

**Limites : critère des trois appels non atteint.** Geste improvisé : `tuer`
refusé sur une personne capable de se défendre, quatre appels ; refus moteur
valide pour ce typage, sans preuve que l'intention excluait un simple coup.
Traîner : cinq appels, action correcte rejetée par la contre-revue ; explication
finale erronée sur la portée et l'obstacle. Enfermer : quatre appels, faux refus
malgré porte et clé accessibles ; Luna confond aussi porte du bureau et meuble.
L'ajout de destination et la précision de sa description après la passe sont
testés par le moteur, **pas revalidés par Luna**.
La classification corporelle reste sémantique ; les tests simulés ne prouvent
pas la détection de toute paraphrase. Aucun progrès universel ni objectif 4f
entièrement satisfait revendiqué. Temps descriptifs, sans comparaison CPU sur
ce poste partagé. La reprise ciblée finale a chevauché brièvement la suite à
deux processus ; cette reprise aurait dû attendre sa fin.

Bruts : `artifacts/force-147/` (`luna`, `luna-enfermer`, `mesures.json`, ciblés,
suite, `empreintes.json`) ; aucun rejeu de référence Luna ni seconde passe.
Livraison : branche poussée, commit non signé, aucune fusion.
