# Rapport Codex 196 — Changements d'avis des PNJ : diagnostic et contrat commun

Branche `codex-changements-avis`. Diagnostic et conception seuls : aucun fichier de
`donjon/`, des scénarios ni des tests modifié ; aucun appel à Luna. Bruts dans
`C:/Users/msics/donjon/artifacts/avis-196/`.

---

## 1. Inventaire des parades locales existantes

Le moteur compte aujourd'hui **neuf familles de parades locales** réparties entre
`deliberation.py`, `planification.py`, `agendas.py`, `eau.py`, `ouie.py`, `defense.py`
et `social.py` :

| Parade et emplacement | Ce qu'elle empêche | Ce qu'elle laisse passer |
|---|---|---|
| **1. Hystérésis d'éveil d'un besoin** (`REPRISE = 15`, `deliberation.eveiller`, `urgents`, l. 176–218) | Clignotement d'un besoin autour de son seuil unique `urgence` d'une minute à l'autre. | Bascules entre besoins déjà pressants, entre un besoin et une pulsion/routine, ou perte d'un besoin interrompu entre `urgence - 15` et `urgence`. |
| **2. Inertie entre motifs pressants** (`INERTIE = 5`, `urgents(inertie=True)` l. 221–240, `_candidats` l. 1582–1585) | Remplacement d'un besoin pressant par un autre dont l'excès au seuil ne le dépasse pas d'au moins 5 points. | Inopérante dès que `intention["plan"]` est vide (`l. 228`, ex. attente sur place), entre paliers distincts (`Palier`), ou entre deux candidats de même motif. |
| **3. Bonus de stabilité d'agenda** (`INERTIE + max(0, VOL)/4`, `_candidats` l. 1644–1648) | Bascule entre un agenda actif et un besoin pressant de poids voisin au `Palier.BESOIN_PRESSANT`. | Perdu dès que l'intention courante prend un sous-but sans clé `"agenda"` (ex. `interposition` en `l. 1639`, `but["type"] == "interposer"`), ou face aux paliers 0–3. |
| **4. Hystérésis entre recours d'un même motif** (`retenu`, `choisir` l. 1812–1843) | Changement de moyen au sein d'un même besoin pressant tant que la méthode courante produit exactement `courant["but"]`. | Exclue si `intention["plan"]` est vide (`l. 1812`), si `routine=True` (`l. 1836`), si `recours=False` (`voir`, `prevenir`, `interposition`), entre motifs différents, ou si la méthode change de cible interne. |
| **5. Verrous de cible en route** (`en_route` dans `_plan_abri` l. 1164, `trajet`/`sejour` dans `_plan_lumiere` l. 1222, `_voir_en_cours` dans `bruit_a_voir` l. 879) | Changement d'abri, de salle éclairée ou de salle de bruit pendant le trajet vers la cible déjà choisie. | Tous les autres générateurs (`_plan_faim`, `_pulsion_a_soi`, `_remettre`, `reclamer`, `s_enquerir`, `agendas._amener`) réévaluent leur cible sans verrou. |
| **6. Progrès durable en cours** (`Palier.PROGRES_EN_COURS`, `_continuer_progres` l. 1490, `abriter` terminal de `eclairer` l. 3211, lot 90) | Abandon immédiat de `reposer`, `chauffer` ou `abriter` dès la première minute où le besoin repasse sous `urgence`. | Classé au rang 11, **sous** `BRUIT_A_VOIR` (9) et `PULSION_ROMPUE` (10) : un bruit ou une pulsion interrompt le progrès sous `urgence`, et `REPRISE = 15` empêche ensuite d'y revenir. |
| **7. Neutralisation des effets de son propre plan** (`retabli_par_son_plan` l. 1507, lot 103 ; `de_son_fait` l. 1250 ; `en_peril` l. 264, lot 163) | Interruption d'un plan par la pulsion de serrure qu'il a lui-même déverrouillée (et refermera via `retablir`), ou par `PERIL_EAU` pendant une traversée admissible. | Spécifique aux serrures, aux objets portés et à la traversée de l'eau ; ne couvre pas l'éloignement temporaire d'un poste de garde ou d'une lumière fixe pendant un plan. |
| **8. Coût de séjour et d'endurance** (`RESTER = 30`, `_endure` l. 2070, `Vue.pression`, `prix_gardes`, `lumiere_devant_crue` lot 146e, `lieux_dangereux` lot 155) | Départ vers un abri, une lumière ou une garde dont le séjour de 30 min coûte plus que de rester sur place, ou retour vers un agresseur actif. | Seuls `chaleur`, `lumiere`, `garder` et `abri` passent `tenir=True` ; les autres buts (`_pulsion`, `voir`, `faim`) ignorent la pression du lieu d'arrivée où `tenir=True` reprendra la main. |
| **9. Certificats causaux de non-réessai** (`tient`/`moyens_crus` l. 268, `couvert`/`examen` `ouie.py` l. 582, `appels_vains` l. 482, `attentes_bornees` l. 63, `agendas._croyances` l. 158, `faits_dits` `social.py` l. 52) | Répétition à l'identique d'une demande refusée, d'un examen de bruit vain, d'une recherche bornée, d'un agenda sans plan ou d'une confidence tant que les croyances pertinentes n'ont pas changé. | Chacun ne protège qu'un sous-système d'échec ou de parole ; **aucun certificat semblable ne protège une intention active qui réussit et avance normalement**. |

**Point commun.** Chaque parade locale tente de suppléer l'absence d'une même règle
dans `deliberation.choisir` : *une intention en cours reste tenue tant qu'elle n'est
ni accomplie, ni démentie dans ses préconditions par un fait nouveau, ni supplantée
par un palier supérieur ou un gain net excédant le coût de bascule*.

---

## 2. Recensement des boucles connues et classement par cause racine

L'examen du code et des rapports de lots confirme et précise les **trois causes racines**
proposées dans le brief : aucune famille historique ou actuelle n'échappe à cette
tripartition, mais plusieurs boucles combinent (1) et (2).

### Cause 1 — Choix sans engagement (réévaluation sans mémoire à chaque pas)
- **Aubin, lumière ↔ ronde** ([lot 88](rapport-codex-88-boucle.md), [lot 90](rapport-codex-90-recours-prioritaire.md), crue 2024 à 649 min, 237 passages/h) : `eclairer(tenir=True)` tarifait 30 min de séjour éclairé mais n'exportait que `aller(galerie)`. À la galerie éclairée, `eclaire(v, depart)` devenait vrai (`eclairer -> None`), faisant tomber l'intention sur la ronde `inspecter(refuge)` (`Palier.ROUTINE`) ; dès le premier pas dans le palier obscur, `securite` pressante (`Palier.BESOIN_PRESSANT`) renvoyait Aubin à la galerie.
- **Mathe / Gorm, aller voir un bruit ↔ garder** ([audit B2](../audit-nuits.md), branche `ouie-temoins`, mine 18 et Relais) : l'inspection d'une salle obscure sans y voir personne ne résolvait pas le souvenir `bruit` (`ouie.resolu` exigeait une présence vue) ; revenu à son poste de garde, le PNJ repartait aussitôt voir le même bruit.
- **Gorm, entretenir le brasero ↔ garder ses biens** ([audit curiosités](../audit-nuits.md), [lot 174](rapport-codex-174-verif-integ.md), [lot 188](rapport-codex-188-appels-alternances.md)) : quand la ronde du feu est accomplie toutes les 30 min (`REVOIR_FEU`), l'aller-retour est légitime ; en revanche, lorsqu'un besoin ou une pulsion est interrompu avant achèvement faute d'engagement sur le plan en cours, le PNJ fait la navette entre les deux lieux.
- **Amener ↔ s'interposer** ([lots 167 / 167b / 182](rapport-codex-182-attente-hameau.md), `_candidats` l. 1639 et 1644) : `interposition` est insérée au `Palier.PAROLE_DUE` (rang 5) ou en tête de `garder`, tandis qu'un agenda `amener` est au `Palier.BESOIN_PRESSANT` (rang 4) mais perd son bonus de stabilité `INERTIE + VOL/4` dès que `intention["but"]` devient `{"type": "interposer", ...}` (sans clé `"agenda"`), ou lorsque `_amener` attend sur place avec `plan = []` (`choisir` l. 1812 ignore `courant` si `plan` est vide).

### Cause 2 — Deux juges pour la même chose (planificateur vs délibération/exécution)
- **Mathe, ouvrir le garde-manger pour servir ↔ le refermer à clé** ([lot 103](rapport-codex-103-boucle-garde-manger.md), mine 3 à 9 min, 328 ouvertures/fermetures) : `planification.retablir` (juge 1) construisait un plan valide `[deverrouiller, ouvrir, servir, fermer, verrouiller]`, mais à mi-parcours `deliberation._candidats` (juge 2) voyait la pulsion `verrouillee` rompue au `Palier.PULSION_ROMPUE` et interrompait le service non urgent parce que `retabli_par_son_plan` ne protégeait que les motifs urgents.
- **Brune, rallumer la torche pour crocheter ↔ l'éteindre par économie** ([lot 146e](rapport-codex-146e-amener-social.md), crue 1985 à 102 min, 10 allumages / 9 extinctions) : `Vue.lumiere_devant` et `pnj._assez_de_lumiere` (juge 1) exigeaient la lumière devant la serrure, tandis que `deliberation.lumiere_utile` / `menager_flamme` (juge 2, appelé chaque minute hors de `choisir` dans `pnj._avancer` l. 1997) jugeait la lumière de la salle et éteignait la torche.
- **Brune, fuir un agresseur ↔ revenir chercher la lumière ou l'abri près de lui** ([lot 155](rapport-codex-155-fuite-lumiere.md), crue 2024 à 680 min, 68 passages/h) : `defense.choisir` (juge 1, appelé en tête de `deliberation.choisir` l. 1798) faisait fuir la salle de l'agresseur actif, puis une fois dans la salle voisine obscure où `dangers(monde, id)` était vide, `planification.eclairer` / `_plan_abri` (juge 2) ignorait `defense.actifs` et renvoyait Brune dans la salle de l'agresseur.

### Cause 3 — Croyances ou suivis qui basculent sans fait nouveau
- **Gorm et Ilse, deux pentes d'eau opposées promues tour à tour** ([lot 58](rapport-codex-58-eau-plan-marche.md), crue 2024 à 368 min et 1985 à 247 min, 44 passages) : revoir le niveau d'une salle dans `eau.estimation` rajeunissait la date d'une ancienne vitesse mesurée dans cette salle ; en marchant entre deux salles, Gorm faisait basculer sa prévision entre $-8$ et $+8\text{ cm/h}$ sans nouvelle mesure de vitesse, ouvrant et fermant alternativement la route.
- **Sève, Ilse et Maël, ancienne pente non bornée par une salle revue sèche** ([lots 182 / 185](rapport-codex-185-prevision-bornee.md), hameau 42) : une observation sèche n'ancrait pas de niveau dans `eau.observer`, laissant une ancienne pente positive extrapoler 110 cm d'eau dans une salle pourtant revue sèche.
- **Avertissements et constats redits** ([lot 64](rapport-codex-64-deja-dit.md), [lot 108](rapport-codex-108-avis-redits.md), [lot 191](rapport-codex-191-deja-entendu.md)) : le suivi des paroles dites tombait hors des 40 souvenirs (lot 64), était effacé pour tous les destinataires dès que le seul locuteur changeait d'avis (lot 108), ou ignorait ce qui avait été entendu ensemble (lot 191).
- **Brune, douze appels à Gorm** ([lot 174](rapport-codex-174-verif-integ.md), [lot 188](rapport-codex-188-appels-alternances.md), crue 1985 à 495–518 min) : le diagnostic du lot 188 a établi que ces rappels suivaient chacun un nouveau bruit de pas anonyme rouvrant `indice_recherche` (aucune violation de l'invariant de réessai), tandis que le même lot a révélé un défaut de **Cause 2** entre `_chercher` (qui planifie d'inspecter après une sortie) et `presence.franchir` (qui retire définitivement le marcheur à la digue).

---

## 3. Détecteur générique et mesures sur 20 nuits (4 h)

### Définition du détecteur (`tools/detecter_changements_avis.py`)

La sonde enveloppe `deliberation.choisir`, `deliberation.deliberer`, `pnj.agir` et
`deliberation.menager_flamme` en lecture seule (`--verifier-empreinte` vérifie que
`empreintes`, `chronique` et `sha256(monde.data)` sont strictement identiques à
`banc_pnj.nuit`). À chaque changement de décision canonique `_cle_decision(intention["but"])`
d'un PNJ, elle photographie six catégories d'**entrées externes** réellement lues par le
choix (`croyances_valeurs`, `besoins_paliers`, `pulsions_dues`, `alarmes_et_dangers`,
`social_et_engagements`, `inventaire_et_droits`), séparées de la **progression interne**
(`lieu`, `ordre_visites`, `manque`).

Tout retour `D1 -> D2 ... -> D1` dans une fenêtre de 60 min est classé selon l'état de
`D1` à son abandon (`t_quitte`) et à sa reprise (`t_retour`) :
- **`cycle_accompli` / `garde_interruption_accomplie`** : `D1` était accompli en
  `t_quitte`, ou `D1` était une garde interrompue par une tâche `D2` elle-même accomplie
  avant le retour à la garde ;
- **`justifie_par_entree_nouvelle`** : au moins une entrée externe a changé entre le
  début et l'abandon de `D1`, ainsi qu'entre l'abandon et le retour ;
- **4 classes `non_justifie_*`** :
  1. `strict_complet` : aucune entrée externe ni le lieu n'a changé entre `t_quitte` et `t_retour` ;
  2. `retour_etat_initial_exact` : l'état externe et le lieu en `t_retour` sont redevenus bit à bit identiques à ceux de `t_debut` ;
  3. `externe_fixe_seul_deplacement` : aucune entrée externe n'a changé, seul le lieu du PNJ a bougé ;
  4. `abandon_sans_entree_externe` : `D1` a été abandonné sans qu'aucune entrée externe ait changé entre `t_debut` et `t_quitte`.

### Résultats sur 20 nuits (`relais`, `mine`, `auberge`, `crue`, `crue_hameau` × `1985, 7, 42, 2024`, 4 h)

Bruts dans `C:/Users/msics/donjon/artifacts/avis-196/detection-4h.json` (538,9 s en un processus à priorité réduite) :

| Scénario (4 graines × 4 h) | Cycles accomplis | Justifiés (entrée nouvelle) | Non justifiés (total) | `strict_complet` | `retour_etat_initial` | `seul_deplacement` | `abandon_sans_entree` | `menager_flamme` contraire |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **relais** | 109 | 7 | **0** | 0 | 0 | 0 | 0 | 0 |
| **mine** | 102 | 11 | **0** | 0 | 0 | 0 | 0 | 0 |
| **auberge** | 135 | 10 | **0** | 0 | 0 | 0 | 0 | 0 |
| **crue** | 87 | 193 | **359** | 118 | 214 | 0 | 27 | 0 |
| **crue_hameau** | 161 | 51 | **5** | 0 | 4 | 1 | 0 | 0 |
| **Total (20 nuits)** | **594** | **272** | **364** | **118** | **218** | **1** | **27** | **0** |

### Preuve sur chronique et épisodes : les 364 cas sont de vraies boucles de `main`

La relecture des chroniques et de `Recit.episodes` établit que **les 359 cas de `crue` et
les 5 cas de `crue_hameau` sont tous de vraies boucles de décision du moteur**, réparties
en quatre familles exactes :

1. **Gorm (`marchand`), `pulsion(reserve, verrouillee=True)` ↔ `garder(antichambre)` / `voir` — 358 des 359 cas de `crue`** (`crue 7` min 138–240 : **160** cas + 60 masqués par 1 cm d'eau ; `crue 42` min 142–240 : **173** + 50 ; `crue 2024` min 214–240 : **25** + 10) :
   - **Fait déclencheur dans la chronique** : Brune force la porte de la réserve au pied-de-biche (`integrite = 0, ouverte = True, verrouillee = False`) à **137 min** (`crue 7`), **141 min** (`crue 42`) ou **213 min** (`crue 2024`). Gorm voit la réserve brisée (`croyances["reserve"]["fin"] = {"valeur": "detruit", "source": "vu"}`). Dès cette minute et jusqu'à 240 min, il oscille plusieurs fois par minute entre `pulsion(reserve, verrouillee=True)` et `garder(antichambre)` (ou `voir(antichambre)` à 230 min en `crue 7`, `t = 138256 -> 138286 -> 138291`).
   - **Mécanisme exact (combine les trois causes racines)** :
     - *Cause 2 (deux juges sur la porte brisée)* : à l'exécution, `portes.valider_fermeture` (`portes.py` l. 10) refuse `fermer("reserve")` parce que `integrite == 0` (« le battant est brisé ») et appelle `constater(monde, "marchand", "reserve", "essai")` (`pnj.py` l. 974) avant de renvoyer `MANQUE`. Mais ni `deliberation.satisfaite` (`l. 668`), ni `planification.gestes` (`l. 1443`), ni `planification._entrees` (`l. 1943`, qui filtre `if a != "fin"`) ne consultent `fin == "detruit"`.
     - *Cause 3 (révision incomplète et asymétrique de `constater`)* : dans `esprits.constater` (`esprits.py` l. 986–993), voir une porte ouverte (`source="vu"`) écrit `etat["ouverte"] = True` **sans effacer** `croyances["reserve"]["verrouillee"] = True` (héritée du savoir initial en `crue 42` et `2024`), de sorte que `_pulsion` croit qu'un simple `[fermer("reserve")]` suffit à rétablir `verrouille and not ouvert`. De plus, `constater(..., "essai")` (`l. 991`, `if ... and source == "vu"`) réécrit `etat = {"ouverte": True}` en effaçant la clé `"vide": True`, que `percevoir_tous` (`source="vu"`) remet aussitôt à `{"ouverte": True, "vide": True}` : cette bascule interne de croyance produit les **214** `non_justifie_retour_etat_initial_exact` (`diff_debut_retour = []`).
     - *Cause 1 (auto-annulation par `retabli_par_son_plan` et `plan = []`)* : en `crue 7`, Gorm a vu `verrouillee = False` et porte `cle_reserve` ; son plan pour `pulsion(reserve)` est `[aller(echoppe), aller(reserve), fermer(reserve), verrouiller(reserve)]`. Au choix suivant (dès 138 min en plein trajet dans l'antichambre, avant même d'atteindre la réserve !), `retabli_par_son_plan` (`deliberation.py` l. 1507–1525) voit `"verrouiller"` dans `intention["plan"]` et `biens in urgents(...)`, renvoie `True` et **exclut la pulsion en cours de `_candidats` (`l. 1622`)** ! Gorm bascule alors sur `garder(antichambre)` (`plan = []`), qui renvoie immédiatement `FIN` dans `pnj.agir` (`pnj.py` l. 1659) et rappelle `choisir` : comme `intention["plan"]` ne contient plus `"verrouiller"`, `retabli_par_son_plan` renvoie `False` et Gorm reprend `pulsion(reserve)` (`117` `strict_complet` et `27` `abandon_sans_entree_externe`).
   - **Pourquoi `audit_nuits.py` et `Recit.personnage` ne la voyaient pas** : `audit_nuits.py` ne cherche des bascules que sur les relevés aux 5 minutes (`PAS = 5`) et sur les lignes de chronique répétées $\ge 6$ fois ; or `pnj.py` l. 972–975 capture `ErreurMonde` sur `fermer` sans écrire dans la chronique, et `Recit.personnage` (`recit_pnj.py` l. 264–267) agrège tous les épisodes sans geste ni abandon en une seule ligne `Sans geste à faire : garder la réserve de vivres sous clé (biens) ×148`.

2. **Brune, évacuation `PERIL_EAU` auto-annulée — 1 cas en `crue 1985` (min 42) et 2 cas en `crue_hameau 1985` (min 204)** :
   - En `crue 1985` à 42 min (`t = 25353 -> 25373`, `0,03 min` dans `echoppe` avec 3 cm d'eau), Brune suit `agenda a1` (`aller(beffroi)`). `eau.en_peril` (`eau.py` l. 271–272) renvoie `True`, activant `_plan_abri` au `Palier.PERIL_EAU` (`abri(chambre_cloche)`). Deux secondes plus tard, sur un éveil dans la même salle humide sans changement d'entrée, `choisir` rappelle `en_peril` : comme `intention["plan"][0]` est maintenant `aller(chambre_cloche)` (sortie sèche), `en_peril` renvoie `False`, retirant `_plan_abri` du `Palier.PERIL_EAU` (`securite = 11,7` non pressante) et ramenant Brune à `agenda a1` (Cause 1 : un palier d'urgence qui s'auto-annule dès que l'intention d'évacuation est adoptée).
   - En `crue_hameau 1985` à 204 min (`t = 122400 -> 122645 -> 122682`), `planifier("chaleur")` (juge 1) fait entrer Brune de `antichambre` dans `echoppe` (`aller(echoppe)`), où `eau.en_peril` (juge 2) l'interrompt aussitôt pour la renvoyer en `antichambre` (`abri(antichambre)`), d'où `chaleur(poele_guet)` la renvoie vers `echoppe`.

3. **Ilse, changement d'abri en cours de trajet — 1 cas `seul_deplacement` (+ 17 avec révision de croyances) en `crue_hameau 2024` (min 42–97)** :
   - `abri(antichambre) -> abri(echoppe) -> abri(chambre_cloche) -> abri(antichambre)` (`t = 25398 -> 26661 -> 29093`) : dans `_plan_abri` (`deliberation.py` l. 1168), le verrou `en_route` saute dès que `ici in abris` ou `eau_monte`, et `_plan_abri` sélectionne une salle sans vérifier la précondition d'exécution de `pnj._abriter` (`not menacee(monde, id, lieu)` et présence effective du compagnon sûr).

4. **Brune, chute transitoire sur `intention = None` — 2 cas en `crue_hameau 1985` (min 190)** :
   - `agenda a1 -> None -> agenda a1` (`t = 114321 -> 114331 -> 114346`, `0,02 min` en `antichambre`, `diff_debut_retour = []`).

### Ce que j'ai corrigé dans le détecteur et ce qu'il ne voit pas encore

- **Correction apportée à `_est_accompli`** (`tools/detecter_changements_avis.py` l. 94–131) :
  1. `abri` n'est plus déclaré accompli sur la seule condition `securite <= SECURITE_FIN` (qui était déjà vraie lors d'une évacuation `PERIL_EAU` à `securite = 11,7` alors que le PNJ n'avait pas quitté la salle inondée), mais exige `ici == cible and not eau.en_peril(monde, id)`.
  2. `voir(salle)` vérifie `cause_sortie == "fin:"` ou la résolution effective des bruits de `salle` via `ouie.resolu` (et non `bruit_a_voir(monde, id)` après écrasement de `_voir_en_cours`).
- **Ce que le détecteur ne voit pas (limites explicites)** :
  1. *Oscillations chevauchant un pas de crue* : quand la boucle de Gorm franchit une frontière de minute où l'eau monte d'1 cm dans une salle vue, `croyances_valeurs["__eau__"]` change et l'aller-retour est classé par prudence dans `justifie_par_entree_nouvelle` (120 itérations supplémentaires de la même boucle en `crue 7/42/2024`).
  2. *Changement de moyen sous un même `but`* : deux plans de `tete_plan` différents qui conservent exactement le même dictionnaire `intention["but"]` restent dans le même épisode.
  3. *Dérives ouvertes `A -> B -> C` sans retour à `A`* ou cycles de période supérieure à 60 min.

---

## 4. Proposition de contrat d'engagement commun

### 4.1. Liste fermée des raisons de quitter l'intention courante (`deliberation.choisir`)

Une intention active `I` (y compris à `plan == []` lorsqu'elle tient un poste de garde ou
une attente sur place) reste tenue tant qu'aucune des **quatre conditions fermées**
suivantes n'est remplie :
1. **Accomplie (`est_accompli(monde, id, I)`)** : le prédicat d'achèvement propre au but
   de `I` est satisfait (et non le simple fait que `I["plan"]` soit vide).
2. **Démentie ou bloquée (`est_dementie(monde, id, I)`)** : l'action en tête vient de
   renvoyer `MANQUE` ou un refus, ou une croyance nouvelle rend la cible ou la route
   inadmissible (`fin in ("detruit", "consomme")`, `etat.parti`, route noyée ou en péril).
3. **Préemptée par un palier strictement supérieur (`cand.palier < palier_actif(I)`)** :
   un candidat valide existe à un `Palier` strictement plus prioritaire. Le palier actif
   d'une intention inclut la raison qui l'a fait naître tant que cette raison persiste :
   une évacuation née au `Palier.PERIL_EAU` conserve `Palier.PERIL_EAU` tant que le PNJ
   n'est pas arrivé dans une salle sèche hors péril.
4. **Supplantée au même palier avec marge d'engagement (`gain(cand) >= gain(I) + COUT_BASCULE`)** :
   au même `Palier`, un candidat d'un autre but ne remplace `I` que s'il la domine d'au
   moins `INERTIE` majorée du trajet déjà parcouru pour `I`, même si `I["plan"]` est vide.

### 4.2. Juge unique entre choisir, continuer et dire « fini »

Chaque famille de but partage un seul contrat `(admissible, est_accompli)` entre
`deliberation`, `planification` et `pnj.agir` :
- **Portes et contenants détruits** : `deliberation.satisfaite`, `planification.gestes`
  (`fermer`, `verrouiller`) et `planification._entrees` lisent `croyances[o].get("fin") == "detruit"`
  exactement comme `portes.valider_fermeture`. Un battant cru brisé (`fin == "detruit"`)
  ne génère ni étape `fermer`/`verrouiller` ni candidat `_pulsion_a_soi`.
- **Non-auto-annulation des gardes de plan (`retabli_par_son_plan` et `eau.en_peril`)** :
  - `retabli_par_son_plan(monde, id, c)` (`deliberation.py` l. 1507) renvoie `False` dès
    que `intention["but"]` est la pulsion `c` elle-même (`intention["but"] == {"type": "pulsion", **c}`) :
    une intention ne peut jamais s'exclure elle-même de `_candidats` sous prétexte que
    son propre plan va la rétablir !
  - `eau.en_peril(monde, id)` distingue le péril physique du lieu courant (`lieu_en_peril`)
    de la validité de la sortie en cours : tant que `lieu_en_peril` est vrai, l'intention
    d'évacuation garde le `Palier.PERIL_EAU`, et `planification.route_admissible` refuse
    aux recours ordinaires (`chaleur`, `faim`, `routine`) de pénétrer dans une salle où
    `lieu_en_peril` s'activerait sans être un simple transit vers une salle sèche.
- **Abri et lumière** : `_plan_abri` et `pnj._abriter` appellent le même prédicat
  `abri_valide(monde, id, salle)` ; `deliberation.lumiere_utile` et `Vue.lumiere_devant`
  appellent le même prédicat de besoin lumineux de l'étape en tête.

### 4.3. Révision monotone des croyances par fait constaté (`esprits.constater`)

- **Attributs couplés** : dans `esprits.constater`, enregistrer `etat["ouverte"] = True`
  ou `fin = "detruit"` sur une porte ou un contenant met simultanément à jour
  `croyances[id]["verrouillee"] = {"valeur": False, "lieu": salle, "minute": m, "source": source}`
  si une croyance `verrouillee = True` existait (une porte vue ouverte ou brisée ne peut
  plus être crue verrouillée).
- **Symétrie `"vu"` / `"essai"`** : `constater(..., "essai")` conserve ou calcule les
  mêmes clés d'`etat` visibles (`"vide"`) que `constater(..., "vu")` lorsque la salle est
  éclairée, évitant toute bascule de `croyances[o]["etat"]` entre l'essai et la perception
  de fin de pas.

### 4.4. Parades rendues inutiles, risques et vérification comme garantie (`VERIFIER_AVIS`)

| Proposition | Parades locales rendues inutiles ou absorbées | Risques identifiés et bornes | Garantie déterministe (`VERIFIER_AVIS`) |
|---|---|---|---|
| **Engagement commun (4.1)** | Verrous ad hoc par générateur (`en_route` dans `_plan_abri`, `trajet`/`sejour` dans `_plan_lumiere`, `_voir_en_cours`), cas particuliers `plan != []` dans `urgents` (l. 228) et `choisir` (l. 1812), patchs de stabilité d'`interposer` / `agenda`. | *Risque* : entêtement si un plan devient très coûteux sans être impossible. *Borne* : la marge `COUT_BASCULE` reste finie (`INERTIE = 5`), donc un besoin qui monte de $> 5$ points ou change de `Palier` préempte immédiatement. | Assertion en fin de `choisir` / `audit_nuits` : tout retour `D1 -> D2 -> D1` non accompli doit citer une raison `R2`, `R3` ou `R4` (compteur `total_non_justifies == 0`). |
| **Juge unique (4.2)** | Filtres dispersés `retabli_par_son_plan` sur sa propre pulsion, `lumiere_devant_crue` séparé de `lumiere_utile`, exceptions de `en_peril` selon `plan[0]`. | *Risque* : bloquer la traversée d'une salle humide lorsqu'elle est le seul chemin vers un abri. *Borne* : `route_admissible` autorise le transit si la destination finale est sèche et sûre. | Invariant de cohérence : aucune étape produite par `planification.gestes` à `depart(monde, id, v)` ne peut échouer dans `pnj.agir` sur une croyance déjà présente dans `e["croyances"]` (dont `fin`). |
| **Révision cohérente (4.3)** | Patchs de non-réessai après échec de porte brisée. | *Risque* : écraser une croyance `verrouillee` lors d'un essai dans le noir. *Borne* : ne mettre `verrouillee = False` que si `o.get("ouverte")` ou `fin == "detruit"` est constaté. | Invariant d'idempotence : `constater(m, id, o, "essai")` suivi de `constater(m, id, o, "vu")` au même instant et même état physique laisse `e["croyances"][o]` invariant. |

---

## 5. Découpage en lots d'un invariant chacun (30 à 45 min)

| Ordre et lot | Invariant garanti | Fichiers touchés | Ce que le lot mesure et prouve |
|---|---|---|---|
| **Lot 196a — Croyance `fin`, cohérence `constater` et non-auto-annulation de `retabli_par_son_plan`** | Un objet cru détruit (`fin == "detruit"`) ou vu ouvert ne peut ni rester cru verrouillé, ni être planifié pour `fermer`/`verrouiller`, ni osciller entre `"essai"` et `"vu"` ; `retabli_par_son_plan` n'exclut jamais la pulsion qui est déjà le but de l'intention courante. | `donjon/esprits.py`, `donjon/deliberation.py`, `donjon/planification.py`, `tests/` | Cas réels `crue 7` (min 137–240), `crue 42` (min 141–240) et `crue 2024` (min 213–240) : les **358** allers-retours non justifiés (+ 120 masqués par l'eau) de Gorm passent à **0** ; empreintes 2 h identiques sur `relais`, `mine`, `auberge`. |
| **Lot 196b — Juge unique d'évacuation et de traversée d'eau (`en_peril` / `_plan_abri` / `route_admissible`)** | Tant qu'un PNJ se trouve dans une salle en péril d'eau, son évacuation conserve le `Palier.PERIL_EAU` jusqu'à la sortie de la salle humide ; aucun recours ordinaire ne planifie un séjour ou un trajet entrant dans une salle en péril sans sortie sèche ; `_plan_abri` et `_abriter` partagent le même prédicat d'abri. | `donjon/eau.py`, `donjon/deliberation.py`, `donjon/planification.py`, `tests/` | Cas réels Brune (`crue 1985` min 42, `crue_hameau 1985` min 204) et Ilse (`crue_hameau 2024` min 42–97) : allers-retours d'évacuation et d'abri ramenés à **0** sur `crue` et `crue_hameau` ; empreintes 2 h identiques hors eau active. |
| **Lot 196c — Contrat d'engagement dans `choisir` et maintien des intentions à `plan == []`** | `choisir` applique la liste fermée (Accomplie / Démentie / Palier supérieur / Gain $\ge$ `INERTIE`), conserve `courant` même lorsque `plan == []` (garde ou attente sur place) ou lors d'un sous-but d'interposition, et unifie les verrous de cible en route. | `donjon/deliberation.py`, `donjon/agendas.py`, `tests/` | Cas réel Brune (`crue_hameau 1985` min 190, `agenda -> None -> agenda`) ramené à **0** ; **0** aller-retour non justifié sur les 20 nuits (`relais`, `mine`, `auberge`, `crue`, `crue_hameau` × 4 graines, 4 h). |
| **Lot 196d — Garantie déterministe `VERIFIER_AVIS` dans `audit_nuits.py`** | L'audit des nuits et les tests d'invariants vérifient déterministement qu'aucun PNJ ne revient à une décision non accomplie sans entrée externe nouvelle pertinente. | `tools/detecter_changements_avis.py`, `tools/audit_nuits.py`, `tests/` | `total_non_justifies == 0` certifié sur les 20 nuits de 4 h et intégré aux contrôles d'intégration. |
