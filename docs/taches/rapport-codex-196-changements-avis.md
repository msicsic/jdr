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

*(Section complétée ci-dessous avec les résultats de `tools/detecter_changements_avis.py`.)*
