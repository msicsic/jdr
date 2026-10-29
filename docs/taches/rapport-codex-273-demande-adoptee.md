# Rapport 273 : un échec ancien ne clôt pas une demande adoptée

**Branche `ds-demande-adoptee`**, base `0e3e626`, moteur : `donjon/deliberation.py` seulement. Tests :
`test_contrat_engagement`, `test_dynamique_besoins`, `test_pas_compagnons`.

## Invariant

Un geste manqué dément le **moyen** employé, jamais la **demande** adoptée. `choisir` écarte le plan
périmé (`courant = {**courant, "plan": []}`), garde l'intention et laisse la revalidation existante
(`correspondants`, `_reprendre_demande`, `_fin_demande`, attente) retrouver un autre moyen, ou mettre
la demande en attente. Elle ne se clôt plus que sur une fin attestée (`_fin_demande`) ou une
préemption par un palier supérieur ; aucune exception par personnage, objet, scénario ou formulation.

Deux corrections de contrat accompagnent ce point, sans quoi la demande survivante serait close ou
préemptée par ses propres moyens :

- `_meme_demande_tenue(a, b)` : deux demandes typées désignent la même fin quand leur `raison`
  commune est identique (ou la demande entière, pour les demandes sans raison). Changer d'objet servi
  est un **nouveau moyen**, pas une nouvelle demande. Employée par `_meme_demande_adoptee`,
  `correspondants` et la boucle d'arbitrage : un autre moyen de la même demande n'est pas une
  préemption, même à palier et valeur égaux.
- La sortie `dementie` sur `manque` est supprimée du traitement ; `dernier_contrat_intention` ne
  conserve donc plus cet ancien démenti.

## Vérification

- **Capture réelle `117503` rechargée** (Aubin, Relais 2024) : avant, `choisir` sortait `dementie`
  (`intention = None`) sur le `manque` du `demander vivres` refusé `necessaire` à 195. Après, la
  demande `pulsion {objet: vivres, servir: ilse}` reste tenue, phase `continuer`, sans sortie, puis
  passe à `attendre` (plan `[]`) en cherchant un autre moyen (Gorm sollicité et refusé). Plus de
  renaissance à la seule perception d'Ilse : la demande n'a jamais cessé.
- **Seconde nature** (mine 1985, Mathe → Lucien) : l'achat de `pain_lucien` manque ; le choix suivant
  garde la même raison (`lucien/faim`) et adopte `vivres` ; le service s'achève ensuite en
  `accomplie`, sans passer par `dementie`.
- **Vraie fin** : Ilse crue morte dans la croyance d'Aubin → `dementie` (`finir`), intention close.
- **Vraie préemption** : faim propre d'Aubin à 96 → `palier` 12 → 4, sortie `palier` enregistrée avec
  la demande d'empathie abandonnée.
- **Recharges** : monde, rendu et scène identiques après sauvegarde/rechargement, et après 60 min
  jouées d'un seul tenant ou minute par minute (6 contrôles verts sur les deux cas, `verification.json`).
- **92 tests ciblés verts** (326 s) : les neuf fichiers du brief, plus `test_pas_compagnons` et
  `test_contrats_internes`, `test_deliberation_evenements`, `test_restauration_charges`.
  Deux attentes périmées réécrites : l'ancien test de contrat encodait le défaut (échec → `dementie`) ;
  l'ordre des acheteurs et le lieu du bénéficiaire de la promesse du hameau 1985 suivent le décalage
  d'une minute du monde, l'assertion de fond (service admissible, vente compensée prioritaire) tient.
- **Scène de Lucien** (`test_lucien_attend...`) : la mise en scène d'auteur est conservée et complétée
  (retour d'Anselme à l'étable à 111) ; le vol 107–110 sans témoin, la reprise du ballot, l'attente
  d'information et les croyances de Lucien sont reproduits.

## Limite déclarée, puis reprise

La première version laissait une demande tenue dont **aucun moyen n'est admissible** en attente sans
borne : elle n'immobilisait plus pour un geste, mais pouvait immobiliser un PNJ tant que sa raison
tenait (Anselme au poêle, Aubin dans l'antichambre, Bram sur `garder ses biens`, Marchand sur ses
ventes au banc). La reprise corrige ce point et le défaut de continuation lot → part.

### Cause 1 — sommeil sans moyen (prouvée sur capture rechargée)

Capture **mine 1985, minute 200**, produite avec le code `20b7601` avant correction : Remy tient
`pulsion {objet: biscuits, servir: josse}`, plan `[]`, phase `attendre`, `_reprendre_demande` renvoie
`None` ; six choix et soixante minutes plus tard, même intention, même plan vide, même phase. Après
correction, `choisir` écrit un record `demandes_sommeil` (palier 12, but et demande conservés) et
libère le palier : une autre intention (ronde) est adoptée dans le même choix, sans sortie ni
`dementie`. Six choix à la même minute laissent l'empreinte intacte ; cinq minutes de jeu aussi. Un
biscuits placé dans sa possession et cru disponible réveille la demande : même but, `depuis` 190,
palier 12, plan `servir biscuits pour josse`, record retiré, aucune sortie. Monde, rendu et scène
identiques après recharge aux deux étapes. La règle est celle du lot 213 : sommeil, palier libéré,
réveil sur croyance ou moyen nouveaux, jamais par délai. Les agendas gardent leur propre sommeil ; une
garde, un lieu, une ronde ou une mission précise gardent leur attente d'occasion.

### Cause 2 — la part reçue est un moyen de la demande (prouvée sur la capture 373)

Capture réelle de l'analyse indépendante, **mine 1985 minute 373** : Josse tient la demande
`{objet: biscuits, servir: odon}` et possède `biscuits_1`, reçu avec la provenance publiée `lot:
biscuits` (souvenir `recu` et promesse). `_meme_demande_tenue` reconnaît la part comme le même but par
sa provenance ; `_moyens_concrets` retire le lot générique quand la part est tenue ; `choisir` sert
`biscuits_1` à Odon, conserve le palier 12 et `depuis` 0, sans sortie. Le lot n'est plus redemandé.
Sur notre propre rejeu de la mine 1985, la part est servie dès la minute 10. Une mission qui nomme un
objet précis (par exemple une restitution) ne suit pas une part d'un autre lot : même raison ne vaut
pas même demande. Aucun cas par objet, PNJ ou scénario.

### Vérification de la reprise

- **47 tests ciblés verts** (90 s) : `test_demande_sommeil` (captures 117503, sommeil 200, part 373,
  objet précis), `test_contrat_engagement`, `test_dynamique_besoins`, `test_pas_compagnons`,
  `test_etapes_chainees`.
- **106 tests d'agendas et de reprise verts** (169 s), dont les fichiers du lot 213 et les reprises
  de demande. Deux oracles réécrits : les empreintes d'étapes de mine et d'auberge (visites, plans,
  monde) après le changement de décisions, et la scène de Lucien isolée par une capture à 95 min ;
  les attentes de `vivres_1` et du secours endormi sont explicites.
- **Banc de reprise en cours** : cinq scénarios (Relais, mine, auberge, crue, hameau) × quatre
  graines, 4 h, départ tiré, référence `0e3e626`, deux processus. Critères : aucune hausse de
  suspects par nuit ; richesse S de la mine revenue dans l'étendue de la référence, ou perte
  restante prouvée légitime. Le résultat sera ajouté au rapport et à `docs/etat-dev.md` à la fin du
  calcul (`banc2-fin.json`).

## Mesures

- Les quatre échecs de la première campagne ciblée sont expliqués : contrat obsolète, scène de Lucien
  (monde décalé par le contrat), ordre des ventes, constat décalé d'une minute. Aucun n'est un défaut du
  correctif.
- **Banc rapide** : 20 paires 4 h, départ tiré, référence `0e3e626` (absente du cache, calculée et
  rangée), 422 s, **20/20 identités** (état, empreintes, rendu, scène identiques), zéro plantage,
  zéro usurpation ni violation. **Ce banc a joué `rixe` au lieu du hameau et quatre processus au lieu
  de deux** ; sonde de l'intégration appliquée aux mêmes nuits.

| Compteur (20 nuits) | 0e3e626 | branche |
|---|---:|---:|
| Suspects 219 (non justifiés) | 1 | **0** |
| dont Aubin Relais 2024 | 1 | **0** |
| À expliquer | 16 | 13 |
| Cycles accomplis | 558 | 515 |
| Préemptions par palier supérieur | 38 | 57 |
| Entrées publiées utilisées | 29 | 33 |
| Changements de moyen admissibles | 14 | 9 |
| Pertes d'état de service payé | 8 | 8 |
| Dérives ouvertes | 160 | 173 |

**Le critère « aucune hausse de suspects par nuit » est tenu** : le seul suspect de la référence
(Aubin, Relais 2024, `117518`) disparaît, aucune nuit n'en gagne, et le maximum par nuit tombe de 1 à 0.

**Richesse S/F/D** (mesure du lot 183 : signatures `(famille, auteur, texte)`, familles présentes,
familles par PNJ) :

| Scénario (4 h, 4 graines) | S réf → branche | F | D |
|---|---|---|---|
| Relais | 15,25 → 14,50 | 4,25 → 4,25 | 1,75 → 1,62 |
| Mine | **25,75 → 17,25** | 5,00 → 4,50 | 1,96 → 1,54 |
| Auberge | 9,25 → 15,25 | 4,00 → 4,25 | 1,00 → 1,22 |
| Crue | 23,50 → 25,75 | 6,75 → 7,00 | 3,06 → 3,25 |
| Rixe | 15,00 → 15,00 | 4,25 → 4,25 | 1,81 → 1,75 |

**Coût observé, à porter au lot suivant.** La mine perd un tiers de sa richesse (gestes 148,5 → 136,25,
échanges 46,75 → 37,5) et Marchand cumule les dérives ouvertes (crue 18 → 32, Relais 5 → 14,
rixe 3 → 14, plus trois alertes `voir_alterne`). C'est la limite déclarée prise sur des cas réels :
une demande tenue dont les moyens sont épuisés reste ouverte sans borne (Bram tient `garder ses biens`
à la mine 2024, Marchand ses ventes), et le compteur la voit comme dérive plutôt que comme fin. Le
reliquat de la liste « à expliquer » (13) n'est pas certifié ; aucune boucle ni usurpation nouvelle.

Bruts : `C:/Users/msics/donjon/artifacts/demande-273-ds/` (`verifier.py`, `verification.json`,
`banc_lance.py`, `banc.log`, `banc.json`, `banc-fin.json`, `richesse273.py`, `lecture-banc.json`).
