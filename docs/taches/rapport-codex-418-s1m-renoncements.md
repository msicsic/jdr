# Lot 418 — S1m, renoncements et efforts publiés au choix complet

31 octobre 2026, PC fixe · `codex-s1m-renoncements` · base exacte `integration 718ca2e0`.
Moteur `0e143815`, inchangé depuis. **Tests achevés ; empreintes en cours,
le lot n'est pas encore déclaré terminé.**

**Invariant et code.** `donjon/memoire.py` possède les lectures, admissions, clôtures et
validations de `renoncements` et `attentes_bornees`. Les vues rendent des copies profondes
des causes/étapes/témoins ; les signatures sont des chaînes immuables. Le stockage et ses
anciens délais entiers restent inchangés. Le juge métier du 417 garde la cause, sa levée
par constat et les suites conditionnelles ; aucun délai ne remplace un démenti.

`deliberation.choisir` encadre tout le choix, jusqu'au classement final, dans
`memoire.choix_complet`. `planification.vues_du_choix` prépare un brouillon : un devis
isolé ne publie aucun effort, une sélection imbriquée réussie ne publie que dans son
parent, une interruption jette ses modifications. Les devis négatifs de
`pnj_propositions.recours` et la clôture des obstacles suivent cette même frontière,
y compris après la sélection. Le renoncement effectivement rencontré à l'exécution
reste enregistré à son instant historique, avant l'épisode et l'abandon de l'intention.
Les autres effets opérationnels du choix ne sont pas transactionnés par ce lot.

**Contrôle.** Inventaire AST **46 → 7 expressions** hors porte (54 → 7 occurrences) :
déclaration exacte du schéma et six expressions de diagnostic/archives ; aucun accès
au stockage vivant. Les outils actifs passent par les vues. L'observateur des bancs
charge sa propre porte pour pouvoir aussi lire une référence antérieure à cette API.
Le schéma et les inventaires des familles déjà portées ne sont pas élargis.

**Tests.** Sept nouvelles méthodes vertes contrôlent les copies imbriquées,
l'admission, les causes distinctes, les anciens délais, la survie après 45 épisodes,
les corruptions, les brouillons imbriqués, les devis isolés et l'interruption du vrai
choix au classement final. Chaînes réelles Odon/mine et Brune/Relais : même laps entier
ou découpé avec recharges, état complet et ordre JSON, lignes, rendu, scène et paroles.
Devis négatifs réels Odon/Rémy et effort borné de Joss à l'auberge également exercés.
**156 tests distincts sur 15 fichiers : 155 méthodes vertes aux derniers passages.**
Les deux sous-échecs restants d'une même méthode d'`etapes_chainees` (mine/auberge)
sont reproduits avec les mêmes traces sur `718ca2e0` : `base-etapes.json` et
`attribution-etapes.json`. Aucun oracle historique n'est réécrit. Les premiers rouges
ont révélé trois harnais assimilant devis et choix complet, et une nouvelle éprouvette
qui n'effectuait pas le constat perceptif réel ; harnais/fixture corrigés, assertions
finales conservées, fichiers concernés rejoués. Détails dans `tests-cibles.json`,
`tests-final-voisins.json` et `tests-compensation-final.json` ; rouges conservés.

**Empreintes détachées.** 2 h × graines 1985/7/42/2024 × Relais/mine/auberge/crue,
base exacte `718ca2e0` puis branche, cache partagé, deux travailleurs réduits au plus.
Résultat attendu : `empreintes-base.json`, puis **`fin.json` écrit en dernier** dans
les bruts ; aucune identité n'est affirmée avant sa lecture. Aucun temps comparé au cache.

**Limites et voisinage.** Contrôle AST syntaxique local, sans preuve de tous les flux
interprocéduraux Python ; politiques historiques conservées. Aucune modification de
`mj.py` (416), aucun nouveau registre. Avance documentaire `8c5eaaa7` intégrée par
`ac6a998e` : seul conflit dans `etat-dev`, suivi du 419 conservé. Pas de suite complète ni Luna. Deux travailleurs
réduits au plus. Les premières tentatives confinées des tests ont rencontré les droits
des répertoires temporaires Windows ; les passages de validation disposent des droits
nécessaires. Bruts : `C:/Users/msics/donjon/artifacts/s1m-418/`.
