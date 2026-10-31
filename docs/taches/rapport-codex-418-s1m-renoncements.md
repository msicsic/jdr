# Lot 418 — S1m, renoncements et efforts publiés au choix complet

31 octobre 2026, PC fixe · `codex-s1m-renoncements` · base exacte `integration 718ca2e0`.
**Validation en cours ; le lot n'est pas encore déclaré terminé.**

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

**Tests et mesures.** Sept nouvelles méthodes contrôlent les copies imbriquées,
l'admission, les causes distinctes, les anciens délais, la survie après 45 épisodes,
les corruptions, les brouillons imbriqués, les devis isolés et l'interruption du vrai
choix au classement final. Chaînes réelles Odon/mine et Brune/Relais : même laps entier
ou découpé avec recharges, état complet et ordre JSON, lignes, rendu, scène et paroles.
Devis négatifs réels Odon/Rémy et effort borné de Joss à l'auberge également exercés.
Résultats ciblés et empreintes 2 h × quatre graines × Relais/mine/auberge/crue à compléter
depuis les bruts ; aucune identité n'est affirmée avant la fin du calcul.

**Limites et voisinage.** Contrôle AST syntaxique local, sans preuve de tous les flux
interprocéduraux Python ; politiques historiques conservées. Aucune modification de
`mj.py` (416), aucun nouveau registre. Pas de suite complète ni Luna. Deux travailleurs
réduits au plus. Les premières tentatives confinées des tests ont rencontré les droits
des répertoires temporaires Windows ; les passages de validation disposent des droits
nécessaires. Bruts : `C:/Users/msics/donjon/artifacts/s1m-418/`.
