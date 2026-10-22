# Rapport Codex 7 — le corps blessable (4a)

Branche `codex-force-4a`, non fusionnée, partie de `97af140`. Référence de comportement :
`origin/main` au commit `06602a67ed2ac84835a4255039ef2d65a008ff8e`. Aucun changement de `main`,
aucune PR, aucun appel au modèle. Luna reste `gpt-6-luna`.

## Règles et fonctions

- `corps.installer`, `pv`, `blessure`, `malus` : PV pour tous, maximum déclaré ou 6 + FOR de base ;
  blessures déduites des seuils 2/3 et 1/3, sans liste d'exceptions. Les malus passent par les
  caractéristiques communes, même pour un personnage sans profil.
- `corps.vivre` et `vecu` : une heure de repos conscient soigne 1 PV. Le cumul `corps.soin` est en
  minutes, calculé en dixièmes entiers ; effort et interruptions ne perdent pas les fractions.
- `corps.perdre`, `endormir`, `reveiller`, `ranimer`, `conscient` : PV 0 donne une inconscience
  de 30 + d20 minutes, réveil à 1 PV ; autre inconscience 5 + d20. Les dates et le jet sont sauvegardés.
  L'inconscience interrompt le geste et son registre, efface l'intention, fixe `libre` au réveil,
  et neutralise l'activité vécue. Le corps continue de vivre indépendamment de la délibération.
- `pnj._avancer` : réveils à leur instant, y compris sans aucun PNJ. L'inconscient ne voit,
  n'entend, ne délibère, ne parle, ne témoigne ni ne s'écarte. La case reste occupée. Les appels
  peuvent encore viser quelqu'un que l'appelant croit vivant ; l'absence de réponse se retient.
- `planification.ranimer`, geste déclaré et candidat de devoir : un protecteur rejoint son protégé
  qu'il croit inconscient, puis le ranime au contact après une minute au moins. Le devoir est relancé
  lors du constat. Le plan ne lit ni PV ni date de réveil du protégé. Le joueur a `ranimer <personnage>`.
- `Moteur._attendre_reveil` : après une chute à 0 PV, le joueur perd connaissance ; les PNJ vivent
  jusqu'au réveil dans la même action. L'affichage ne révèle pas leurs gestes survenus pendant
  l'absence. La suite d'une manœuvre s'arrête après cette perte de connaissance.
- `corps.mourir` : type `depouille`, même identifiant et place, masse 70 kg par défaut ; profil
  archivé dans `defunts`, esprit retiré, pas d'orientation, biens conservés et explicitement au mort.
  Les références historiques (propriétaire, fonds, savoirs, paroles anciennes, protégé, conditions)
  restent valides ; les engagements envers le mort échoient. Une charge envers quelqu'un qu'on
  sait mort cesse d'appeler une action. Sans découverte ni parole, on ne sait pas sa mort.
- `esprits.constater`, `social` : une dépouille vue établit `mort`, un souvenir `mort_vue` et
  l'inquiétude ; la nouvelle se transmet avec le jugement et la confiance ordinaires du ouï-dire,
  sans désigner un coupable. Le genre du défunt est archivé séparément du corps.
- Scène, carte, page et contexte du MJ : blessures qualitatives, inconscient à terre sans regard,
  dépouille. Aucun PV de PNJ ni date de réveil ne sont exposés au joueur ou au MJ. Le rejeu, outil
  omniscient, montre les PV et la conscience. Les locuteurs autorisés excluent les inconscients.
- Mort du joueur : `fin` persistante ; moteur et boucles terminal/page refusent la poursuite.
  La sauvegarde est conservée. Aucun geste violent ni action `tuer` ne sont introduits.
- Banc : `--etat personnage:inconscient`, `:mort`, `:blesse:pv`, répétable ; transitions du moteur,
  mesures physiques et section « Violences et corps » seulement si un événement du corps existe.

`Monde.verifier` contrôle notamment les PV bornés, PV 0 ⇒ inconscience, l'absence de geste d'un
inconscient, son réveil cohérent, les dépouilles sans esprit/profil/orientation et la fin persistante.

## Cas vérifiés

`tests/test_corps_blessable.py` contient 16 tests (sous-cas compris dans leurs méthodes) :

- PV déclarés et calculés, blessures du joueur, d'Ilse et d'Aubin, effets sur les jets, recharge ;
- repos/effort interrompu, fractions de repos sauvegardées, même soin avec un autre découpage ;
- Ilse et Aubin inconscients : aucune perception, ouïe, parole, intention ni déplacement, mais faim
  qui évolue ; positions et croyances contrôlées après recharge ;
- Ilse et un autre protégé ranimés par Gorm ; réveil naturel à PV 0 ; même état complet après un
  laps d'un bloc ou découpé et rechargé ;
- action locale de réanimation, refus motivés avec `attendu`, délai et contact ;
- états visibles et contexte du MJ sans PV, corps interne ni réveil ;
- dépouilles d'Aubin à la galerie du beffroi et de Brune au refuge, biens et découverte ; nouvelle crue sans coupable ; décès de
  chaque PNJ des quatre scénarios, attente et rechargement sans référence invalide ;
- deux sources de chute, puis vrais sauts de la terrasse sur échec et réussite : 0 PV, réveil à
  1 PV, scène de réveil et sauvegarde cohérente ;
- joueur mort, sauvegarde rechargée close, action moteur et commande de page refusées ; invariants
  volontairement brisés refusés.

Le test historique de faim extrême utilise désormais `ecouter`, qui ne soigne pas, pour isoler
la perte de PV. Attendre rend désormais 1 PV/h et compense sinon cette perte : la règle du test
reste « affaiblir sans tuer », sans empêcher le nouveau repos qui soigne.

## Mesures et critère

**Suite complète verte : 1298 tests, quatre sautés** faute du SDK Anthropic facultatif, 163,127 s,
123 fichiers isolés, quatre processus à priorité réduite. Le test du rejeu vérifie désormais les
PV et la conscience ajoutés aux pistes, en plus des positions et regards ; les 16 tests 4a
passent. Le placement final d'Aubin à la galerie et de Brune au refuge est aussi revérifié
après la suite, avec sauvegarde/rechargement. Rapport détaillé :
`artifacts/force-4a/tests-finaux-verts.json` et sortie `tests-finaux-verts.txt`.

**Comportement : critère atteint.** Vingt nuits de huit heures : Relais, graines 1985, 7, 42,
2024, 3, 11, 99, 500 ; mine, auberge et crue, les quatre premières. Chroniques, mesures,
souvenirs et récits sont strictement identiques à la référence. Les champs préexistants des
états finaux et les empreintes physiques aux minutes 5, 60, 120, 240 et 480 sont identiques.

Normalisation limitée aux champs ajoutés : PV/PV max des objets personnages, `corps.inconscient`
et `soin` des personnages et du joueur, `blessure` et `conscient` des croyances d'état. Les anciens
PV du joueur restent comparés. Pour l'empreinte physique, qui exclut déjà corps/profil, seuls
les deux nouveaux champs PV des personnages sont exclus en plus. Aucun écart préexistant n'est
masqué, aucune normalisation de la chronique, des mesures, du récit ou des souvenirs.

Quatre nuits de huit heures, graine 1985, avec `planification.VERIFIER=True` et
`spatial.VERIFICATION=0.2` : aucun écart ni plantage ; mêmes états complets et récits que sans
contrôle. Les 26 nuits de branche, contrôles et épreuves atteignent toutes la minute 480,
sans usurpation ni violation. Les archives ont été relues et leurs SHA-256 revérifiés.

**Temps : seuil respecté sur les moyennes appariées**, pas une borne garantie pour chaque
chronométrage. Python 3.14.3 identique des deux côtés, graine 1985, huit heures, un processus à
priorité réduite ; pour chaque passe, référence puis branche, sans ma suite de tests en parallèle.

| Scénario | Paires | CPU référence (s) | CPU branche (s) | Écart CPU | Écart mural |
|---|---:|---:|---:|---:|---:|
| Relais | 2 | 5,117 | 5,336 | +4,27 % | +4,28 % |
| Mine | 2 | 10,875 | 11,094 | +2,01 % | +1,79 % |
| Auberge | 2 | 12,211 | 12,617 | +3,33 % | +4,16 % |
| Crue | 3 | 9,505 | 10,234 | +7,67 % | +7,09 % |

Les mesures sont variables sur ce poste utilisé par d'autres travaux : Relais +14,76 % puis
−6,50 %, mine +21,06 % puis −15,16 % ; une troisième paire de crue donne +2,06 %. Ces moyennes
sur une graine ne démontrent pas une limite de +10 % sur toutes les nuits. La passe de vingt
nuits sous quatre processus de tests concurrents avait des temps plus hauts, conservés dans les
artefacts mais exclus de cette comparaison de performance. Aucun gain de vitesse n'est revendiqué.

Épreuves de huit heures au Relais, graine 1985, départ tiré :

- `ilse:inconscient` : Ilse reste inconsciente 5,731667 minutes ; Gorm la ranime à l'instant 3439
  (5 min 43,9 s), une réanimation, aucun mort. Avant le réveil : corps vivant, pas de perception
  ou d'action. Le cas d'Ilse au refuge est également exercé en test après rechargement.
- `aubin:mort` : un mort, trois découvertes : Brune minute 1, Ilse minute 2, Gorm minute 28 ;
  Brune annonce sa mort à Gorm à la minute 2, qui doute. Le départ tiré place Aubin au refuge ;
  le placement du corps peut être changé par une donnée de scène, sans règle liée à son nom.

Une première passe avait révélé un éveil supplémentaire quand les besoins visibles changeaient.
La correction porte sur le contrat commun d'événement : les nouveaux changements de blessure
et de conscience éveillent ; les besoins ordinaires conservent leur cadence précédente. Les
vingt nuits restent ensuite identiques. Le dernier ajustement des textes `attendu` de réanimation
ne change aucune transition réussie et est vérifié par les tests de refus.

Artefacts locaux : `artifacts/force-4a/rapport-branche3.md`, `comparaison-troisieme.json`,
`synthese-branche3.json`, `temps-apparies.md/json`, les dossiers `reference-*`, `branche3-*`,
`verifier3`, `epreuve3-ilse` et `epreuve3-aubin` (JSON, états complets, récit et rejeu HTML).
Le comparateur et le lanceur de tests proviennent de `origin/codex-outils` `60b8716`, sans fusion
de cette branche. Le collecteur local emploie jusqu'à quatre sous-processus indépendants car le
pool Windows du comparateur est interdit en sandbox. Le moteur et les nuits ne sont pas modifiés.

Commandes de contrôle et d'épreuve équivalentes :

```powershell
C:\Users\msics\donjon\.venv\Scripts\python.exe -m unittest discover -s tests -q
C:\Users\msics\donjon\.venv\Scripts\python.exe -m donjon.banc_pnj --scenario relais --heures 8 --graines 1985 7 42 2024 3 11 99 500 --processus 4
C:\Users\msics\donjon\.venv\Scripts\python.exe -m donjon.banc_pnj --scenario relais --heures 8 --graine 1985 --etat ilse:inconscient --processus 4
C:\Users\msics\donjon\.venv\Scripts\python.exe -m donjon.banc_pnj --scenario relais --heures 8 --graine 1985 --etat aubin:mort --processus 4
```

Les commandes exactes du collecteur (comparaison avec état complet, empreintes normalisées,
paramètres `VERIFIER`, mesures appariées et répertoires de sortie) sont conservées dans les
rapports locaux ci-dessus. Les bancs utilisent Python 3.14.3 parce que le `.venv` était absent
au premier relevé ; la suite utilise le `.venv` créé en Python 3.13.7, avec les dépendances du
README et `jsonschema`. Aucun test ni banc ne nécessite de clé ou de requête au modèle.

## Limites

- Le périmètre s'arrête à 4a. Pas d'attaque, d'arme sur une personne, de `tuer`, de lien, de soin
  actif, de fuite ou de reddition. Les autres recommandations du plan restent une conception.
  Douceur 100 garde la possibilité future de défendre soi-même ou un protégé.
- La réanimation suit la convention des gestes courts : effet au début, auteur occupé 10 s.
  Le registre à issue différée des gestes longs est prévu en 4d.
- Les dégâts naturels de faim/froid restent ceux du joueur ; aucun nouveau dégât naturel de PNJ
  n'est ajouté dans ce lot. Faim, froid et eau ne donnent jamais la mort en 4a.
- Les contradictions narratives restent en partie sémantiques ; aucune liste de formulations,
  de personnages ou de faits n'a été ajoutée au prompt. Aucun banc Luna n'est nécessaire à ce lot
  du moteur. Le contrôle des locuteurs et des entités perçues est déterministe.
- Aucune migration d'anciennes parties n'est garantie. Les champs des nouveaux mondes sont
  installés et les sauvegardes créées par cette branche sont vérifiées après rechargement.
- Les artefacts volumineux restent locaux dans `artifacts/force-4a/` ; les chiffres utiles et les
  commandes reproductibles figurent dans ce rapport.
