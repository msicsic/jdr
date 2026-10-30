# Outils de mesure

Déplacé de `docs/etat-dev.md` le 2026-10-30.

- Coût déterministe, sans Luna : `python tools/mesure_cout.py --reference 42bb9c0
  --branche integration --verifier --sortie artifacts/cout.json`. Par défaut : auberge 1985
  12 h fixe/tiré et mine 1985 12 h fixe ; `--scenario`, `--graine`, `--heures`, `--depart`
  pour une nuit. Références figées en commits, worktrees détachés nettoyés, aucun checkout
  du worktree courant. Cache commun `<commit>/mesure_cout/`, clé incluant configuration,
  version de la sonde et vérification ; `--sans-cache` ignore et ne remplit pas le cache.
  Compteurs entiers par heure et PNJ × but, totaux et moyennes par heure : appels de
  `choisir` (but `__choix__`, car un choix compare plusieurs buts), recherches, neuves,
  reprises mémoire, graphes réutilisés, passes, nœuds examinés de toutes les passes,
  nœuds de certificats, générations et propositions de gestes réellement produites.
  Une reprise de graphe sans réponse mémorisée reste une recherche neuve selon le banc.
  Les nœuds incluent les terminaux examinés ; les gestes comptent les sorties du générateur
  (une proposition immédiate ou différée), pas les gestes exécutés ni les arêtes uniques.
  Générations des certificats incluses, nœuds des certificats séparés. Ventilation à l'heure
  de début de recherche ; intervalle `[h*60, (h+1)*60[`. Le CPU instrumenté est indicatif.
  `--verifier` exige deux mesures identiques et des empreintes identiques au témoin sans
  sonde (chronique, récit, souvenirs, mesures et état complet). Un seul calcul à la fois
  par invocation, priorité réduite ; aucune suite complète nécessaire pour cet outil.
- Suite sans appel au modèle, par fichiers isolés : `python tools/tests.py` ; moitié des cœurs
  par défaut, `--processus N` pour régler la charge. Fichiers en arguments (`tests/test_web.py
  tests/test_tui.py`) ou `--motif "test_*banc*.py"` ; `--sortie artifacts/tests.json` pour les traces
  et temps détaillés. Les durées dans `artifacts/durees_tests.json` servent aux exécutions suivantes
  (fichiers les plus longs en premier). Rendu et comptes de `unittest`, y compris subtests, erreurs
  d'import, sauts, échecs attendus et succès inattendus. Code 1 si échec ou processus interrompu.
  Le mode `--processus 1` garde l'isolation par fichier ; la référence en un seul interpréteur reste
  `python -m unittest discover -s tests -q`.
- Comparaison sans Luna : `python tools/comparer_bancs.py --reference main --scenarios relais mine
  --processus 2 --sortie artifacts/comparaison.json` : 4 h, graines 1985/7/42/2024, salles passives
  adaptées aux scénarios ; `--branche REF` pour une référence git, sinon fichiers du worktree courant.
  Worktrees détachés créés et supprimés automatiquement, sans changer la branche principale.
  `--depart fixe`, `--verifier`, `--joueur mine=galerie` ; tableau moyenne [min–max], audit des boucles,
  usurpations, plantages, temps écoulé et temps processeur par nuit (`secondes_cpu` dans le JSON).
  `--empreintes` : 2 h par défaut, identité de chronique, mesures et état final complet (`data`, SHA-256),
  code 1 si divergence. Première nuit dans l'ordre scénarios/graines, première minute observée par un
  rejeu instrumenté uniquement en cas d'écart (exclu des temps). Voir les limites dans le rapport.
  **Cache des références** : la référence (et `--branche REF`) est résolue en commit ; chaque nuit est
  lue dans `artifacts/references/<commit>/comparer_bancs/f<format>-i<observation>/` avant d'être jouée,
  et rangée une fois jouée (un fichier par nuit, nommé par scénario, graine, heures, départ, salle du
  joueur, empreintes, `-verifier`, `-localiser` ; la clé complète relue avant réemploi ; `i…` est
  l'empreinte du code de `jouer_nuit` et de `audit_nuits.py`). Une nuit plantée n'est pas rangée ; le
  worktree courant jamais. Le worktree de la référence n'est créé que s'il reste une nuit à jouer. La
  sortie dit combien de nuits viennent du cache et que leurs temps ont été mesurés dans d'autres
  conditions de charge ; `--sans-cache` rejoue tout, pour comparer des temps.
- Cache commun (`tools/references.py`) : dossier du dépôt principal, partagé par ses worktrees
  (`SEUIL_REFERENCES` le déplace). `python tools/references.py lister` (commits, sujet, contenu par
  outil, taille) ; `purger [--garder N] [--simulation]` retire les commits qui ne sont plus des ancêtres
  de `main` et ceux qui ont plus de N commits de retard ; un dossier qui ne se résout pas en commit
  est signalé, jamais retiré.
- Luna en plusieurs passes : `python tools/banc_multi.py --variante main=main --variante lot=. --repetitions
  1 --connexion chatgpt <scripts>`. Une variante résolue en commit réemploie ses parties déjà jouées,
  par script : `<commit>/banc_multi/<script>-<connexion>-<effort>-<réflexion>-m<max-appels>[-offline]-<empreinte>/partie-<n>.json`
  (`cle.json` : contenu du script et de `banc_parties.py`, options) ; la passe i prend la i-ième partie
  rangée, seuls les scripts manquants se jouent. Une partie arrêtée par le budget ou touchée par une
  erreur technique n'est pas rangée ; `nom=.` jamais. Le résumé dit, par variante, les passes venues du
  cache ; `--sans-cache` rejoue tout.
- Banc moteur seul, sans appel à Luna, avec son récit (`--chronique` pour chaque pas) :
  `python -m donjon.banc_pnj --heures 8 --graine 1985 --joueur chambre_cloche` ; plusieurs nuits
  en parallèle, avec le tableau des mesures et leur moyenne : `--graines 1985 7 42 2024`.
  `--diagnostic` ajoute les recherches du planificateur par PNJ et par but (issue, reprises de
  la mémoire, nœuds, durée), aussi dans `--sortie`.
  `--scenario crue` joue la crue : récit de l'eau (tirage, salles gagnées, feux noyés, où chacun
  finit) et mesures `minutes_dans_l_eau`, `feux_noyes`, `trempes_fin`, `au_sec_fin`.
