# Rapport Codex 15 — restes des fusions

Branche `codex-restes-fusions`, non fusionnée, issue de `main` **5594028** ; tâche portée
par **78c96ae**. Worktree `tmp-worktrees/codex-restes-fusions`. Aucun changement de `main`
ni fusion des chantiers parallèles. Luna reste `gpt-6-luna`, comparaison des modèles désactivée.

## Corrections et cas vérifiés

### 1. Constat de la parole tenue à réception

`echanges.remettre` inscrivait `engagement_tenu` avant `recu`. Le crochet des relations
ne trouvait donc pas la réception qui permet d'apprendre immédiatement la réussite ; il
la mettait dans les suites à annoncer. La remise physique et le souvenir de réception
précèdent maintenant la clôture de l'engagement, comme pour une part servie. Aucun
nouveau souvenir ni effet social propre aux objets vendus n'est ajouté. Les livraisons
payées restent distinctes des dons.

`test_restes_fusions` achète réellement un objet laissé au sol, sauvegarde la promesse,
fait prendre puis remettre l'objet par les gestes PNJ, et recharge. Même chaîne pour une
part détachée d'un lot, promise et payée avant sa remise. Deux couples vendeur/bénéficiaire :
Gorm/Brune et Aubin/Ilse. Propriété et portage passent à l'acheteur ; confiance +15, dette
morale augmentée selon les valeurs du bénéficiaire ; réception et parole tenue à la même
minute ; aucune suite en attente, aucune nouvelle hausse lors d'une conversation ultérieure.
Le joueur perçoit la remise. Une réussite lointaine garde le contrat d'annonce entendue,
vérifié aussi par les tests existants de relations.

### 2. Bandes communes, hystérésis et mesures

`echanges.accueil` et `voix.repond` lisaient encore 60 au lieu des bandes de rancune et de
peur. Ils lisent maintenant la relation **perçue**, avec entrée à 40 et sortie sous 30.
Les lectures d'une relation déjà calculée sont dans `relations` (`rancune`, `peur`),
partagées avec `en_veut` et `craint`. Une voix non identifiée n'emprunte pas les axes d'une
identité seulement prétendue. Aucun seuil de refus plus fort n'est conservé.

La recherche de comparaisons numériques a aussi trouvé le seuil d'affection de l'orgueil
au passage, ainsi que les seuils des mesures de méfiance, rancune et dette. Ils sont
centralisés dans `relations` ; affection 50 et dette 20 ne changent pas. Les comptes de
méfiance et de rancune incluent désormais les bandes maintenues par hystérésis. Le contrôle
AST de `test_relations_socle` interdit les seuils numériques directs d'axes hors du module ;
la validation de la confiance d'une **croyance**, entre 0 et 1, reste distincte.

Cas après recharge : appels du joueur et d'Aubin à Ilse, peur seule puis rancune seule,
45 au départ, bande maintenue sous 40 après estompement, sortie sous 30. Réponse prononcée
et visible seulement après sortie ; accueil refusé par la rancune, sans inventer de méfiance.
Les frontières 39/40 remplacent 59/60 dans les anciens parcours. Deux scènes vérifient les
comptes du banc à 35 dans une bande maintenue. Les tests du passage conservent 49/50.
`docs/plan-relations.md` est accordé à ces règles.

### 3. Refus d'action du joueur

Les deux refus de `_preparer_references` donnent maintenant le champ et l'état reçu,
les identifiants et la condition acceptée : `fin.cause`, `auteur=joueur`, `fin=null` pour
la partie close ; `auteur=joueur`, `conscient=false`, `conscient=true` pour l'inconscience.
Aucune action n'est acceptée dans ces états. Les messages destinés au joueur restent en
français, sans les données de correction. Deux actions sont refusées dans chacun des
deux états sauvegardés, sans mutation du monde ; scène close ou inconsciente après recharge.

### 4. Dépouille, apparence et observateur

La transition `corps.mourir` retire le portrait libre du vivant, sa manière de parler et
les facettes `voix`/`temperament`. Un portrait libre peut mêler aspect et comportement :
il n'est pas recyclé comme description du corps. Le nom et le profil restent archivés ;
le portrait et la manière de parler sont également archivés dans les données internes du
défunt, absentes du contexte actuel de la dépouille. La désignation visuelle déjà établie,
les facettes physiques, les détails visibles et les biens restent disponibles. Le rendu
et le contexte montrent la blessure qualitative, sans PV ; le contexte indique la mort.

`noms.nom` prend un observateur ; `social._qui` lui passe le PNJ locuteur. Sa propre vue
et ses croyances de source vue décident de la désignation, indépendamment de la vue du
joueur. Le nom connu garde son contrat distinct.

Le parcours réel a révélé un autre reste de fusion : la projection produisait bien
`personne_<n>` pour le corps inconnu, mais `voix.reel` ne décodait que les vivants.
Les attestations narratives échouaient avant même l'appel de Luna. Le décodage partage
maintenant `noms.PERSONNES`, y compris pour une référence historique de voix reconnue.

Cas : Aubin et Brune, nom connu ou inconnu, blessure, facettes physiques et comportementales,
mort, sauvegarde, contexte et attestations, puis **examen et fouille via la référence publique**,
rechargement entre les gestes. Aucun portrait vivant ni voix dans la description actuelle ;
blessure et manteau visibles conservés. Autres scènes : Gorm voit le corps hors de la vue
du joueur, puis situation inverse ; sa nouvelle décrit selon ce qu'il sait lui-même.

`tests/data/bancs/depouille.json` prépare une dépouille vue avec ses planches. Le préparateur
de banc accepte les `etats` par `banc_pnj.appliquer_etats`, transition commune déjà utilisée
par les épreuves moteur. Le préfixe console `mj` force les intentions « je regarde le corps »
et « je fouille le corps » dans la voie de Luna. Le banc utilise uniquement une sauvegarde
temporaire et `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`.

Luna : **2 tours, 8 appels (4/tour), 15,3 s/tour**, aucun refus, repli, incident ni mention
sans fondement détectée ; rechargement sans erreur. Elle décrit le corps du vieil homme
voûté, sa blessure et les planches accessibles ; elle ne lui prête aucune parole. Le passage
précédent avec le décodeur limité aux vivants bloquait les deux tours avant tout appel.
Ces deux tours constituent une vérification de scène, pas une mesure statistique de qualité.

### 5. MiMo avec ses dépendances, sans réseau

Environnement dédié `.venv-mimo` créé dans le worktree, dépendances du README et
`requirements-mimo.txt`. Aucune installation dans le `.venv` partagé ; `.venv-mimo/` est ignoré.
Les six sous-échecs historiques sont reproduits avant correction :

- Quatre comparaisons d'état conservaient les symboles `I`/`G` des anciennes captures ;
  la vue actuelle les transforme en `L` selon la désignation publique. Les tests actualisent
  la mémoire visuelle avant de prendre l'état de référence, comme le lancement du jeu.
  Les captures réseau historiques restent intactes ; tout l'état reste comparé après refus
  et après reprise.
- Deux comptes de transports faisaient 6 au lieu de 5 : la réponse simulée d'audit omettait
  le champ obligatoire `presentation`. MiMo refusait correctement ce faux audit et le
  redemandait. Le double fournit ce champ vide ; les comptes attendus restent **5**, avec
  quatre fonctions logiques et une seule correction physique du premier JSON invalide.

L'adaptateur MiMo n'a pas changé. Les cas crypte/atelier et les deux rejets archivés passent
avec leurs contrôles d'état, d'affichage avant/après sauvegarde et de reprise. La nouvelle
suite `test_restes_fusions` réexécute ces parcours quand `jsonschema` est disponible.

## Vérifications et mesures

Suite complète partagée (`tools/tests.py --processus 4`) : **1 448 tests, 15 sautés,
aucun échec ni erreur**, 136 fichiers, 566,25 s, priorité réduite. Tous les sauts concernent
MiMo facultatif dans cet environnement ; le nouveau parcours MiMo explique le saut ajouté
aux 14 de la référence. `test_mimo`, `test_fournisseurs_jeu` et `test_restes_fusions` dans
`.venv-mimo` : **24 tests, un saut** (SDK Anthropic absent), zéro échec, 17,19 s. Les fichiers
MiMo seuls : 16 tests, un saut, verts après les six sous-échecs reproduits. Contrôles ciblés
finaux des restes et du socle : 14 tests, un saut, verts ; noms/voix/restes : 57 tests, un
saut, verts. Les changements du code n'ajoutent aucune dépendance au jeu.

### Banc rapide contre 5594028

4 h, quatre graines 1985/7/42/2024, quatre scénarios, départ tiré, salles passives du
comparateur. Référence puis branche, au plus quatre processus, après la suite complète.
Moyennes par nuit, référence → branche :

| Scénario | Échanges | Appels / réponses | Méfiances finales | Rancunes finales | CPU (s) |
|---|---:|---:|---:|---:|---:|
| Relais | 6,50 → 6,25 | 0 / 0 → 0 / 0 | 2,25 → 2,25 | 0,75 → 0,75 | 7,22 → 6,34 |
| Mine | 13,75 → 13,75 | 0 / 0 → 0 / 0 | 3,50 → 3,50 | 0 → 0 | 11,88 → 11,10 |
| Auberge | 7,75 → 7,75 | 0 / 0 → 0 / 0 | 2,75 → 2,75 | 0 → 0 | 12,56 → 12,55 |
| Crue | 6,75 → 6,75 | 1,50 / 1 → 1,50 / 1 | 2,50 → 2,50 | 0,50 → 0,75 | 8,20 → 7,96 |

- **Relais 7, minute 162** : Aubin remet les planches à Gorm. L'annonce supplémentaire
  « avoir tenu sa parole » disparaît, ainsi que ses deux auditions incidentes : Gorm vient
  de constater la remise. Sur cette nuit : échanges 9 → 8, confidences 1 → 0, paroles
  surprises 16 → 14. Les conséquences matérielles ne changent pas. La voie habituelle
  `faire_entendre` annonçait déjà la suite dans ce même échange ; le test dirigé contrôle
  maintenant le constat dès `remettre`, avant cette annonce.
- **Crue 42** : rancunes finales 0 → 1, sans modification de l'état ni de la chronique.
  La bande de Brune envers Gorm est maintenue après les refus ; le vieux comptage à 40
  l'ignorait. C'est une correction de mesure, pas une rancune nouvelle.
- **Auberge 1985, 7 et 2024** : chroniques et mesures identiques, souvenirs différents.
  Mathurine et Mireille se désignent selon leur propre vue (« la grande fille de vingt-huit
  ans », « la vieille femme menue »), au lieu de « une personne inconnue » dépendant du joueur.
  Cette conséquence vient du contrat commun de l'observateur, également corrigé pour les vivants.
- **Accueil et appels** : mêmes refus d'accueil relevés et mêmes nombres de réponses dans
  ces nuits libres de 4 h. Aucun refus supplémentaire par rancune dans leurs chroniques.
  La différence entre 40 et 60 et le maintien de bande sont démontrés par les scènes dirigées ;
  ce banc ne montre pas une variation du taux de réponse.

Les **16 nuits ont les mêmes empreintes physiques** aux repères et la même issue matérielle.
15 chroniques sur 16 sont identiques ; 12 états finaux complets sur 16 sont identiques
(les quatre différences sont celles décrites ci-dessus). Dettes morales finales,
méfiances levées et minutes urgentes sans recours restent égales dans les quatre scénarios.
**Zéro plantage, usurpation ou violation** des deux côtés. Les constats de l'audit restent
identiques : Gorm pressé sans but au Relais 1985, Josse à la mine 2024, Lucien longtemps dans
le noir à l'auberge 1985, une alternance d'examen pour Gorm aux crues 7 et 42. Ce lot ne
prétend pas corriger ces comportements préexistants.

### Contrôles renforcés

`planification.VERIFIER=True`, `spatial.VERIFICATION=1`, 2 h, graine 42, départ tiré,
chaque scénario : **quatre nuits sans erreur ni écart**. Puis `VERIFIER=True` et
`VERIFICATION=0.2`, 8 h, même graine et quatre scénarios : **quatre autres nuits sans erreur
ni écart**, zéro usurpation. Lots successifs, aucun banc simultané de ce chantier.

À 8 h : 1 218 / 901 / 766 / 1 251 reprises de mémoire et 657 / 24 / 182 / 391 reprises de
graphe (Relais / mine / auberge / crue) contrôlées par `VERIFIER`. La mine compte 17 reprises
par certificat et la crue 20. **Quatre recherches neuves atteignent leur borne à la mine** ;
ce ne sont pas des écarts de reprise détectés par les contrôles, ni une preuve d'impossibilité.
Ce lot n'a pas modifié l'exploration ou ses bornes et ne garantit pas leur absence.

Temps CPU des contrôles, 2 h puis 8 h : Relais 16,94 / 104,36 s, mine 35,56 / 164,08 s,
auberge 25,78 / 80,53 s, crue 24,00 / 53,72 s. Ils incluent les recalculs de contrôle et
ne se comparent pas au coût du banc rapide ordinaire.

Artefacts locaux non versionnés : `artifacts/tests-suite.json`, `tests-suite.log`,
`mimo-avant.log`, `tests-mimo-final.log`, `cibles-final.log`, `noms-final.log`,
`comparaison-4h.json` et son journal, `verifier-2h.json`, `verifier-8h.json`, et
`artifacts/luna/*-restes-fusions-final-depouille.json` avec son fil HTML.

## Reproduction

Depuis le worktree, Python partagé : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
Pour les tests utilisant des fichiers temporaires, `TMP` et `TEMP` désignent
`artifacts/tmp` ; `PYTHONIOENCODING=utf-8` évite les erreurs de console redirigée.

```powershell
C:\Users\msics\donjon\.venv\Scripts\python.exe tools/tests.py --processus 4 --sortie artifacts/tests-suite.json
.venv-mimo\Scripts\python.exe -m unittest tests.test_restes_fusions tests.test_mimo tests.test_fournisseurs_jeu -q
C:\Users\msics\donjon\.venv\Scripts\python.exe tools/comparer_bancs.py --reference 5594028 --scenarios relais mine auberge crue --heures 4 --graines 1985 7 42 2024 --processus 4 --sortie artifacts/comparaison-4h.json
C:\Users\msics\donjon\.venv\Scripts\python.exe tools/empreintes_nuits.py jouer --depot . --scenarios relais mine auberge crue --graines 42 --departs tire --heures 2 --processus 4 --verifier --verification 1 --sortie artifacts/verifier-2h.json
C:\Users\msics\donjon\.venv\Scripts\python.exe tools/empreintes_nuits.py jouer --depot . --scenarios relais mine auberge crue --graines 42 --departs tire --heures 8 --processus 4 --verifier --verification 0.2 --sortie artifacts/verifier-8h.json
C:\Users\msics\donjon\.venv\Scripts\python.exe tools/banc_parties.py tests/data/bancs/depouille.json --max-appels 50 --fil --etiquette restes-fusions-final --sortie artifacts/luna
```

## Limites

- Pas de nouvelle mécanique, de modification du planificateur ni de rattrapage des branches
  `codex-garde-pret` et `codex-force-4b`. L'intégrateur devra rejouer les contrôles sur leur fusion.
- Les portraits anciens ne sont pas séparés automatiquement en propositions visuelles et
  comportementales : la dépouille perd le texte libre complet et conserve sa désignation
  visuelle ainsi que ses détails structurés. Un texte déclaré visuel reste une donnée
  sémantique ; aucun analyseur déterministe ne certifie toutes ses formulations.
- Les souvenirs de rencontres et les paroles effectivement prononcées du vivant demeurent
  des événements historiques, sans donner une voix actuelle à la dépouille.
- Aucune migration générale des anciennes sauvegardes de dépouilles n'est ajoutée.
- La détection des contradictions narratives libres reste en partie sémantique, comme
  le contrat commun du jeu ; ce lot ne prétend pas résoudre cette limite.
- Les chronométrages sur ce poste partagé ne prouvent pas un gain de performance.
