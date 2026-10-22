# Rapport Codex 1 — profils du Relais et de la crue

Branche `codex-profils`, non fusionnée ; référence `main` **f1eee53** du 22 octobre 2026.
Tâche : [codex-1-profils.md](codex-1-profils.md).

## Changements

Dans les deux scénarios, Brune passe à douceur 75, Ilse à honnêteté 80, Aubin à honnêteté 65
et douceur 80. Gorm reste strictement inchangé. Les traits d'Ilse et d'Aubin ne leur prêtent
plus une honnêteté sans réserve. Brune continue d'éviter la violence, compatible avec 75.

Le Relais avait déjà des valeurs explicites. Dans la crue, les anciennes limites auraient
réimposé 100 au chargement : suppression de `ne_blesse_pas` chez Brune, de `ne_vole_pas` et
`ne_ment_pas` chez Ilse, des trois chez Aubin ; `ne_blesse_pas` reste chez Ilse. Seules les
valeurs demandées sont ajoutées. L’honnêteté 50 par défaut de Brune dans la crue est
conservée, comme toutes les autres valeurs antérieures des deux scénarios. La douceur 90
d'Ilse et la fierté 70 d'Aubin du prototype historique ne font pas partie de la décision
retenue : elles restent respectivement 100 et leur valeur antérieure.

Aucun changement du moteur, des consignes ou des autres données. Six scènes de tests
posent maintenant explicitement le profil qu'elles testent : honnêteté 100 d'Ilse pour les
interdits du stratège (`test_stratege`, deux scènes ; `test_caractere`, une scène), douceur 100
de Brune pour comparer un bien d'autrui et une porte sans propriétaire (`test_petits_correctifs`,
deux scènes) et pour exclure un recours au forçage quand ses crochets disparaissent
(`test_besoins`, une scène).
Chaque adaptation porte un commentaire expliquant pourquoi le profil du scénario ne suffit plus.
Le commentaire de la scène de garde (`test_echanges_argent`) distingue aussi le droit sur la
clé de l'honnêteté d'Ilse : sans permission, la prendre reste illicite à toute valeur.

## Protocole et définitions

Graines : **1985, 7, 42, 2024, 3, 11, 99, 500**. Joueur passif à `chambre_cloche` ; départ
`tire` (option par défaut). Tous les bancs de référence sont terminés
avant modification, puis tous ceux de la branche ; jamais de référence et de branche
simultanées. Priorité BelowNormal, `--processus 4` au maximum. Aucun banc Luna et aucun
accès à `sauvegardes/`.

```powershell
python -m donjon.banc_pnj --heures 8 --graines 1985 7 42 2024 3 11 99 500 --joueur chambre_cloche --processus 4 --sortie <phase>-relais-8h.json
python -m donjon.banc_pnj --scenario crue --heures 8 --graines 1985 7 42 2024 3 11 99 500 --joueur chambre_cloche --processus 4 --sortie <phase>-crue-8h.json
python tools/audit_nuits.py jouer --scenarios relais crue --graines 1985 7 42 2024 3 11 99 500 --heures 12 --processus 4 --dossier <phase>-12h
python tools/audit_nuits.py analyser --dossier <phase>-12h --sortie <phase>-analyse.json
python tools/audit_nuits.py jouer --scenarios relais crue --graines 42 --heures 8 --processus 2 --verifier --verification 0.2 --dossier verifier-8h
```

`<phase>` vaut `avant` puis `apres`. Résultats bruts locaux, ignorés par git :
`artifacts/codex-profils/` (bancs JSON et journaux, 32 nuits 12 h compressées, analyses,
`resumer.py`, `mesures.json` et contrôles). Les tables ci-dessous conservent les chiffres utiles.

Les **vols tentés** comptent les couples distincts `(auteur, objet)` par nuit sur les gestes
illicites effectivement commencés, hors poussées ; ouvrir une réserve et manger ses vivres
comptent donc deux couples. Les **vols vus** suivent exactement le banc : mêmes couples,
mais retenus visuellement en mémoire à la fin, sans les seuls témoins auditifs. Ce ne sont
ni des parts mangées, ni un compte des coups successifs. Le registre des audits 12 h fournit
les tentatives ; pour 8 h on le tronque à 480 min. Les chroniques des bancs 8 h ont été
comparées intégralement aux préfixes des audits 12 h, ainsi que toutes leurs empreintes
aux minutes repères : identiques pour les 32 comparaisons.

Les **coups de forçage** comptent `frappe`, `frappe en vain` et le dernier coup `force` dans
la chronique ; une **cible forcée** compte seulement `force`. Le souvenir d'un crochetage
manqué porte lui aussi l'opération `forcer` : ce libellé de mémoire n'est pas un coup
physique. Les échecs de crochetage sont rapportés séparément.

## Bancs de 8 h

Moyennes exactes sur huit nuits par scénario ; avant → après.

| Mesure par nuit | Relais, avant → après | Crue, avant → après |
|---|---:|---:|
| Vols vus | 1 → 1 | 0 → 0 |
| Poussées | 0 → 0 | 0 → 0 |
| Méfiances | 1,875 → 1,875 | 1,5 → 1,5 |
| Rumeurs crues | 0,5 → 0,5 | 1,5 → 1,5 |
| Rumeurs doutées | 0,25 → 0,25 | 0,625 → 0,625 |
| Échanges | 15,375 → 15,125 | 18,125 → 18,125 |
| Achats | 2,125 → 2,125 | 2 → 2 |
| Minutes·PNJ sans recours | 60,625 → 64,375 | 16,25 → 16,25 |
| Minutes·PNJ en attente | 52,5 → 46,875 | 218,75 → 213,75 |
| Usurpations | 0 → 0 | 0 → 0 |

## Audits de 12 h

Mêmes graines et contrôles d'état du moteur à chaque pas ; moyennes exactes par nuit.

| Mesure par nuit | Relais, avant → après | Crue, avant → après |
|---|---:|---:|
| Vols vus | 1,25 → 1,375 | 0,5 → 0,625 |
| Poussées | 0 → 0 | 0 → 0 |
| Méfiances | 2,5 → 2,75 | 1,5 → 2 |
| Rumeurs crues | 0,625 → 0,75 | 1,625 → 2 |
| Rumeurs doutées | 0,25 → 0,25 | 0,625 → 1 |
| Échanges | 18,5 → 19 | 24,375 → 25,5 |
| Achats | 2,25 → 2,25 | 2,25 → 2,25 |
| Minutes·PNJ sans recours | 111,25 → 126,875 | 42,5 → 67,5 |
| Minutes·PNJ en attente | 298,125 → 245,625 | 571,25 → 499,375 |
| Usurpations | 0 → 0 | 0 → 0 |

## Auteurs et gestes

Totaux sur huit nuits, avant → après. Gorm et Ilse : **0 vol tenté et 0 vol vu** dans les
quatre lots, avant comme après.

| Scénario, durée | Brune, tentés | Brune, vus | Aubin, tentés | Aubin, vus |
|---|---:|---:|---:|---:|
| Relais, 8 h | 9 → 9 | 8 → 8 | 0 → 0 | 0 → 0 |
| Relais, 12 h | 12 → 10 | 10 → 8 | 0 → 3 | 0 → 3 |
| Crue, 8 h | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |
| Crue, 12 h | 5 → 3 | 4 → 2 | 0 → 3 | 0 → 3 |

| Scénario, durée | Coups de forçage | Cibles forcées | Crochetages réussis | Crochetages manqués |
|---|---:|---:|---:|---:|
| Relais, 8 h | 0 → 0 | 0 → 0 | 4 → 4 | 23 → 23 |
| Relais, 12 h | 0 → 12 | 0 → 2 | 8 → 7 | 51 → 49 |
| Crue, 8 h | 14 → 14 | 2 → 2 | 2 → 2 | 0 → 0 |
| Crue, 12 h | 14 → 33 | 2 → 4 | 4 → 3 | 15 → 15 |

Les coups déjà présents dans la crue 8 h sont ceux d'Ilse (graine 99 : 9 coups, une porte
forcée) et d'Aubin (500 : 5 coups, une porte forcée). Ils visent la porte étanche du beffroi,
sans propriétaire : ils ne démontrent pas qu'un PNJ lésait déjà autrui à douceur 100.
Les crochetages réussis de la crue incluent aussi les portes sans propriétaire.

Sur 12 h, Aubin devient un second auteur d'atteintes au bien d'autrui :

- **Relais 1985** : il prend le pied-de-biche à 515, frappe la réserve à 630 et la force à 635
  (6 coups), puis mange à 636. **Relais 7** : il la force à 678 après 6 coups ; il ne mange pas
  les vivres ensuite. Soit 12 coups, 2 réserves forcées, 13 gestes illicites et 3 couples
  `(auteur, objet)` tentés/vus sur le lot.
- **Crue 1985** : il prend le marteau à 579, frappe la réserve à 670 et la force à 677
  (8 coups), puis mange à 678. **Crue 2024** : il prend le marteau à 488 et force la réserve
  à 680 après 11 coups, sans en manger ensuite. Cela ajoute 19 coups et 2 réserves forcées
  aux 14 coups et 2 portes déjà présents ; 20 gestes illicites d'Aubin et 3 couples tentés/vus.
- Brune reste la seule voleuse sur 8 h. Sur 12 h elle commet moins de gestes illicites :
  Relais 75 → 70 ; crue 22 → 19. Aubin intervient sur certaines des mêmes ressources.
  Aucune poussée dans aucun des lots ; Ilse et Gorm ne volent pas dans ces nuits.

## Constats de l'analyseur

Nombre de constats sur les huit nuits de 12 h, avant → après ; une nuit peut en porter plusieurs.

| Code de l'audit | Relais | Crue |
|---|---:|---:|
| `dette_fin` | 0 → 0 | 2 → 2 |
| `eau_longue` | 0 → 0 | 4 → 4 |
| `fige_presse` | 7 → 6 | 16 → 14 |
| `illicite_entendu` | 9 → 9 | 2 → 14 |
| `voir_alterne` | 1 → 1 | 3 → 2 |

Ce sont des observations de nuits, pas des violations de `Monde.verifier`. Les atteintes
entendues supplémentaires dans la crue viennent notamment des coups d'Aubin. Des PNJ
restent sans but malgré un besoin pressant ; les données seules ne résolvent pas ce manque.
Les dettes de fin de nuit et les longues présences dans l'eau restent présentes.

## Vérifications et limites

Un défaut préexistant de `test_proto.ConsoleTests`, dans
`test_console_mj_propose_sans_agir_puis_execute_sur_tenter`, a été relevé séparément des profils :
le test simulait `echanger`, mais pas `raconter_resultat` après « tenter ». La pile montrait une
tentative HTTPS OpenAI avec sa clé explicitement factice `cle-test`. La première suite a été
interrompue à 833 tests (deux échecs de profils, ensuite corrigés ; aucune erreur, 14 sautés),
sans compter ce lancement comme une suite réussie. Le récit indisponible est maintenant
simulé pour garder le repli du moteur ; une garde `urlopen` fait échouer cette scène si elle
tente le réseau. Son rejeu ciblé passe. La suite finale enlève les clés héritées et passe le
HTTP(S) extérieur par un proxy local fermé, en conservant les services de test locaux.
Le moteur et ses transports ne changent pas.

- Suite complète verte : **1241 tests, 14 sautés** (`jsonschema` facultatif pour MiMo),
  `python -m unittest discover -s tests -q`, code de sortie 0 ; 1175,552 s observées,
  priorité BelowNormal. Les avertissements de lenteur asyncio de la TUI ne sont pas des échecs.
- `planification.VERIFIER` et `spatial.VERIFICATION` à 0,2 : deux nuits de 8 h, graine 42,
  une par scénario modifié ; aucun écart, aucune borne atteinte, aucune usurpation ni plantage.
- Aucun plantage et aucune violation du monde dans les 64 nuits mesurées ; aucune usurpation.
- Chargement, sauvegarde dans `artifacts/`, puis rechargement des deux scénarios : valeurs
  attendues conservées, même état sérialisé et mêmes traits/valeurs transmis au MJ. Comparaison
  des JSON et des profils migrés avec `f1eee53` : Gorm et tous les champs hors périmètre inchangés.
- Aucun nouveau mode, mot-clé, règle propre à une formulation, ni correction du moteur.

Les profils font varier le prix des fautes, sans garantir une occasion de fauter. Le banc 8 h
ne montre ni second voleur ni nouvelle contrainte ; l'effet net apparaît après la huitième
heure. L'attente diminue mais les minutes sans recours augmentent dans les deux scénarios
sur 12 h : ce réglage ne constitue pas une amélioration générale de l'activité des PNJ.
Ces mesures portent sur huit graines, avec joueur passif ; elles ne promettent pas une
fréquence de vol ou de violence en partie. Les anciennes sauvegardes gardent leur propre
profil ; seules les nouvelles parties prennent les données modifiées. Aucun essai Luna
n'a évalué ici la narration sémantique.
