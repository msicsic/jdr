# Lot 332 — Attention conjointe

Lot terminé, branche `codex-attention-conjointe`, **non fusionnée**, base `integration 7e65907`.
29 octobre 2026. Ni Luna, ni suite complète, ni modification de scénario.

**Invariant et fonctions.** `signes` projette la direction réellement perçue sans
sa cible inaccessible, même dans une impression historique. Un PNJ disponible
peut suivre le regard d'une personne fiable ou familière ; `pnj.agir` tourne avec
`spatial.QUART * quarts`, puis seule sa propre perception révise ses croyances.
La direction choisie persiste dans l'attitude : le tiers caché ne la déplace pas.
Les épisodes physiques et `esprits.regards_suivis` dédupliquent sans échéance,
après recharge aussi. Perdre puis retrouver la vue ne renouvelle pas l'émission.
L'ordonnanceur accepte aussi un PNJ sans intention ; guet et gestes engagés gardent
leur priorité. Aucun accès nouveau dans la recherche : `_entrees` inchangé.
Recouvrement possible 330 : **`esprits.py`, `pnj.py`, `signes.py`**.

**Tests ciblés : 94 tests distincts verts, huit fichiers**, deux travailleurs
réduits au plus. Neuf nouveaux tests : Relais/auberge, vrais coups de la rixe
(Brune/Aubin, Ilse suit), cas négatifs, obstacle, cible partie, non-répétition,
nouvelle direction et impression historique. Monde/rendu/scène rechargés ; deux
scénarios sur huit secondes, entières ou découpées : états et projections identiques.
Échecs initiaux de prémisses conservés ; aucun oracle existant affaibli.
Dernière reprise : neuf tests, 8,319 s ; autres fichiers verts non relancés.

**Banc terminé : vingt paires de nuits de 4 h**, cinq scénarios × 1985/7/42/2024,
deux travailleurs réduits, référence puis branche. Vingt références 7e65907 absentes
calculées une fois et mises en cache. Moteur/tests `0b60a91` inchangés ; `fbd234b`
documentaire seulement. Sonde 219 de l'intégration (`101c6af25b`). **Critère tenu sur
20/20 nuits : suspects 0 → 0, aucun plantage ni usurpation des deux côtés.**

| Scénario | Regards suivis | Rotation (s de jeu) | CPU branche moyen/nuit (s) |
|---|---:|---:|---:|
| Relais | 0 | 0 | 30,582 |
| Mine | 36 | 31,5 | 52,121 |
| Auberge | 19 | 13,5 | 52,719 |
| Crue | 14 | 17 | 81,953 |
| Hameau | 64 | 56 | 236,895 |

**133 signaux suivis, 118 s de rotation** ; un suivi déjà aligné peut coûter zéro.
CPU branche total **1 817,078 s** ; Hameau 1985 atteint 512,906 s. Signes perçus :
638 795 appels, **104,766 s** inclusives ; choix d'attention : 258 421 appels,
**9,281 s** inclusives. Ces deux durées se recouvrent et ne s'additionnent pas.
CPU avec sondes, sans comparaison de vitesse ni estimation causale du surcoût.
Durée totale détachée, référence comprise : **2 113,492 s**.

**Autres observations conservées :** cycles accomplis 462 → 453, entrées à expliquer
32 → 35, dérives ouvertes 387 → 329, bascules 0 → 0, avertissements redits 7 → 6,
appels à l'aide 8 → 8. Nouvelles alertes Hameau 42 : Brune et Ilse, chacune 100 min
dans le noir au beffroi sous proximité d'un proche ; Aubin, 105 min sans but.
Hameau 2024 : une alternance « aller voir / autre but » de Maël, sans preuve de retour
au même bruit. Ces observations restent à examiner à l'intégration ; le zéro
suspect certifié ne les déclare ni corrigées ni légitimes.

**Clôture du lanceur.** `validation.json` était vert, mais `fin.json` initial est
en échec : variable `avant` écrasée par un compteur après les vingt nuits. Correction
du lanceur uniquement ; les quarante archives réelles sont revalidées, puis son
chemin de clôture corrigé est rejoué sur ces archives, sans moteur ni nuit rejouée.
Validation identique, code 0 ; **`fin-cloture.json ok=true`**. Échec initial conservé.
Aucun calcul actif, aucune relance de tests.

**Limites.** Le joueur voit la direction mais la suit manuellement : aucune
rotation automatique. Une direction parallèle ne garantit pas de découvrir la cible.
Les anciennes intentions sans direction gardent leur contrat jusqu'au prochain
regard décidé. Aucune garantie générale d'absence de boucle.
Bruts : `C:/Users/msics/donjon/artifacts/regard-332/` :
`comparaison.json`, `validation.json`, `analyse-cloture.json`, `relecture-lanceur/`,
tests et fichiers de fin ; branche poussée vers origin.
