# Lot 303 — rejoindre un participant de lieu inconnu avant le geste

29 octobre 2026. Branche **`codex-service-rejoindre`, non fusionnée**, base
intégration **`79beaf1`**. Aucun MJ, scénario ni modèle modifié ; ni Luna,
ni suite complète. Un seul travailleur réduit pour les vérifications.

**Invariant et code.** Inconnu ne signifie pas absent : le but reste possible,
mais sa présence se prépare par `_chercher` (inspection, appel ou question).
La normalisation et `_pulsion` lisent les participants de `pnj._a_reunir`,
venues convenues comprises ; `_couper` empêche d'exécuter le suffixe supposé.
`_mesurer_direct` exige la présence projetée ; `pnj.refus_etape` revalide les
anciens plans (« participant à localiser »). La charge garde son parent
pendant le contact, même si son moyen matériel change : sur la capture,
`marmite_1` est vide mais `marmite_1_1` est portée. Aucun délai, registre
d'échec ni champ de sauvegarde ajouté.

**Cinq nouvelles preuves.** Capture exacte 289 retrouvée dans les archives
273 (seuls ses deux champs expérimentaux retirés), Mathe/Lucien à la mine,
plan indépendant des positions cachées dans toutes les salles, devis pur,
suffixe non publié, venue convenue. Les deux chaînes contrôlent parent,
contact, service réussi, portions et chronique ; monde/rendu/scène/textes
identiques après recharge et six minutes entières ou découpées.

**Tests : 53/53 verts, neuf fichiers, 509,704 s**, zéro échec, erreur ou
ignoré (`tests-cibles.json`). Contre-épreuves 251 pour un lieu cru connu
inchangées ; premières passes incluses dans ces 53 tests distincts.

**Banc achevé, code 0.** Douze paires de quatre heures, auberge/mine/Relais
× 1985/7/42/2024, départ tiré, `79beaf1` puis `066c12d` (moteur `7937fdd`).
Douze références absentes calculées et rangées une fois, puis douze nuits de
branche ; un travailleur réduit, 1 424,115 s de nuits cumulées. Aucun plantage
ni usurpation ; **suspects 219 : 0 → 0 dans chacune des douze nuits**.
Six chroniques identiques ; les autres changent avec la préparation du contact.

| Compteur sur les douze nuits | Référence | Branche |
|---|---:|---:|
| Portions servies | 33 | 30 |
| Appels nommés | 34 | 43 |
| Questions de localisation | 50 | 88 |
| Recherches du planificateur / neuves | 13 979 / 5 194 | 14 897 / 5 786 |
| Avis à expliquer / dérives ouvertes | 9 / 162 | 11 / 186 |

Les recherches comptent les calculs de plans, pas chaque inspection physique.
Portions par scénario : auberge **11 → 11**, mine **17 → 16**, Relais
**5 → 3**. Aucun gain général de services ou de coût revendiqué. Relais 7
ajoute aussi un constat `but_hors_besoin` (Gorm auprès d'Aubin alors que
pressent ses biens) ; il n'est pas certifié bénin.

**Alertes instruites, oracle inchangé.** `fin.json` conserve **`ok=false`** :
les seuils `repetition` et `appels_nombreux` signalent onze appels de Lucien
à Hugues (auberge 2024). Une seule nuit de branche sous sonde vérifie chaque rappel : salle
commune, indice de localisation à **79000** avant rappel **140869** ;
cuisine, contact à **136318** avant rappel **141120** ; grenier, nouveau
bruit à **142155** avant rappel **142200** (instants en dixièmes). Aucun
appel dans un lieu encore vain ni rappel par le seul temps : aucune boucle
nouvelle établie par ces seuils. Chronique,
récit, souvenirs, mesures et empreinte de l'état final sont identiques au
banc original (`analyse-alertes.json`, script et journal). Aucune
référence ni autre nuit relancée. **Bilan retenu `fin-cloture.json`,
`ok=true`**, distinct du bilan brut conservé. Aucun calcul actif ; branche
poussée, non fusionnée. Bruts : `C:/Users/msics/donjon/artifacts/service-303/`.

**Limites.** Rencontre et accord restent incertains ; une croyance périmée
peut faire échouer une question (Hugues dans la capture). Les preuves excluent
le service exécuté en échec, pas tout refus préparatoire. Avis/dérives
supplémentaires non certifiés bénins ; aucune garantie universelle contre
les boucles. L'exécution et le rendu constatent encore le monde réel.
