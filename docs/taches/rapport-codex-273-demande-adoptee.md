# Lot 273 — demande adoptée et moyen démenti

29 octobre 2026. **`codex-demande-adoptee`, non fusionnée**, base `c9459ce`,
moteur **`4047c16`**. **Deux critères non tenus : fusion à différer.**

**Changement.** `poursuites.py`, `esprits.py` et `deliberation.py` font suivre
à la demande conservée les fournitures reçues, par provenance publiée
transitive, sans perdre but, début ou palier. Aucune équivalence par simple
raison ni substitution pour une mission d'objet précis. Sans plan admissible,
la demande dort et libère son palier ; elle se réveille sur croyance/moyen
nouveau, jamais par délai. Les plans vides valides restent actifs.
Aucun cas par PNJ/objet/scénario, ni modification d'agendas/échanges/signes.

**Tests.** 16 cas ciblés verts ; **449 compléments : 444 succès, cinq échecs**.
Rejeu inchangé sur `9a1ba3e` isolé : deux écarts hérités de `pas_compagnons`
(ordre de vente, lieu cru au service), trois nouveaux. Brune n'a plus le
retour daté 929 ; Lucien trouve Anselme à 115 min avant recherche épuisée.
**Défaut réel Tilo : service admis avec bénéficiaire de lieu inconnu, puis
rejeté dans une autre salle.** La même capture sur le parent expose la même
lacune commune de présence. Aucun oracle affaibli ; preuves rechargées et
correction proposée au [bilan détaillé](bilan-codex-273-correction.md).

**Banc.** Vingt nuits de branche seules, cinq scénarios × quatre graines ×
4 h ; référence **`0e3e626` relue**, sonde 265/271, compteur 219, `cats` 183.
Passe de **2 126,692 s**, priorité réduite, zéro plantage/usurpation.
Ni Luna ni suite complète ; moteur et tests inchangés pour ce bilan.

**Suspects : critère non tenu**, 19/20 nuits sans hausse, total **1→3**.
Aubin Relais 2024 reste corrigé ; Crue 42 fait **0→3** : interpositions de
Gorm, retours 32490/33234/33255, répétitions sans entrée nouvelle,
sans preuve permettant de les excuser.

| Moyenne sur quatre nuits | S réf→corr. | F réf→corr. | D réf→corr. |
|---|---:|---:|---:|
| Relais | 15,25→14 | 4,25→4,5 | 1,750→1,750 |
| Mine | **25,75→16** | **5→4,5** | **1,964→1,679** |
| Auberge | 9,25→14,75 | 4→4,25 | 1,000→1,156 |
| Crue | 23,5→21,5 | 6,75→7,5 | 3,063→3,250 |
| Hameau | 22,75→22 | 7,25→7,25 | 2,167→2,125 |

**Mine : critère non tenu.** S reste sous l'étendue de référence **19–32**,
F sous **5** ; D seul revient dans son étendue. S par graine :
**32→16 / 19→16 / 24→19 / 28→13**. **60 signatures perdues, 21 gagnées** ;
repas **19→19**, crédits **8→9**, Odon nourri dès la minute zéro par Josse.
Le cas 373 s'améliore ; **la perte restante n'est pas prouvée légitime**.

**Autres signaux.** À expliquer **21→35** (hausses Relais 1985, Auberge 1985,
Crue 1985/42, Hameau 2024) ; une observation `voir_alterne` au Relais 2024.
Dérives ouvertes **203→172**, minutes urgentes en attente **695→1060**.
Le sommeil fonctionne localement chez Anselme, mais n'explique pas toutes
les dérives de Gorm : **62→88→77** (référence / avant correction / correction).
Une garde vide valide ou une vente ne prouve pas un épuisement.

**Suite avant fusion.** Contrat commun de présence, prémisses stables des
tests, trois suspects et recul restant de la mine. Diagnostics et bruts :
`C:/Users/msics/donjon/artifacts/demande-273-sol/correction/instruction/`.
**`correction/fin.json : ok=false` ; aucun calcul actif.** Le
[diagnostic initial](diagnostic-codex-273-richesse-alertes.md) reste historique.
