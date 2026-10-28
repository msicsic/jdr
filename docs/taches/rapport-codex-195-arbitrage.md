# Lot 195 — arbitrage des attentes et richesse

28 octobre 2026. Complément au [rapport principal](rapport-codex-195-pas-compagnons.md).
Base figée `346c1aa`, moteur inchangé depuis `e7aab68`. Aucun changement de
placement social ; aucun nouveau banc nécessaire pour ces seules prémisses.
Bruts : `C:/Users/msics/donjon/artifacts/pas-195/arbitrage/`.

## Classement exhaustif des treize échecs et de l'erreur

Les scènes ci-dessous rendent explicite l'hypothèse que le test prétendait
exercer. Elles ne rétablissent aucun retournement ni preuve par accident dans
le moteur. Comparaison AST avec `e7aab68` : **les 273 appels d'assertion des
huit fichiers modifiés sont identiques**, arguments compris. Les huit fichiers
ciblés passent : **67 tests, zéro échec/erreur**, 126,648 s, deux travailleurs
à priorité réduite (`cibles.json`).

**Suite complète après arbitrage : 2 497 tests / 289 fichiers, 2 091,515 s,
cinq échecs, zéro erreur, zéro ignoré**, une seule passe après les dernières
prémisses, deux travailleurs à priorité réduite (`suite.json` et `suite.log`).
Exactement les quatre préexistants et le défaut de placement restants ; les
huit échecs de trajectoire et l'erreur ont disparu. Contrôle AST durable dans
`assertions.json` ; aucun changement du moteur depuis le banc final.

| Cas initial | Classement et traitement |
|---|---|
| `test_attente…test_sans_rien_qui_l_interrompe_le_meme_monde_qu_un_bloc` | Prémisse de silence implicite : un dialogue réel interrompt désormais l'attente. Corps calmes et aucun agenda personnel dans les deux variantes ; mêmes assertions sur 5 minutes, texte et égalité des mondes. |
| `test_caractere…test_memes_moyens_valeurs_differentes` | Rencontre auparavant dépendante d'une localisation fortuite : Gorm est vu à une case précise et reste occupé deux minutes à son poste. La comparaison des valeurs, des demandes et de l'issue alimentaire reste entière. |
| `test_proposer_recours…test_mine_odon_paie_la_contre_offre_apres_refus_et_mathe_livre` | Le repas est payé/livré, puis une autre offre financière réelle intervient. La scène borne maintenant les connaissances d'Odon : ses propres cinq pièces sont connues, pas les encaisses des autres. Les assertions de négociation, paiement et livraison restent entières. |
| `test_relations_lectures…test_l_abri_rejoint_le_plus_aime_des_proches_fiables` | Projet de dette concurrent désormais déclenché ; scène de choix d'abri avec dette personnelle nulle. Toutes les combinaisons de préférences et assertions restent exécutées. À distinguer du défaut de placement ci-dessous. |
| `test_ressources…test_on_monte_se_chauffer_au_poele_du_guet_et_le_bois_reste_compte` | Une charge réelle de combustible est achetée/consommée quand le poêle est mieux perçu. L'expérience de consommation à stock fixe commence désormais avec les quatre corps rassasiés et réchauffés. Stocks, extinction et refus de bois fictif restent contrôlés. |
| `test_temps_reel…test_cas_reel_brune_renonce_apres_trente_minutes_de_guet` | Gorm fournit effectivement un repas avant le renoncement attendu. La scène explicite un fournisseur sans besoin déclencheur et l'absence de dette concurrente de Brune ; même seuil de patience et même issue exigés. |
| `test_temps_reel…test_la_patience_ne_depend_pas_du_decoupage` (erreur) | Même scène : l'égalité des états passait, puis l'intention déjà résolue était indexée. Même préparation commune, aucune garde ajoutée à l'assertion ; découpage et intention sont contrôlés comme avant. |
| `test_verifier_eau…test_on_ne_descend_pas_ou_l_eau_va_noyer_et_on_ne_s_y_chauffe_pas` | Ilse a déjà évacué au poêle haut, le trajet attendu n'a donc plus lieu d'être. Départ du recours positif placé explicitement à l'antichambre après observation de la crue ; interdictions de descente et trajet sûr inchangés. |
| `test_signalements…test_mireille_auberge_11_travail_confie` | La croyance fraîche constate réellement le feu suffisant ; l'ancien test dépendait d'une vue périmée. Fourneau réellement faible et Joss déjà occupé pour les dix minutes observées ; mêmes assertions de cause, pureté de lecture et égalité après découpage. |
| `test_securite…test_inquiete_dans_le_noir_elle_rejoint_la_lumiere_et_la_compagnie` | **Défaut du jeu, laissé rouge.** Attitude de placement périmée qui bloque un recours d'abri ; ni scène ni assertion modifiées. Lot séparé décrit ci-dessous. |
| `test_constater_rumeurs…test_le_joueur_qui_ne_les_connait_pas_n_entend_que_des_voix` | **Préexistant, laissé rouge.** Mathurine intervient réellement dans l'échange ; les voix restent anonymes. Le test attend exactement deux voix. Première apparition vérifiée : fusion du **221**, `d7dbf1a`. |
| `test_detecter_changements_avis…test_torche_hameau_1985_service_perdu` | **Préexistant, laissé rouge.** Attente historique d'une perte de service qui n'arrive plus. Première apparition : fusion **224**, `346c1aa`, par interaction avec 221, pas sur la branche 224 seule. Ne pas fabriquer une extinction pour satisfaire cet oracle. |
| `test_fournisseurs_jeu…test_mimo_correction_avant_action_sur_deux_scenes` (atelier/MiMo, 6 au lieu de 5) | **Préexistant, laissé rouge**, déjà reproduit sur `bd45f65` lors du lot 224 ; hors de l'ouïe et de la preuve d'engagement. |
| `test_restes_fusions…test_mimo_rejets_et_actions_sur_deux_scenes_apres_reprise` (MiMo, 6 au lieu de 5) | Même défaut préexistant de décompte, laissé rouge ; aucune assertion ajustée. |

### Contrôle historique indépendant

`origines.py` extrait chaque source exacte par `git archive` dans les bruts,
sans changer le worktree, puis exécute les **deux tests originaux inchangés** :

| Source | Troisième voix | Ancienne perte de torche |
|---|---|---|
| `bd45f65` (213) | vert | vert |
| `a12a418` (fusion 223) | vert | vert |
| `d7dbf1a` (fusion 221) | rouge | vert |
| `0ae525f` (branche 224, sans 221) | vert | vert |
| `346c1aa` (fusion 224 après 221) | rouge | rouge |

Le test des voix est inchangé entre `a12a418` et `d7dbf1a`, celui de la torche
entre `d7dbf1a` et `346c1aa`. La sonde du compteur et l'exécution sans sonde
produisent les mêmes états, mémoires, rendu, chronique et mesures sur la base
comme sur le candidat (`extension-346/torche-*`). Ce n'est pas un effet de sonde.

## Lot de placement à créer, sans application dans 195

Cas reproductible : `test_securite.AbriTests.test_inquiete_dans_le_noir_elle_rejoint_la_lumiere_et_la_compagnie`.
Ilse finit en `[2,1]`, Aubin en `[1,5]`, Gorm en `[4,5]`. La croyance du lieu
de Gorm est devenue nulle, mais l'intention conserve `attitude.place` proche de
Gorm. **`signes.place`** n'efface cette attitude que dans certaines sorties ;
des liens sociaux encore présents permettent de sortir sans la renouveler.
**`pnj.agir`** saute alors `_rejoindre_un_proche` dès que cette attitude existe,
même si aucun pas social valable n'a été produit.

Contrat proposé : une attitude de placement ne bloque un autre recours que si
elle correspond encore à un choix de placement réalisable avec les croyances
actuelles ; invalider explicitement les décisions périmées, sans lire la position
réelle de la cible et sans ajouter de retour au choix. Valider le cas réel,
une autre cible perdue, les préférences entre proches, le rendu et la recharge.
Le prototype en mémoire qui effaçait simplement l'attitude au début du jugement
ne suffit **pas** : 21 tests de signes passent, mais Ilse choisit Brune et
l'ancienne assertion sur Aubin reste rouge. Il faut arbitrer l'invariant et
l'oracle du choix social dans ce lot séparé. Aucun patch de ce prototype appliqué.

## Hameau : une baisse réelle des interactions, pas un artefact de comptage

Relecture des vingt nuits déjà mesurées, définition exacte du lot 183 : une
signature S est `(famille, acteur, texte exact)`, dédoublonnée dans la nuit.
**Ni bruit inconnu ni retournement ne sont une famille de S.** Sur les quatre
graines, S total passe de **162 à 108**, soit **40,5 à 27** en moyenne.

| Famille | Signatures référence → candidat | Écart |
|---|---:|---:|
| Demandes | 70→42 | −28 |
| Offres | 36→26 | −10 |
| Promesses de contrepartie | 14→4 | −10 |
| Travail payé | 14→11 | −3 |
| Appels | 9→6 | −3 |
| Services reconnus | 5→2 | −3 |
| Disputes | 2→0 | −2 |
| Avis | 6→11 | +5 |
| Délégations / interpositions | 3/3→3/3 | 0 |

Le banc du lot (ouïe et preuve dans `tenu` ensemble) change réellement les
rencontres, les croyances et les interactions qui en découlent. Il n'isole pas
la contribution causale de chaque fonction à chaque échange. Ce n'est pas seulement
du bruit narratif retiré : les mesures d'échanges passent de **328 à 210**,
les propositions de **51 à 31**, les acceptées de **16 à 9**, les prêts/rendus
de **1/1 à 0/0**, les tâches faites de **4 à 2**. Inversement les occurrences
de travail payé passent de **20 à 26** : moins de signatures ne signifie pas
partout moins d'activité. Plusieurs disparitions sont des offres impossibles
ou refusées, mais cela n'explique pas toutes les pertes acceptées.

Exemples traçables dans `richesse-hameau.json` : disputes d'Aubin envers Gorm
et Sève (1985, minutes 207/220), reconnaissances de Brune envers Maël (1985,
minute 4), envers Gorm (7, minute 8 ; 42, minute 81 ; 2024, minute 5), offres
de travail de Gorm refusées/impossibles envers Maël et Sève. Les différences
de signatures et les gains sont conservés intégralement dans les bruts.
Parmi les interactions acceptées disparues : Aubin achète des vivres à Gorm
(1985, minutes 2/3), Brune vend la torche à Aubin (7, minute 135) ou la clé
à Aubin (42, minute 132). Des dons effectifs de nourriture de Gorm manquent
aussi (7, minute 6 ; 42, minute 81 ; 2024, minutes 2/4/5). Ce sont des
signatures absentes de la nuit candidate, pas une preuve que chaque besoin
correspondant reste insatisfait : les deux trajectoires ont aussi des gains.
**Aucune garantie de richesse inchangée : le hameau perd aussi des interactions
réelles.** Le critère demandé des répétitions suspectes reste satisfait.
