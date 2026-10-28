# Lot 201 (196 a) — battants brisés et garde de son propre plan

Branche `codex-reserve-brisee`, non fusionnée ; base exacte `fffa3a2` vérifiée.
Aucun Luna. Deux travailleurs réduits au plus. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/reserve-201/`. Aucune clé Git de signature configurée.

**Invariant.** Une installation crue détruite ne demande plus de remise sous clé.
`portes.refermable` juge cette capacité à partir de la fin observée, crue ou simulée :
`deliberation.satisfaite`, `planification._pulsion`, `gestes`, `retablir` et la fuite
emploient ce même critère. La fermeture réelle le vérifie avant le geste. La fin des
battants entre dans `_entrees_communes` ; les fins des autres objets gardent leur
contrat antérieur. Une effraction simulée porte aussi sa destruction jusqu'à la
restauration. `esprits.constater` dément le verrou sur ouverture/destruction pour
tous les acteurs ; l'essai conserve les informations de contenu et les actualise
seulement si le contenu est visible. `retabli_par_son_plan` protège les préconditions
des autres buts sans jamais exclure sa propre pulsion. Aucun délai ni exception de
personnage, objet ou scénario.

**Diagnostic réel corrigé.** Les trois graines ont été rejouées avant modification.
Sur cette base, contrairement au départ 199, la réserve reste intacte en crue 7 et
42 (6 et 3 suspects). En 2024, Brune la force à 45 min, Gorm la constate détruite à
49 min ; 253 suspects, dont 251 retours de la boucle réserve/garde. Les captures et
les différences de croyances prouvent la fermeture impossible et la disparition/
réapparition de `vide` entre essai et vue. La perception générale démentait déjà le
verrou : c'est le constat direct qui n'assurait pas ce contrat. L'auto-exclusion
reste présente dans le code et est éprouvée séparément sur une garde pressante
intacte ; elle n'est pas nécessaire aux fermetures refusées observées en 2024.
Les minutes et les 385 suspects du lot 199 ne décrivent plus cette base après les
fusions intermédiaires. Aucun brut 196/199 disponible sur ce poste ; référence
exacte calculée une fois par le comparateur, puis conservée dans le dossier du lot.

**Validation partielle.** 22 tests ciblés verts : cas réel 2024, autre contenant de la mine,
joueur/PNJ, essai/vue, ignorance du contenu, croyance sans oracle, clé de recherche,
restauration après effraction simulée, garde propre et d'un autre but, battant
intact encore verrouillable, laps entier/découpé, état et rendu après recharge.
Les huit nouveaux tests sont repris verts avec leurs assertions finales de texte
public. Reprise de la capture réelle de base à 45 min : six sauvegardes/recharges,
état et rendu identiques, aucune reprise de fermeture.
Captures base avant/après les créneaux annoncés pour 7/42 et juste avant/après
l'effraction réelle 2024 (45 min, intégrité 2 → 0). Contrôle crue 7, 2 h,
`VERIFIER` + `spatial.VERIFICATION=0,2` : zéro écart, borne ou plantage (128,7 s).

Vingt paires de 4 h, compteur 199 actif ; suspects référence exacte → branche :

| Relais | Mine | Auberge | Crue | Hameau |
|---:|---:|---:|---:|---:|
| 1 → 1 | 1 → 1 | 2 → 2 | **271 → 19** | **16 → 17** |

Crue 2024 : **253 → 1**, disparition de la boucle réserve/garde ; Gorm conserve
notamment la garde de l'antichambre. Aucun plantage ni usurpation signalé.
Total suspects **291 → 40**, entrées changées à expliquer **428 → 301**,
cycles accomplis **617 → 620**. Hameau 7 : **5 → 6**, retours abri/attente/ronde
d'Aubin, Ilse et Gorm ; **critère « aucun scénario ne monte » non atteint**.
Trois contre-épreuves sur cette seule nuit (ancienne garde du plan, anciens
constats, puis retrait de la fin simulée, séparément) gardent six suspects :
elles n'établissent pas une attribution causale unique. Pas de nouvelle famille
de boucle de fermeture ; aucune garantie sur les retours d'abri. Nouvelle
observation `fige_presse` de Gorm en crue 2024 : 125 min sans but, devoir pressant
avec cause `confiee`, et non une alternance de fermeture. Ces limites restent
visibles dans le compteur, sans correction du détecteur ni exception moteur.

Suite complète unique : **2 385 tests, 276 fichiers, 1 803,701 s, trois échecs,
zéro erreur**. Les deux incidents MiMo `6 != 5` et le contrôle AST des accès aux agendas (deux lectures du détecteur 199,
inchangé) sont reproduits par trois tests ciblés sur les sources exactes de
`fffa3a2`, zéro erreur ; bruts `incidents-base.json`.

**Limites.** Ce lot ne certifie pas l'absence générale de changements d'avis : les
autres familles de retours, notamment eau/abri et engagement, restent aux lots
196 b/c. Une destruction distante non constatée n'est pas devinée. Un essai dans
le noir ne donne aucune preuve nouvelle du contenu. Aucun gain de temps revendiqué.
