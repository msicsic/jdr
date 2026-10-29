# Lot 277 — demander l'allumage d'un foyer fixe pour soi

Branche `codex-allumer-pour-soi`, **non fusionnée**. Raccord validé sur
**`9ff488b`**, référence **`bca5061`** : **410 tests verts, 20/20 paires
4 h sans hausse de suspects, aucun plantage**, `raccord-266/fin.json`,
`ok=true`. Intégrations fusionnées sans rebase : `59a1388` (266), puis
**`88e54a9` avec `30d4611` (280 et 281)**. Seuls conflits documentaires ;
le second raccord moteur change uniquement `reagir` pour nommer le protégé,
sans toucher les fonctions 277. Rejeu de cette dernière fusion : **81 tests
verts dans huit fichiers, zéro échec/erreur/saut, 190,888 s**, deux processus
réduits. Fichiers : les quatre régressions, `test_allumer_pour_soi`,
`test_but_protection`, `test_taches_payees`, `test_planification`.
**Aucun nouveau banc** : les vingt paires ci-dessous restent celles de `9ff488b`.

**Invariant et réalisation.** Un foyer mécanique fixe cru éteint et chargé,
utilisable sans faute, hors de l'eau attendue et sans fin connue, offre
`confier` gratuit ou `engager` payé à qui est cru porter une flamme lorsque
le demandeur n'en porte aucune. Positions et moyens viennent des croyances.
Devis, jugement, refus et exécution sont les mécanismes ordinaires ; le
plan s'arrête à la demande et aucun feu ni déplacement n'est produit à
l'accord. La parole du joueur passe par la proposition de tâche existante.
Le travail payé et son estimation restent dans le contrat connu du payeur ;
son contrôle sert le besoin courant sans devenir un nouveau devoir pressant.
Une réponse « déjà fait » déclenche un contrôle, sans créer le fait annoncé.

Fonctions touchées : `planification.Vue.__init__`, `Vue.attend_tache`,
`gestes`, `_aide_sur_place`, `_confier_tache`, `_allumer_pour_soi`, `_engager`,
`_entrees_communes` ; `echanges.engager`, `confier`, `_retenir_aide`,
`_echeance_devis`, `executer`. Ni `agendas.py`, `signes.py`,
`deliberation.py` ni prompt modifiés par 277 ; aucun appel à Luna.

**Les quatre cas de la fusion d'essai 277+280.**

- Protection, avec et sans agenda : Gorm répond à l'alarme et inspecte
  l'échoppe (600 → 836 dixièmes), puis Brune propose l'allumage payé (859).
  Le registre ajouté par 277 publiait une délégation dont le contrôle
  devenait un devoir pressant ; avec 266, Gorm finissait dans la crypte.
  La panne subsiste sans le recours et disparaît sans cette publication.
  Le contrat payé conserve maintenant son attente et son estimation, sans
  cette urgence. Assertions des deux tests inchangées.
- Voix inconnue : Odon reçoit sa part, puis 89 demandes « déjà fait » de
  Josse à Rémy évacuent le repas de la chronique bornée. La réponse positive
  est maintenant retenue pour contrôle, sans nouvel engagement ni fait créé.
  Le test de voix et ses assertions restent inchangés.
- Lucien : à 19340 dixièmes (32 min), Anselme, biens 100, va légitimement
  demander gratuitement l'allumage à Hugues ; refus à 19381, puis recherche
  d'une flamme. Sa pauvreté n'interdit plus ce recours et son départ change
  la fenêtre du vol. La prémisse « chambre sans recours de lumière » devient
  explicite : poêle connu hors d'usage, tous les buts conservés. Le recours
  vérifie aussi ce `fin` cru, sans lire l'intégrité réelle. Toutes les
  assertions restent présentes : 95 min, vol 107–110, reprise du ballot,
  recherche et recharge ; 136 changements de choix et 191 gestes, comme
  le témoin sans nouveau recours.

**Validation du raccord à 266.** 41 fichiers, **410 tests**, zéro échec,
erreur ou saut, **1 314,326 s**. Scènes d'auteur brasero/poêle : permission
de Maël, accords gratuits/payés, déplacement/allumage/chauffage réels,
parole du joueur, huit minutes en bloc/découpées. Contre-épreuves : flamme
crue éteinte, foyer vide, noyé ou connu détruit, position réelle cachée,
refus sans rappel par délai, réalisation annoncée sans fait créé.
Six captures avant/accord/travail : monde/rendu/scène identiques après
recharge. Diagnostics et ablations des quatre cas également rechargés.

**Banc 4 h, `bca5061` → `9ff488b`.** Suspects 219 par nuit :

| Scénario | 1985 | 7 | 42 | 2024 |
|---|---:|---:|---:|---:|
| relais | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| mine | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| auberge | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| crue | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| crue_hameau | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |

**Coups : 0 → 0 dans chaque nuit.** Demandes/offres naturelles d'allumage
**9 → 10** : neuf offres impossibles conservées ; seul ajout, crue/7,
**Ilse → Aubin**, poêle du guet, **218 min, instant 130969, accepté**.
Aubin allume à **131032**, puis se chauffe à **131137**, aux mêmes instants
que dans la référence : aucun gain de vitesse démontré. Aucun ajout au hameau.
S/F/D (`cats` 183) : **S total 437 → 436**, **F moyen 5,30 → 5,30**,
**D moyen 2,053571 → 2,053571**. Seul crue/7 change son triplet :
**26/6/3 → 25/6/3** ; les dix-neuf autres sont identiques.
Vingt références absentes du cache calculées une fois ; chaîne entière
**3 320,365 s**, deux travailleurs réduits au plus. Aucun temps comparé
entre campagnes.

**Limites et preuves.** Diagnostic initial 269 à 615 et 652 min : condition
admise mais aucun recours offert ; devis de Gorm toujours impossible pour
les deux foyers sur les deux captures. Le banc 4 h ne couvre pas ce coup
tardif ; aucun bénéfice universel annoncé. Anciennes sauvegardes sans
estimation : aucune date de contrôle inventée. Les corrections de fixture
et d'admission de `d306370` restent archivées ; six empreintes historiques
conservées. Les résultats antérieurs (`bbab808` / `1852d6e`) ne sont pas
ceux du raccord courant. Bruts :
`C:/Users/msics/donjon/artifacts/allumer-277/`, notamment `integration/`
et `raccord-266/{fin,tests,scenes,comparaison,bilan}.json`.
Ni suite complète ni nouveau banc après `30d4611` ; la fusion vers
l'intégration reste au superviseur. Aucun calcul actif ; résultat du dernier
rejeu : `raccord-266/tests-fusion-30d4611.json` dans les bruts.
