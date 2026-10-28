# Lot 248 — ascendant neutre (A5, lot 1)

Branche `codex-ascendant-neutre`, **non fusionnée**, base `f46a0b5`,
28 octobre 2026. Cette base remplace `1006204` sur instruction du superviseur.

L'invariant est un sixième axe orienté, accessible par `relations.py`,
sans effet sur les décisions. `AXES`, `ETRANGER`, `_nouvelle`, `envers`,
`axes` et `autorite_reconnue` exposent maintenant l'ascendant (0–100,
neutre à zéro). Les liens déclarés dans un profil le fixent ; aucun scénario
n'est modifié et aucune épreuve ne le fait varier. La bande reprend les
seuils 60/50 de la confiance ; l'estompement reprend le retour de l'affection
vers le lien initial, à un point par heure. Une valeur initiale déclarée
reste donc stable. Ces réglages ne donnent aucun bonus d'autorité.

`_completer` fournit une vue pure des relations historiques sans ce champ :
valeur zéro, bande fausse et ancre neutre. Chargement et lecture ne réécrivent
pas la sauvegarde. La validation accepte l'ancien contrat complet ou le
nouveau et rejette les contrats partiels. Les anciennes chroniques restent
valides. `signature` inclut valeur, bande et ancre ; la clé de lecture inclut
le lien initial. `_entrees` énumère déjà `relations.AXES` et reçoit ainsi
le sixième axe sans modifier `planification.py`. Les signatures des signes,
limitées aux seuils effectivement lus, restent inchangées.

Vérifications ciblées : **44 tests verts en 11,856 s**, puis **50 verts en
13,809 s**, soit **81 tests distincts** dans six fichiers (relations,
voix, signes). Six tests nouveaux couvrent deux couples orientés (70 contre
20), profil déclaré, pureté, sauvegarde/rechargement du monde et du rendu,
ancien format sans migration puis action visible identique, estompement en
bloc/découpé, hystérésis, invalidation du cache et validation. Le contrôle AST
interdit toute occurrence directe de l'axe hors de `relations.py` dans le
jeu et les outils. `git diff --check` vert. Les premières tentatives du
lanceur ont rencontré les permissions temporaires du sandbox Windows ;
les passes rapportées sont les reprises autorisées hors sandbox.

**Banc de neutralité en attente** : vingt paires de 2 h, Relais/mine/auberge/
crue/crue_hameau, graines 1985/7/42/2024, référence `f46a0b5` via le cache
standard (seules les manquantes sont jouées). Lanceur de preuve dans les
bruts : `banc_ascendant_248.py`. La branche conserve chaque état et résultat
bruts et chaque chemin retiré ; seuls les champs `ascendant` neutres
(valeur, bande, ancre, y compris instantanés typés des chroniques) sont
retirés avant comparaison du hash complet et des données hors temps.
Les textes de chronique, mesures, récit et souvenirs doivent rester identiques.
Le résultat ne sera déclaré validé qu'après lecture de `comparaison.json`.
Fichier de fin écrit en dernier :
`C:/Users/msics/donjon/artifacts/ascendant-248/fin.json`.

Aucune suite complète, aucun Luna, aucune fusion. Ce lot pose le contrat ;
statuts, attribution, jugement des mandats et épreuves d'autorité restent
aux lots suivants. Bruts : `C:/Users/msics/donjon/artifacts/ascendant-248/`.
