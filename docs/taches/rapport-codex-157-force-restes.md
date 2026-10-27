# Rapport Codex 157 — Restes de force 4f

Branche `codex-force-restes`, **non fusionnée**, base `af1b8f3` (brief récupéré
par avance rapide depuis `origin/integration`). `main` et les modules réservés
aux autres lots intacts. Aucune clé Git de signature configurée : commit non signé.

**Invariant et correction.** La contre-revue doit lire la même destination et
les mêmes opérations que le moteur, sous leurs désignations publiques.
`tenir.preparer` calcule le repère de destination du corps avec le trajet validé,
et reprend la conséquence dans le titre public de traînage ; la contre-revue
reçoit `Salle des vannes (crypte)`, sans identifiant technique dans la fiche
joueur. `couverture_action` nomme aussi les salles des effets et des faits des
désignations, en conservant les références de ces désignations. Son dossier de
porte associe l'objet de type porte, les lieux concernés, les personnes perçues
ou mémorisées et les issues connues avant action ; aucune recherche de position distante ni
nom de porte non désignable. Les textes littéraux restent intacts ; aucune
prédiction de captivité cumulée dans une séquence n'est ajoutée.
La consigne commune précise que le contact exigé est celui de la porte, pas
celui de la personne derrière. Aucun effet physique, mode ou règle lexicale
ajouté ; les instructions de contre-revue sont inchangées. `tuer` exigeait déjà
une cible vivante sans défense : aucune consigne supplémentaire pour le talon.

**Tests.** Sept tests force verts, dont un nouveau test porte/personne et le test
de traînage renforcé : deux seuils dont le cas réel, bureau/Bram et réserve/Rémy,
MJ simulé et console, état du monde et rendu après recharge. Le dossier ne mute
pas le monde ; un verdict conforme est admis, un verdict non conforme reste
refusé (cela ne prouve pas le jugement sémantique de Luna). 38 tests voisins
verts ; reprise finale 27 tests verte, après la correction de fermeture ci-dessous.
**Suite unique : 2 185 tests, 247 fichiers, 1 310,441 s ; deux échecs MiMo
historiques `6 != 5`, zéro erreur ni test ignoré.** Aucun rejeu de référence
pour ces échecs déjà établis sur les bases antérieures.
La suite a démarré avant le resserrement final de projection (lieux sans réécrire
les textes et issues avant action) ; reprise finale **27 tests verts, 30,972 s**.

**Luna.** Deux passes des trois restes, une passe des huit autres scripts,
`gpt-6-luna`, coffre principal, sauvegardes temporaires uniquement, deux exécutions
réduites au plus. Suite à deux processus réduits ; reprise finale à un seul
processus quand il ne restait que le dernier travailleur (total deux au plus). Les quatorze
parties correspondantes de `cdaf371` ont été relues du cache, sans rejeu ni
écriture : **60 → 60 appels / 22 tours MJ**, 2,73 appels/tour ; 8,68 → 8,13 s/tour,
charges différentes, sans gain de temps revendiqué. Zéro repli, incident technique
ou erreur de recharge. Traîner **6/4** appels (référence 5/4), enfermer **3/7**
(référence 2/3), improvisé **3/3** (référence 6/4). Achever demande quatre appels
pour sa fiche ; les autres saisies de force et récits aboutis en deux appels.

**Critère non atteint.** Traîner : la revue oppose encore la crypte au nom public
pourtant lié et juge ajouté le pas de Corvus inhérent au geste. Enfermer : Luna
vise le meuble en p1 ; en p2 elle refuse même la séquence correcte en exigeant
le déplacement de Bram, déjà dans la pièce. Elle lit aussi `ouverture=False`
comme ouvrir : correction générale finale de projection vers `fermer`/`ouvrir`,
y compris dans le dossier de porte ; effet exécutable intact. Cette dernière
correction est couverte par les tests finaux et la suite, **pas revalidée par
Luna** (aucune troisième passe). Le refus du geste improvisé repose encore sur
son interprétation mortelle et la capacité de défense ; aucun progrès général
sur ce sens n'est démontré. Aucun nouvel état corporel inventé ni parole de mort
ou d'inconscient relevé dans les fils ; le harnais ne conserve pas le monde
complet ni tous les corps, donc pas de certification exhaustive après recharge
pour Luna. La garantie générale d'absence de faux refus reste ouverte.

Bruts : `artifacts/force-157/` (lanceur, références, quatorze fils JSON/HTML,
mesures, suite). Livraison : branche seule poussée, aucune fusion.
