# Rapport : l'ancien son fondu dans l'ouïe commune

Branche `ouie-commune`, partie d'`origin/main` cd38352, poussée sur `origin`, non fusionnée. Détail
dans `docs/plan-ouie.md`, section « L'ancien son fondu dans l'ouïe commune ».

## Causes

Deux systèmes de son coexistaient :
- **L'ouïe commune** : distance en cases, portes, seuil de chacun, interprétation.
- **L'ancien son** (`sons.appliquer`), pour l'appel à l'aide, le cri, le sifflement du joueur, le son
  d'un objet et l'appel à l'aide d'un PNJ (`ecoute.appel`, en double) :
  - une portée salle par salle, sans distance ;
  - une humeur « inquiet » ou « méfiant » forcée ;
  - un souvenir `son` à part (`esprits.entendre`) ;
  - un réflexe déclaré (`reaction_son`, `pnj.reagir`) qui faisait rejoindre l'origine d'office, ou
    accourir le protecteur d'un protégé reconnu de façon omnisciente.

Un même cri ne s'entendait donc pas pareil selon son auteur, et le réflexe court-circuitait le devoir
et le courage.

## Règles changées (fonctions)

1. **Une seule ouïe.**
   - Les sons du joueur, des objets et les sons improvisés retentissent par `ouie.retentir`
     (paramètre `force`), depuis `moteur._terminer_etape`, avec leur nature donnée par
     `sons.nature_emise`.
   - Natures déclarées dans `ouie.NATURES` : appel et cri sont des appels, le sifflement un fracas.
     Le son d'un objet dépend de sa sonorité (`ouie.SONS` : 1 un geste, 2 un fracas, 3 un appel).
   - `sons.portee`, `liens` et `auditeurs` sont retirés. `data["sons"]` reste l'historique de ce qui
     est émis, avec ceux qui l'entendent par l'ouïe commune (`sons.entendants`).
   - Les paroles que le MJ prête aux PNJ sont entendues de ceux qui en saisissent les mots
     (`ouie.saisissent`, dans `narration` et `faits_locaux`).
   - L'humeur liée au tapage du joueur se calcule sur ceux qui entendraient un fracas.
2. **Le réflexe devient une donnée de l'ouïe.**
   - Le seuil d'alerte est dans le profil (`alerte`, en crans, vérifié par `verifier_profil`).
   - `deliberation.alarme` envoie voir avant tout le reste (but `voir`, motif devoir) dans deux cas :
     - un bruit inconnu venu d'un autre lieu qui lui est parvenu à ce seuil ;
     - l'appel d'un protégé dont il a reconnu la voix.

     Les autres bruits suivent `bruit_a_voir` (devoir de garde, courage).
   - Un appel porte la voix : qui la connaît sait qui crie (`ouie.entendre`, `voix.reconnaitre`) et
     le croit là. Le bruit retenu le nomme (`qui`).
   - Un personnage sans profil retient le bruit sans délibérer (`ouie._retenir_seulement`).
   - `pnj.reagir` est retiré. Une partie qui porte encore `reaction_son` est refusée (pas de
     migration).
3. **Plus d'humeur forcée** : l'inquiétude ne vient que de l'ouïe commune (`deliberation.inquieter`).
4. **Un seul souvenir.**
   - Le souvenir `bruit` de l'ouïe commune garde le lieu, la nature, le niveau le plus fort et
     éventuellement `qui`.
   - `esprits.dernier_son`, que reçoit le MJ, le lit.
   - `esprits.entendre` et la migration de `dernier_son_entendu` sont retirés.
5. **L'appelé se tourne vers la voix** (`ouie._vers_la_voix`) : vers l'appelant dans sa salle, sinon
   vers le seuil par où la voix arrive. La rotation prend son temps (« se tourne vers la voix qui
   l'appelle »), et il peut ainsi voir l'appelant. Nouvelle mesure du banc : `vers_la_voix` (ainsi
   que `appels_a_l_aide`).
6. **La réponse au joueur hélant** se décide après que les PNJ ont vécu ses 3 secondes de cri :
   `pnj.repondre` est appelé après `avancer`, dans `moteur._terminer_etape`.

## Données migrées

- Auberge : Hugues passe de `reaction_son: {seuil: 2}` à `profil.alerte: 3`.
  - L'ancien seuil 2 valait un appel d'une salle voisine ouverte.
  - Le même appel, venu de la cuisine, lui parvient à 3 crans.
- Aucun autre scénario ne déclarait de réflexe.

## Cas vérifiés après rechargement

Nouveau fichier `tests/test_ouie_commune.py`, plus les tests adaptés de `test_sons`, `test_reactions`,
`test_protection`, `test_improvisation`, `test_narration`, `test_securite`, `test_eau`, `test_esprits`
et `test_rejeu`.

- **Appel du joueur derrière la porte étanche fermée** :
  - il parvient à 6 crans contre la porte et à 3 au fond des vannes (avant : le même niveau dans toute
    la salle) ;
  - au seuil d'alerte 5, le proche accourt et le lointain non ;
  - Gorm alerté va chercher la clé du relais ; attendu d'un bloc ou découpé en rotations rechargées,
    le monde est le même.
- **La cloche du Relais**, sonnée de la galerie : elle parvient au refuge comme un appel, et Gorm ira
  voir.
- **Un protégé qui crie** : Ilse appelle, Gorm reconnaît sa voix et accourt. Sans connaître sa voix,
  il n'a pas d'alarme.
- **Le gardien au seuil d'alerte bas** (cas réel) : Hugues accourt à l'appel venu du couloir ; Odile
  non.
- **L'appelé qui se tourne** :
  - Gorm, hélé dans son dos, se tourne, voit le joueur et répond ;
  - appelé d'une autre salle, il se tourne vers le passage.
- **La réponse au joueur** est datée de la fin de ses 3 secondes de cri.
- **`VERIFIER`** passe sur une nuit de 8 h de chaque scénario.

Suite complète : 1098 tests passent, 18 sautés (14 sans `jsonschema`). Node est présent : les tests
du clic ont tourné.

## Bancs 8 h

`main` cd38352 puis la branche. Relais 8 graines, mine, auberge et crue 4 graines. Moyennes par nuit,
`main` → branche.

| | Relais | Mine | Auberge | Crue |
|---|---|---|---|---|
| appels (héler) / réponses | 1,25 / 1,13 → égaux | 2,75 / 2,25 → égaux | 6,75 / 2,25 → 5,25 / 1,75 | 2,5 / 2,5 → égaux |
| retrouvailles | 1 → 1,13 | 2,25 → 2,25 | 2 → 1,5 | 2,25 → 2,25 |
| appels à l'aide | 0,38 → 0,38 | 3 → 3,25 | 2,25 → 3,25 | 0 → 0 |
| allés voir | 9,25 → 9,25 | 13,75 → 18,25 | 39,25 → 35,25 | 12,75 → 12,75 |
| bruits inconnus | 50,25 → 50,25 | 57,5 → 62 | 134,5 → 126,75 | 75 → 75 |
| retournements | 145,1 → 144,9 | 164,5 → 167,3 | 119 → 113 | 153 → 153 |
| tournés vers la voix | → 0,88 | → 1,5 | → 1,25 | → 0,75 |
| sécurité en fin de nuit (moyenne des PNJ) | 0,1 → 0,1 | 33,3 → 29,9 | 19,3 → 21,9 | 5,4 → 5,4 |
| vols vus | 0,88 → 0,88 | 1 → 1 | 0,5 → 0,75 | 0 → 0 |
| sans recours / en attente | 53,8 / 66,3 → égaux | 55 / 281 → 55 / 279 | 43,8 / 541 → 30 / 541 | 15 / 107,5 → égaux |
| temps d'une nuit | 6,3 → 6,2 s | 23,7 → 22,3 s | 17,9 → 17,8 s | 7,9 → 8,4 s |

Aucune usurpation ni violation (le banc vérifie l'état à chaque pas). Les nuits sont toutes
distinctes, des deux côtés. Les temps ne sont pas comparables : `main` a été mesuré pendant la suite
de tests, la branche au calme.

Écarts :
- **Relais et crue** : mêmes nuits, sauf que l'appelé se tourne vers la voix. Au Relais, graine 3,
  Aubin hélé par Gorm se tourne vers sa voix et le retrouve, au lieu de cesser de l'attendre.
- **Mine** :
  - Lucien, blessé, appelle à l'aide. Rémy, qui le protège, et Mathe reconnaissent sa voix et accourent
    par le but « voir » : Rémy passe de 7 à 17 « va voir » sur les quatre nuits.
  - Avant, le réflexe les faisait rejoindre l'origine sans ce but, donc sans être comptés.
- **Auberge** :
  - Hugues n'accourt plus qu'à un bruit qui lui parvient à 3 crans (68 → 54 « va voir »).
  - Les nuits se décalent ensuite : moins d'appels par le nom, plus d'appels à l'aide d'Anselme,
    moins de minutes sans recours.

## Limites

- Un personnage sans profil (la crypte) retient le bruit sans y réagir.
- Le seuil d'alerte est une constante du profil, pas un état. Il ne vaut que pour un bruit venu d'un
  autre lieu.
- Un appel ne fait reconnaître qui crie qu'à qui connaît sa voix, et une voix inconnue n'est pas
  retenue à cette occasion.
- La nature du son d'un objet tient en trois paliers de sonorité.
- L'appelé d'une autre salle se tourne vers le seuil, pas vers l'appelant.
- Défaut déjà présent sur `main`, laissé hors de ce chantier : dans la scène de la protection (Ilse à
  bout dans l'échoppe obscure), découper le temps change la minute d'une croyance (le brasero éteint
  revu), sans en changer la valeur. Le test de découpage de la branche porte sur l'appel derrière la
  porte.

## Branche et commit

Branche `ouie-commune`, poussée sur `origin`. Dernier commit : voir `git log -1 origin/ouie-commune`
(message « L'ancien son fondu dans l'ouïe commune… »).
