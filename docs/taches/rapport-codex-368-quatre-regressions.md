# Lot 368 — quatre régressions isolées

30 octobre 2026, PC fixe `msi-desktop`. Branche `codex-quatre-regressions`,
base **`origin/integration dea991a5`**, livraison non fusionnée, poussée vers origin.

**Trois chemins déjà verts après le 360.** Les méthodes réservées du prêt
(333), de l'enfermement (332) et de l'installation (313) passent isolément et
dans leurs fichiers entiers, sans modification. L'ablation du seul filtre
`social._initial` reproduit exactement les trois anciennes assertions rouges.
Le contrat décidé et corrigé par le [360](rapport-codex-360-regressions-337.md)
est donc une différence causale : un savoir initial inchangé n'est pas une
nouvelle à confier. Aucun de ces trois résultats n'est crédité à un nouveau
correctif moteur du 368.

| Origine ; invariant contrôlé | Constat matériel, avec puis sans le filtre du 360 |
| --- | --- |
| 333 ; le rappel porte sur un bien encore emprunté, utile à son détenteur | À trois minutes, Rémy porte la lampe et répond `necessaire`. Avec l'ablation, il l'a déjà rendue à Gaspard et se trouve à la réserve : `absent` décrit le bien absent de ses mains, pas une portée de parole insuffisante. |
| 332 ; seule une perception effective établit un témoin | Au verrouillage, à 835 dixièmes, Gaspard perçoit le joueur depuis `[5, 0]` ; souvenir et méfiance persistent. Avec l'ablation, il est en `[4, 2]`, tourné au sud-ouest, sans perception du joueur : aucune connaissance n'est fabriquée. |
| 313 ; le plan initial ne prouve pas la conduite finale | La porte reste intacte dans le parcours actuel. Avec l'ablation, **Brune** commence les coups à 324 dixièmes ; Gorm a quitté les vannes. L'auteur est établi, sans attribuer le bris au seul plan initial de demande. |

**330 ; une flamme encore utile reste allumée.** Le quatrième rouge est
reproduit : à quatre minutes Rémy reste au baraquement, sa lumière lui est
utile. Le [330](rapport-codex-330-demander-cause.md) change explicitement le
secours : question, réponse, puis replanification ; l'ancien trajet vers un
abri ne constitue plus une prémisse. Le portage suit la scène déjà documentée
au [342](rapport-codex-342-attribution-groupe1.md) pour la lampe chargée : après
trois minutes de remplissage/allumage autonomes, placement d'auteur devant une
source fixe de niveau 2 au bureau, orientation et perception réelles, puis une
minute vécue. Le moteur décide seul l'extinction. Les **12 assertions d'origine
sont conservées exactement**, combustible **> 115**, charge d'huile, ordre des
trois gestes, lumière crue et état rechargé compris ; six assertions ajoutées.
Le total reste quatre minutes de jeu. Aucun changement du code du jeu.

**Validation.** Première passe : 43 tests, un seul échec (lampe vide), zéro
erreur/saut. Reprise ciblée de la lampe portée verte. Validation consolidée :
**77 tests distincts / huit fichiers verts** (les trois premiers fichiers
initiaux inchangés, puis lumière, faits initiaux, attention conjointe,
interposition et contact : 47 tests en 216,811 s).
Sept parcours réels ou analogues sont en outre rejoués en laps entier et
découpé : **19 comparaisons vertes** du monde complet, du rendu et de la scène après
rechargement ; ils couvrent prêt puis restitution, capture et secours, Brune et
Aubin devant l'installation, lampe déjà chargée. La lampe vide compare aussi
trois minutes contre trois fois une minute, puis 600 contre 13/47/540 dixièmes.

**Limites et recouvrements.** Ces preuves ne garantissent pas toute trajectoire
sociale ni un trajet autonome de Rémy au bureau en quatre minutes. L'ablation
est un diagnostic sur copies, jamais une configuration de jeu. Seul
`tests/test_lumiere.py` change hors documentation ; aucun fichier moteur commun
avec 364–367, `docs/etat-dev.md` partagé. Pas de banc d'empreintes, conditionné
par le brief à un changement du jeu ; ni suite complète ni Luna. Deux calculs
réduits au plus. Bruts, scripts, contrôle AST et résultats consolidés :
`C:/Users/msics/donjon/artifacts/quatre-regressions-368/`, fin `fin.json`.
