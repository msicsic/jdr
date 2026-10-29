# Plan de migration — narrateur libre, moteur souverain

> **G0 — 29 octobre 2026 : plan historique.** Le [contrat adopté](../AGENTS.md#contrat-du-mj)
> et la [feuille de route unique](plan-refonte-mj.md) remplacent son ordre de travail.
> Une voie non portée garde ses contrôles. Les phases décrites ci-dessous restent
> disponibles pour la transition ; leurs états sont datés du 17 octobre.
>
> - **Phases 0, 1 et 2 : acquis repris.** Archives de mesure, vérités séparées
>   et transactions sur copie. G0 aligne le contrat écrit ; G2 porte la validation.
>   La proposition historique pour `AGENTS.md` en phase 1 n'est plus la cible.
> - **Phase 3 reportée : pas de reprise globale.** G12/G13 reprennent l'admission
>   commune des faits et leur validation. L'unification de tous les modes reste
>   sans nécessité établie. Fusionner les audits n'est pas un objectif acquis.
>   Une propriété non calculable garde sa revue ciblée à l'admission.
> - **Phase 4 : remplacée par famille.** G4 à G7/G15 à G20 rendent le mécanique
>   et les répliques fixées par le moteur. Noms, références et provenance restent
>   contrôlés. G8 à G11/U-A remplacent la boucle cosmétique bloquante par le fond,
>   avec contrôle avant publication et rejet entier sans relance si doute.
> - **Phase 5 : reprise par G14 après G12/G13.** Matérialiser une seule fois
>   avant manipulation, ou déclarer non manipulable ; reprendre l'intention.
> - **Phase 6 reportée : reste hors du portage.** La boucle générale d'outils
>   n'est un préalable ni à G1/G2 ni aux menus directs. Les corrections typées
>   et bornées ne demandent pas cette réécriture globale des simulations.
> - **Phase 7 : remplacée par G1/G3.** Petit compilateur public, sources stables
>   et contrat de transport commun ; pas d'élagage isolé du prompt monolithique.
> - **Phase 8 : caduque sous la cible pour le mécanique.** G4 à G7/G15 à G20
>   remplacent le récit de résultat par le moteur. Les contrôles actuels restent
>   tant que chaque voie n'est pas portée. Luna garde l'ambiance et le contenu
>   de dialogue inédit admis par D0.
> - **Phase 9 : budgets d'invention conservés dans G12/G13/G14.** G8 à G11/U-A
>   portent l'ambiance distincte ; aucun habillage ne crée d'entité.
> - **Phase 10 : mécaniques existantes conservées.** Leur extension reste un
>   chantier distinct. G1 et les lots sociaux gardent les interactions actuelles.
>
> Le mécanique ne repose plus, à la cible, sur la seule compatibilité d'une prose
> libre avec l'état. La fidélité du libre à effets garde son filet de transition
> avec U-P/U-C, puis décision de retrait sur mesure à G21. Le clic n'est pas
> réinterprété. Le protocole de chaque phase ci-dessous est historique : les lots
> suivent désormais les vérifications ciblées de la feuille de route. Aucun test
> de jeu, appel à Luna ou banc dans G0.

Ce plan applique la revue du 17 octobre 2026. Il remplace l'invariant « chaque phrase
affichée reproduit une attestation du moteur » par « le MJ n'affirme rien que le moteur
ne puisse honorer ». Le moteur garde l'autorité sur l'état ; Luna retrouve sa voix.

Chaque phase est un commit autonome : tests verts, banc de mesure relancé, résultat
comparé à la phase précédente.

## État au 17 octobre 2026 (branche `migration-narrateur`)

| Phase | État | Remarques |
|---|---|---|
| 0 | fait | `tools/banc_parties.py`, scripts `tests/data/bancs/`, `donjon/lexique.py` |
| 1 | fait | trois niveaux dans `AGENTS.md`, README découpé (`docs/mecaniques.md`, `docs/connexion.md`) |
| 2 | fait | `donjon/transactions.py` ; la boucle de jeu réapplique une liste ordonnée |
| 4 | fait | verdicts mécanique / ambiance, garde-fou lexical déterministe, texte affiché tel quel ; contre-revue d'action limitée à l'état |
| 5 | fait | `ambiance_ciblee`, réexamen après création d'un objet |
| 7 | fait | prompt de conversation 3 123 → 2 134 mots, narration 232 mots ; sources d'audit limitées par le schéma |
| 8 | fait | récit des résultats par Luna, repli moteur, contrôle des nombres, `--recit-moteur` |
| 9 | partiel | budget d'invention fait ; habillage à la première visite écarté (l'ambiance à la demande le rend peu utile, pour un appel de plus par salle) |
| 10 | partiel | composition étendue, réactions des PNJ au son, horloges d'environnement et lumière par case faites ; aucun scénario ne déclare encore réactions ni horloges ; fragments et profils d'artisanat non faits |
| 3 et 6 | reportées | voir ci-dessous |

**Phases 3 et 6 reportées.** L'essai de transport a réussi : sur le forfait, avec
`store: false`, Luna appelle un outil, reçoit sa sortie (`function_call_output`) puis appelle
`repondre`. Mais le banc montre que le nombre d'appels par tour vient des contrôles, pas du
nombre de modes : la boucle ne réduirait guère les appels. Elle impose en revanche de réécrire
environ 110 simulations de tests en même temps que `mj.py`, ce qui retire aux tests leur rôle
d'oracle pendant la refonte. À mener comme étape dédiée, relue.

**PNJ réactifs et horloges.** Faits comme mécaniques générales, opt-in par les données :
`reaction_son` sur un PNJ (`donjon/pnj.py`) et `horloges` dans l'état (`donjon/horloges.py`),
dont les effets réutilisent ceux des transitions de scénario. Les phrases « le cri ne crée pas
de sauveteur » et « aucun chronomètre » décrivaient un cas de test et un scénario, pas des
règles du jeu ; elles ont été reformulées. Reste à choisir quels scénarios les déclarent
(crue du Relais, Gorm alerté par un cri).

**Écart de moteur relevé par le banc.** « J'écoute à la porte » n'a pas d'opération de
perception auditive : le moteur refuse une improvisation d'observation et Luna ne peut que
l'expliquer. Une perception `écouter` fondée sur `sons.portee` serait le correctif général.

### Mesures du banc (3 scripts, 31 tours confiés au MJ, Luna réel)

| Version | Tours en repli | Appels par tour MJ | Secondes par tour MJ | Mentions sans fondement |
|---|---|---|---|---|
| Référence (`main`) | 25 / 31 | 6,4 | 26 | 0 |
| Phase 4 | 5 / 31 | 3,6 | 15 | 0 |
| Phase 7 | 1 / 31 | 3,2 | 13 | 0 |
| Final (phases 0 à 10 partielles) | 0 / 31 | 3,2 | 13 | 0 |

Un « repli » est une formule de secours affichée à la place d'une réponse (« Je ne peux pas
encore répondre avec certitude », « Corvus n'a rien tenté »…). Les mentions sans fondement
sont des noms d'entités absents de ce que le MJ a reçu ou affiché.

**Ordre d'exécution retenu.** 0, 1, 2, puis 4 et 5 (le cœur, suivi du point de décision
du banc), puis 3 et 6 ensemble, puis 7, 8, 9. Le mode d'ajout unique de la phase 3
change le parcours de réponse après un fait établi ; il est réalisé avec la boucle
d'outils, où ce parcours devient « outil `etablir_faits`, puis outil `repondre` »,
plutôt que par une étape intermédiaire remplacée ensuite. Les phases 2, 3 et 6 sont des refontes sans changement
de comportement visible ; les phases 4, 5, 8 et 9 changent ce que le joueur lit.

| Phase | Objet | Nature | Taille |
|---|---|---|---|
| 0 | Banc de mesure des parties réelles | outillage | M |
| 1 | Contrat écrit : trois niveaux de vérité | documentation | S |
| 2 | Transactions unifiées entre MJ et boucle de jeu | refonte | M |
| 3 | Un seul mode d'ajout persistant, audits fusionnés | refonte | M |
| 4 | Nouveau contrôle narratif | comportement | L |
| 5 | Matérialisation à la demande | comportement | M |
| 6 | Boucle d'outils | refonte | L |
| 7 | Élagage du prompt | qualité | M |
| 8 | Récit des résultats par Luna | comportement | S |
| 9 | Habillage des salles et budget d'invention | comportement | M |
| 10 | Gameplay : PNJ réactifs, horloges, composition | gameplay | L |

---

## Phase 0 — Banc de mesure (avant toute modification)

**But.** Rendre mesurable le compromis rigueur / fluidité, et disposer d'une référence
sur `main` avant de toucher au contrat.

- `tools/banc_parties.py` : rejoue des scripts de 15 à 25 tours sur une sauvegarde
  temporaire, avec Luna réel, comme les `tools/test_*_reel.py` actuels.
- Scripts dans `tests/data/bancs/` : `relais.json`, `atelier.json`, `crypte.json`.
  Chaque script mélange question d'ambiance, question factuelle, dialogue de PNJ,
  action simple, manœuvre avec jet, improvisation (« je fredonne »), fouille dans la
  pénombre et ciblage d'un détail évoqué par le MJ au tour précédent.
- Mesures par tour, tirées des traces de l'observateur déjà existant :
  nombre d'appels, secondes, tokens, mode final, replis (`_texte_moteur` de secours,
  « Je ne peux pas encore… », refus de validation), texte affiché.
- Contrôles déterministes en fin de script : `Monde.verifier()` après rechargement,
  absence dans les textes affichés des noms et alias d'objets non perçus.
- Sortie : `artifacts/bancs/<date>-<script>.jsonl` et un résumé tabulaire.
- La lecture humaine des textes reste le juge principal ; une note automatique par
  un appel LLM est facultative et ne sert qu'à repérer les tours à relire.

**Critère de sortie.** Référence enregistrée pour les trois scripts sur `main`.

---

## Phase 1 — Contrat écrit

Mettre à jour `AGENTS.md` et `docs/contrat-mj.md` avant le code, puisque les agents
suivent ces textes.

### Trois niveaux de vérité

| Niveau | Contenu | Autorité | Contrôle avant affichage |
|---|---|---|---|
| Mécanique | entités identifiées, positions, sorties et passages, portes et attaches, possession, ressources (or, PV, combustible), lumière, présence et identité des PNJ, missions, objectifs, résultats d'action | moteur seul | toute contradiction ou invention dans ces domaines est refusée |
| Interactif | objet ou détail que le joueur peut cibler | moteur, après proposition typée | validation actuelle de `faits_locaux` |
| Ambiance | aspect, odeur, son de fond, texture, impression | Luna | enregistrée avec son lieu ; ne crée aucune entité des domaines mécaniques |

Les domaines mécaniques forment une liste fermée dérivée du schéma de l'état, pas
d'exemples. Un élément d'ambiance devient interactif seulement quand le joueur le
cible (phase 5).

### Proposition pour `AGENTS.md`, section « Contrat du MJ »

> Le MJ n'affirme rien que le moteur ne puisse honorer. Les affirmations qui touchent
> l'état mécanique (entités, positions, passages, possession, ressources, lumière,
> présence des PNJ, missions, résultats) doivent être compatibles avec l'état ; une
> invention dans ces domaines passe par une proposition typée validée avant affichage.
> L'ambiance est libre, enregistrée avec son lieu avant affichage, et ne crée aucune
> entité mécanique. Un élément d'ambiance ciblé par le joueur est matérialisé par le
> moteur ou déclaré non manipulable. Une parole de PNJ établit qu'elle a été prononcée
> et entendue, sans établir que son contenu est vrai.

Conserver telle quelle la règle de conception prioritaire (pas de cas particulier).

### README

Découper le README actuel : `README.md` court (lancer, jouer, commandes),
`docs/mecaniques.md` (lumière, cases, fabrication, vol, dialogues),
`docs/contrat-mj.md` (contrat). Supprimer les passages périmés, par exemple
« pas encore de navigation case par case » dans les limites.

---

## Phase 2 — Transactions unifiées (refonte sans changement de comportement)

**Constat.** `MJOpenAI` renvoie une clé privée par type d'ajout (`_espace`,
`_conversation_pnj`, `_enrichissement`, `_savoirs`, `_profil_joueur`,
`_faits_narratifs`). `jeu.py:297-356` et `comparaison.py:136-150` réappliquent chacune
par une branche distincte. La boucle d'outils (phase 6) produira plusieurs ajouts par
tour : il faut d'abord une forme commune.

- Nouveau module `donjon/transactions.py` :
  - registre `{type: preparer}` ; tous les modules existants ont déjà la signature
    `preparer(monde, proposition, revision) -> travail` (`espace`, `dialogues`,
    `enrichissement`, `connaissances`, `profil_joueur`, `faits_locaux`) ;
  - `appliquer(monde, transactions) -> travail` applique la liste dans l'ordre sur
    une copie, chaque transaction contrôlant sa révision attendue.
- La réponse du MJ porte `_transactions: [{"type", "revision", "proposition"}, ...]`
  à la place des six clés privées.
- `jeu.py` : une seule branche → `appliquer`, puis `memoriser`, `consigner_narration`,
  recalcul de la proposition en attente, `sauver`, `imprimer`.
- `comparaison.py` lit la même liste pour son affichage.

**Tests.** Suite actuelle verte ; adapter les tests qui inspectent les clés privées.
Nouveau test : une réponse portant un fait narratif et un savoir de PNJ, appliquée,
sauvegardée, rechargée, puis affichée.

---

## Phase 3 — Un seul mode d'ajout persistant

**Constat.** `enrichir`, `enrichir_joueur`, `enrichir_savoirs` et `etablir_faits`
créent tous un fait typé attaché à un ancrage. Ils occupent quatre modes, quatre
catalogues et quatre schémas dans `mj.py:699-702`.

- `faits_locaux.TYPES` reçoit `facette_personnage`, `profil_joueur`, `savoir_pnj`.
  Les validations restent dans `enrichissement.py`, `profil_joueur.py` et
  `connaissances.py` ; `preparer_faits` les appelle.
- `faits_narratifs_proposables` regroupe les catalogues : supports, locuteurs,
  évolutions, personnages, joueur, savoirs.
- Les données restent aux mêmes endroits de la sauvegarde : aucune migration.
- Modes restants : `dialogue`, `action`, `conversation_pnj`, `etablir_faits`.
  `conversation_pnj` reste distinct, car il modifie des engagements, pas des faits.
- Fusionner les audits `portee_narrative` et `coherence_physique` en un seul appel
  lorsque les deux s'appliquent à la même proposition.

**Tests.** Les tests d'enrichissement, de savoirs et de profil passent par le nouveau
type sans changer leurs assertions sur l'état et le rechargement.

---

## Phase 4 — Nouveau contrôle narratif (cœur de la migration)

**Constat.** `narration.controler` exige la reproduction exacte d'une attestation
(`narration.py:136-139`) et réécrit le reste : une phrase neutre devient « Je ne peux
pas encore l'établir. », une hypothèse est enveloppée d'un avertissement.

### Verdicts

| Verdict | Signification | Traitement |
|---|---|---|
| `neutre` | aucune affirmation sur le monde | affiché tel quel |
| `hypothese` | possibilité présentée comme telle | affiché tel quel |
| `ambiance` | aspect sensoriel sans entité mécanique | affiché tel quel, enregistré |
| `parole` | propos nouveau d'un PNJ présent | contrôle actuel du locuteur et de la citation |
| `mecanique` | affirmation sur un domaine mécanique | sources obligatoires, vérifiées par le moteur |
| `invention_protegee` | entité ou fait mécanique nouveau | révision ; passer par `etablir_faits` |
| `contradictoire` | contraire à l'état | révision |

### Garde-fous déterministes, dérivés de l'état

1. **Lexique des entités** : noms et alias de tous les objets du monde, y compris
   cachés, plus les noms des salles et des PNJ. Calculé depuis `monde.objets` et
   `monde.data["salles"]`, sans liste de mots écrite à la main.
2. Un alias d'entité **non perçue et non connue** du joueur dans le texte entraîne un
   refus, quel que soit le verdict de l'auditeur (fuite de secret).
3. Un alias d'entité connue impose un segment `mecanique` citant `objet:<id>` ; le
   moteur vérifie que l'identifiant est perceptible ou mémorisé.
4. Pour `ambiance`, l'auditeur liste les `entites_evoquees` ; aucune ne doit
   appartenir au lexique des entités mécaniques. Elles sont enregistrées comme
   éléments d'ambiance du lieu.

### Rendu et persistance

- Le texte accepté est affiché **tel que Luna l'a écrit**. Supprimer les réécritures
  de `narration.py:151-154`.
- `narrations_mj` reçoit `salle` et `ambiance: [{"texte", "entites"}]` ;
  `narration.verifier` est mis à jour.
- Nouveau fait de contexte `ambiance_etablie` : les éléments d'ambiance du lieu
  courant, pour la continuité entre les tours.
- `attestations` reste fourni comme aide, sans exigence de correspondance exacte.
- Le repli après trois échecs reste en place.

### Limite à documenter

Une contradiction mécanique formulée sans nom d'entité (« la pièce est plongée dans le
noir » alors qu'elle est éclairée) dépend encore du jugement de l'auditeur. Le banc
mesure ce résidu ; s'il est significatif, ajouter des prédicats dérivés des catégories
d'état (niveau de lumière, présence des PNJ, état des passages), pas des exemples.

### Tests

- Le cas réel : « je fredonne doucement » affiche une phrase naturelle, enregistrée
  et identique après rechargement.
- Un texte d'ambiance accepté est affiché mot pour mot et présent dans
  `ambiance_etablie` au tour suivant, après rechargement.
- L'alias de l'anneau encore caché, classé `ambiance` par un auditeur simulé fautif,
  est refusé par le garde-fou lexical et jamais affiché.
- « Un garde entre dans la pièce » est classé `invention_protegee` et révisé.
- Une parole de PNJ garde son contrôle de locuteur et de citation.
- Réécrire les tests de `test_narration.py` et `test_portee_narrative.py` qui
  supposent la correspondance exacte.

---

## Phase 5 — Matérialisation à la demande

**But.** Un élément d'ambiance devient interactif quand le joueur le cible, par le
pipeline `objet` / `detail` / `qualification` qui existe déjà.

- Quand une cible ne correspond à aucun objet (`monde.trouver`, ou cible inconnue
  dans une proposition) mais correspond à un élément de `ambiance_etablie` du lieu,
  le MJ reçoit `ambiance_ciblee`. Il doit alors :
  - proposer un `objet` ou un `detail` ancré sur un support réel, via `etablir_faits` ;
  - ou répondre que l'élément n'est pas manipulable (une odeur, une lueur).
- L'intention initiale est ensuite réexaminée sans que le joueur la répète. On
  généralise le chemin `suite_qualification` de `mj.py:593-603` en un réexamen commun
  après tout fait établi.
- En ligne, une commande locale dont la cible est inconnue est transmise au MJ au
  lieu d'afficher une erreur (`jeu.py`, autour de la ligne 280).
- Point d'accroche pour le budget d'invention de la phase 9.

**Tests.**
- « Des gravats jonchent le sol », puis « je ramasse un gravat » : objet créé, pris,
  présent dans la besace après rechargement, absent de la carte.
- « Une odeur de vase », puis « je prends l'odeur » : aucun objet créé, réponse non
  manipulable, état inchangé.
- Une cible jamais évoquée suit le chemin habituel.

---

## Phase 6 — Boucle d'outils

**Constat.** Un seul appel `repondre_au_joueur` choisit parmi plusieurs modes et
schémas ; les corrections sont des rappels complets écrits à la main
(`mj.py:518-570`, `577-591`, `593-603`, `616-636`, `938-940`).

- Outils : `proposer_action` (simple, composée, improvisée, fabrication),
  `etablir_faits`, `converser_pnj`, `repondre` (texte final).
- Boucle bornée à quatre appels d'outil par tour. Chaque appel est validé par le
  moteur sur la copie de travail ; la sortie de l'outil renvoie
  `{accepte, obstacle, faits_produits}`. Luna corrige à partir de cette sortie.
- Les faits acceptés s'accumulent dans `_transactions` (phase 2). Une action acceptée
  termine la boucle : exécution directe ou attente de « tenter », comme aujourd'hui.
- `repondre` passe par le contrôle de la phase 4 ; un refus revient comme sortie
  d'outil plutôt que par un nouvel appel avec tout le prompt.
- L'interface `echanger(monde, intention, proposition_en_attente)` et la forme de la
  réponse ne changent pas : `jeu.py`, la TUI et `comparaison.py` restent intacts.
- L'audit de couverture d'action (`couverture_action.py`) est conservé ; le banc dira
  s'il peut être fusionné avec la validation de `proposer_action`.

**Prérequis.** Un essai court pour vérifier que les deux transports
(`_appeler_brut` en API et en forfait, avec `store: false` et le flux) acceptent le
renvoi des éléments `function_call` / `function_call_output` d'un même tour, ainsi
que, si nécessaire, des éléments de raisonnement.

**Tests.** Client simulé jouant des séquences d'outils : refus puis correction ;
fait puis réponse ; action avec jet ; dépassement de la borne de quatre appels. Les
tests qui simulent `_appeler_brut` par réponse unique sont à adapter : c'est le
principal coût de la phase.

---

## Phase 7 — Élagage du prompt

**Constat.** Environ 4 400 mots d'instructions, 5 200 avec l'atelier et le
franchissement, dont une large part d'interdictions nées d'un bug précis.

- Classer chaque règle de `CONVERSATION`, `NARRATION` et des `REGLES_*` :
  1. description d'un champ → description de paramètre de l'outil ;
  2. déjà imposée par le moteur → supprimée ;
  3. ton et style → prompt de base ;
  4. consigne propre à un exemple → supprimée, puis vérifiée au banc.
- Objectif : prompt de base inférieur à 1 500 mots. Les dossiers de l'atelier et du
  franchissement restent fournis seulement quand ils s'appliquent.

**Critère de sortie.** Le banc ne montre pas plus de refus ni de contradictions qu'en
fin de phase 6.

---

## Phase 8 — Récit des résultats par Luna

- `conclure` (`jeu.py:156`) appelle `raconter_resultat` avec les lignes du journal
  du moteur.
- Contrôles : phase 4, plus deux garde-fous déterministes : tout nombre du texte
  figure dans le résultat ; tout alias d'entité figure parmi les entités du résultat
  ou les entités perceptibles.
- Repli sur le texte du moteur en cas d'échec ; option `--recit-moteur` pour garder
  le rendu actuel et éviter l'appel supplémentaire.

**Tests.** Récit simulé annonçant 5 PV perdus au lieu de 3 : refusé, texte du moteur
affiché. Récit fidèle : affiché, enregistré, identique après rechargement.

---

## Phase 9 — Habillage des salles et budget d'invention

- Généraliser `espace.a_completer` : à la première interaction avec le MJ dans une
  salle non habillée, un appel produit l'ambiance et zéro à quelques détails ou
  objets, validés par `etablir_faits` et sauvegardés avant la réponse.
- Données de scénario par salle, `potentiel_invention` : nombre maximal d'objets
  créés, masse maximale, capacités permises, catégories exclues. Contrôle dans
  `faits_locaux.preparer_faits`, donc aussi pour la matérialisation de la phase 5.
- Hors ligne : aucun habillage, comportement inchangé.

**Tests.** Budget épuisé : la proposition suivante est refusée, l'état est inchangé.
Habillage persistant après rechargement et non régénéré.

---

## Phase 10 — Gameplay

À lancer une fois le banc stable. Toutes ces mécaniques sont des données de scénario
plus des règles générales du moteur.

1. **PNJ réactifs** (`donjon/pnj.py`) : à l'avancée du temps ou après un son au-dessus
   d'un seuil, un PNJ doté de `reactions` se déplace vers la source le long du graphe
   de `sons.portee`. Les portes fermées ou calées le bloquent. Appel depuis
   `Moteur._terminer_etape` ; Luna ne fait que donner la voix.
2. **Horloges d'environnement** : `horloges` dans le scénario, déclenchées par
   `minutes`. Exemple pour le Relais : niveau de crue qui inonde les salles d'altitude
   inférieure, éteint les sources et change les passages. Même modèle déclaratif que
   `transitions_scenario`.
3. **Composition étendue** : `ouvrir`, `fermer`, `deverrouiller`, `crocheter`,
   `couper` et `bloquer` deviennent des opérations de `operations.py` ; les commandes
   locales sont traduites vers elles, comme `prendre` aujourd'hui.
4. Ensuite seulement : lumière par case, fragments après une coupe complète, nouveaux
   profils d'artisanat (lien, planche, torche de fortune).

---

## Risques

- **Phase 4** : le résidu probabiliste se déplace de « phrase prouvée » vers
  « contradiction détectée ». Le banc doit le mesurer, et la documentation le dire.
- **Phase 6** : le comportement du transport forfait avec `store: false` dans une
  boucle d'outils est à vérifier avant de s'engager.
- **Coût** : la phase 8 ajoute un appel par action ; les phases 6 et 7 doivent
  d'abord en retirer davantage. Le banc arbitre.
- **Sauvegardes** : les phases 2 et 3 ne déplacent aucune donnée. Les phases 4 et 9
  ajoutent des champs ; le README précise déjà que la compatibilité des anciennes
  sauvegardes n'est pas garantie.
