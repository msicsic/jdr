# Rapport Codex 4 — outils

Branche `codex-outils`, worktree `tmp-worktrees/codex-outils`, base `06602a6`.
Travail dans la nuit du 22 au 23 octobre 2026. Livraison en deux temps, sans fusion ni modification de `main`.

## Comparateur livré en premier

Commandes (Python du dépôt principal depuis le worktree) :

```powershell
C:/Users/msics/donjon/.venv/Scripts/python.exe -m unittest tests.test_comparer_bancs -q
C:/Users/msics/donjon/.venv/Scripts/python.exe tools/comparer_bancs.py --reference main --branche main --empreintes --processus 2 --sortie artifacts/outils/main-main.json
C:/Users/msics/donjon/.venv/Scripts/python.exe tools/comparer_bancs.py --reference main --branche codex-profils --empreintes --processus 2 --sortie artifacts/outils/main-profils-identite.json
C:/Users/msics/donjon/.venv/Scripts/python.exe tools/comparer_bancs.py --reference main --branche codex-profils --heures 4 --processus 2 --sortie artifacts/outils/main-profils.json
```

- Six tests passent : nuits réelles identiques, scènes sauvegardées et rechargées avec changement
  du joueur ou d'une donnée interne, première minute et chronique tronquée, mesure absente,
  plantage jamais déclaré identique, nettoyage réel d'un worktree après erreur.
- Relais, départ tiré, 2 h, graines 1985/7/42/2024 : `main` contre `main` identique pour les trois
  composantes, huit nuits achevées. Moyennes écoulées 3,112 → 3,581 s ; processeur 2,820 → 3,184 s.
  Ces temps illustrent le bruit d'une mesure unique sur une machine partagée ; aucun gain revendiqué.
- `main` contre `codex-profils` : différence dès la minute 0 de la première nuit (1985), chronique,
  mesures et état final différents ; code 1 attendu. Les données de profil diffèrent au départ.
- Mode normal, Relais, 4 h, quatre graines : huit nuits achevées sans violation ni usurpation,
  code 0 ; tableaux, écarts notables, boucles et constats d'audit produits. Moyennes écoulées
  5,915 → 4,853 s ; processeur 5,648 → 4,617 s. Les nuits diffèrent : ce n'est pas une preuve
  d'optimisation. Sortie Windows redirigée vérifiée en UTF-8.

Réutilisation : `banc_pnj.nuit`, `ceder`, `divergence`, empreintes physiques existantes ;
`audit_nuits._releve`, `_final`, `boucles`, `analyser_nuit`. Le moteur n'est pas modifié.
Chaque nuit a un processus neuf : les caches d'une graine précédente ne biaisent pas ses compteurs
ni son coût. Les deux lots sont joués successivement. Les références sont résolues une fois en
commits ; les modifications non committées sont incluses seulement si `--branche` est omise.

Publication anticipée : `4b8c4db`, poussé avant de développer le lanceur ; puis `c570298`,
priorité Windows effective, poussé aussitôt vérifié. Sur ce Python Windows 64 bits, l'appel
`ctypes` de `banc_pnj.ceder` sans signatures renvoyait `ERROR_INVALID_HANDLE` (6). Le helper commun
`tools/priorite.py` déclare les types HANDLE/DWORD/BOOL puis appelle la même règle. Aucun fichier
du moteur modifié. La classe effective est contrôlée dans un vrai enfant du lanceur ; les temps
des premiers essais du comparateur ci-dessus sont antérieurs à cette correction de priorité.

Limites :

- L'identité porte sur tout `monde.data`, pas sur les caches Python hors sauvegarde ; les mesures
  incluent les compteurs de recherches. Une optimisation qui change ces compteurs n'est donc pas
  déclarée identique sans justification des écarts.
- La datation utilise la première entrée différente de la chronique et, au rejeu, le dernier état
  complet observé après perception de chaque minute, plus création et fin de nuit. Elle donne la
  première minute **observée**, pas la première instruction Python divergente ; un écart transitoire
  résorbé entre ces points peut échapper à cette datation. Un écart de mesures seul sans trace ni
  état différent est annoncé « minute indéterminée ». L'outil ne prétend pas garantir davantage.
- Le mode normal inclut les relevés d'audit dans ses temps ; le mode identité ne les prend pas.
  Comparer les coûts avec le même mode, les mêmes options et plusieurs passes. `process_time`
  exclut l'attente du processeur, sans éliminer tous les effets de la charge sur le matériel.
- Les violations de vérification et les autres exceptions sont comptées comme nuits en échec,
  avec type, message, minute et trace dans le JSON ; aucune nuit échouée ne vaut zéro mesures.
- Le nettoyage est assuré par `finally` après erreur Python ; un arrêt forcé du processus ou de la
  machine peut laisser un worktree à retirer. Git et Python ≥ 3.11 sont nécessaires.

## Lanceur de tests

`tools/tests.py` distribue les fichiers aux interpréteurs Python du même environnement. Le parent
coordonne les sous-processus, puis donne leurs résultats au `TextTestRunner` officiel : le nombre
de tests reste celui de `unittest`, y compris quand une méthode produit plusieurs subtests en
échec. Les traces, sauts, échecs attendus et succès inattendus sont conservés. Un processus qui
s'arrête sans résultat devient une erreur du fichier, jamais un succès silencieux.

Sur ce poste, 16 processeurs logiques : huit processus par défaut. Parent et enfants cèdent la
priorité avec `priorite.ceder`, qui délègue à `banc_pnj.ceder`. Chaque fichier tourne dans un processus neuf ; les fichiers les
plus longs connus partent d'abord, avec taille du fichier comme estimation sans historique.
Cache atomique non versionné : `artifacts/durees_tests.json`, redirigeable par `--durees`.

```powershell
C:/Users/msics/donjon/.venv/Scripts/python.exe -m unittest tests.test_outil_tests -q
C:/Users/msics/donjon/.venv/Scripts/python.exe tools/tests.py tests/test_comparer_bancs.py tests/test_outil_tests.py tests/test_web.py tests/test_tui.py tests/test_tui_cases.py --processus 4 --sortie artifacts/outils/selection-tests.json
C:/Users/msics/donjon/.venv/Scripts/python.exe tools/tests.py --sortie artifacts/outils/parallele.json
```

- Cinq tests du lanceur passent : mêmes comptes qu'unittest (subtests, échec, saut, erreur
  d'import, échec attendu), succès inattendu qui fait échouer, sélection par motif, dédoublonnage,
  tri par durées persistées, arrêt brutal d'un enfant qui fait échouer l'ensemble, priorité
  réellement réduite du processus Windows (0x4000).
- Le nom `tools/tests.py` pouvait masquer le namespace `tests/` lors des imports ; le lanceur
  charge celui du dépôt avant de rendre `tools/` importable. Régression vérifiée avec
  `tests.support` et les sous-processus multiprocessing des tests du comparateur.
- Sélection réelle : 52 tests verts, aucun sauté, 173,12 s. Le fichier `test_tui.py` compte
  28 tests et prend 173,11 s ; les quatre autres fichiers finissent en 4 à 12 s chacun.
- Audit des écritures : dossiers temporaires uniques pour terminal/web, ports web attribués
  par le système (`port=0`). Les deux écritures à chemin fixe de `test_defi.py` sont propres à
  ce fichier, donc à son processus ; les autres fichiers ne les emploient pas. Aucun regroupement
  ni modification des tests de jeu nécessaire. Les tests de presse-papiers simulent leurs appels.

La référence série utilise exactement `unittest.defaultTestLoader.discover('tests')` et
`unittest.TextTestRunner`, avec `priorite.ceder()` avant le chargement. Le petit script de mesure, dans
`artifacts/outils/serie.py` (non versionné), écrit le compte, le verdict et le temps écoulé dans
`serie.json`. Les deux mesures complètes sont lancées successivement.

Référence série finale : **1 293 tests, 14 sautés, aucun échec ni erreur**, code 0.
**1 458,28 s (24 min 18 s)**, découverte comprise ; le résumé unittest seul donne 1 453,05 s.
Commande exécutée :

```powershell
C:/Users/msics/donjon/.venv/Scripts/python.exe artifacts/outils/serie.py > artifacts/outils/serie.txt 2>&1
```

Résultat final de la comparaison, sur le même code et avec la priorité réduite effective :

| Exécution | Processus | Tests | Sautés | Échecs / erreurs | Temps, découverte comprise |
| --- | ---: | ---: | ---: | ---: | ---: |
| unittest, un interpréteur | 1 | 1 293 | 14 | 0 / 0 | 1 458,28 s — 24 min 18 s |
| `tools/tests.py`, 124 fichiers | 8 maximum | 1 293 | 14 | 0 / 0 | 338,19 s — 5 min 38 s |

**×4,31**, soit 76,8 % de durée en moins sur cette paire de passes ; codes de retour 0.
Les fichiers sont isolés sans regroupement particulier et sans modification des tests du jeu.
La passe parallèle démarre avec l'historique partiel des cinq fichiers de la sélection ; les
autres sont estimés par taille. Le cache contient désormais les durées des 124 fichiers pour
les ordonner aux prochaines exécutions. Plus longs observés : terminal 251,85 s, mine 159,05 s,
refus retenus 89,96 s, boucles PNJ 86,91 s. Les temps restent sensibles à la charge et à l'état
des caches : cette paire mesure ce poste, pas une garantie de facteur d'accélération.

Rapports détaillés non versionnés, conservés dans le worktree :
`artifacts/outils/serie.json`, `serie.txt`, `parallele.json`, `parallele.txt`, ainsi que les trois
rapports du comparateur. La découverte, les sauts et les verdicts sont comparés, pas seulement
le code de retour du lanceur. Les onze nouveaux tests des outils font partie des 1 293.

Pour reproduire la référence série à priorité réduite sans le script de mesure local :

```powershell
C:/Users/msics/donjon/.venv/Scripts/python.exe -c "import tests, sys, unittest; sys.path.append('tools'); from priorite import ceder; ceder(); unittest.main(module=None, argv=['unittest', 'discover', '-s', 'tests', '-q'])"
```

Limites et environnement :

- Le bac à sable de cette session refuse les sockets locaux (`WinError 10013`) et certains
  fichiers temporaires système. Les vérifications finales utilisent les permissions locales
  nécessaires, sans appel au modèle. Deux sélections exploratoires interrompues ne sont pas
  des mesures de performance ; leurs seuls processus résiduels ont été arrêtés avant les mesures.
- La première référence série, lancée avant d'avoir constaté l'échec silencieux de priorité,
  a été arrêtée puis reprise avec la signature Windows corrigée. Elle n'entre pas dans les mesures.
- Les tests d'un même fichier restent séquentiels ; le fichier le plus long borne donc le gain.
  Chaque interpréteur a un coût de démarrage/import, inclus dans les durées mémorisées.
- Deux lanceurs qui écrivent le même cache simultanément gardent le dernier remplacement ;
  le cache reste valide, mais utiliser `--durees` distincts pour préserver les deux historiques.
- Une mort brutale d'un processus ne permet pas de connaître combien de ses méthodes avaient
  déjà fini : ce fichier est signalé comme une erreur de processus, avec sa sortie capturée.
