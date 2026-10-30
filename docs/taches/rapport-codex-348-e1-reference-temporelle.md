# Lot 348 — E1, référence temporelle canonique

Branche `codex-e1-reference-temporelle`, base `origin/integration 014fc35` ; code mesuré `06ad173`.

Une obligation peut porter une référence temporelle explicite, sans convertir une durée
de devis, une fin de protection, une échéance de suivi ou le maximum générique d'abandon
en date acceptée. `agendas.prendre(..., limite=T)` établit uniquement sur demande interne
`reference_temporelle = {id, version, creation, limite}` : instants absolus en dixièmes,
identité séquentielle commune au joueur et aux PNJ, version initiale 1. La séquence
persistante ne réemploie pas l'identité d'un engagement retiré, même provisoire.
`agendas.reference_temporelle` est l'unique lecture et renvoie une copie ou `None`.
Les obligations ordinaires, anciennes ou nouvelles, gardent exactement leur stockage :
aucune date ni identité rétroactive, aucun compteur ajouté tant qu'aucune date n'est établie.
Un renouvellement change encore sa minute historique, sans déplacer la référence.

La validation commune d'`esprits.verifier` passe par `agendas` : forme exacte, types entiers
(booléens exclus), identité positive, allouée et unique, version admise, création non future,
limite positive ou nulle et postérieure ou égale à la création. Chaque refus précise dans
`attendu` le chemin, la valeur reçue et la valeur admissible, avec une seule cause.
Deux lignes de `Monde.charger` préservent désormais un `ErreurMonde` déjà produit par la
validation : son enveloppement comme simple `ValueError` effaçait auparavant `attendu`.
Le contrôle AST du socle inclut les deux nouvelles clés de stockage ; aucun accès extérieur.

**Épreuves.** 126 tests distincts ciblés : 124 verts, deux échecs préexistants reproduits
sur la base intacte `014fc35` (Gorm au beffroi plutôt qu'à l'échoppe :
`test_protection.AppelTests.test_a_bout_sans_abri_elle_appelle_et_gorm_accourt` et sa
réutilisation dans `test_agendas_proteger`). Les autres protections, engagements,
délégations, filiation/jugement de mandat, mandat joueur et marchés passent.
Socle : six tests verts ; référence finale : neuf verts ; voisins : 109/111 verts.
Un parcours court huile d'Odile → Joss complète les planches d'Aubin et le travail
payé de Tilo. Les contrôles comparent état,
rendu, scène perçue et paroles enregistrées après sauvegarde/recharge ; ils couvrent aussi
les laps continu/découpé, la lecture sans mutation, le renouvellement, les doublons et
les corruptions de JSON réellement chargées.

**Neutralité prouvée sur les nuits demandées.** Empreintes 2 h, graines 1985/7/42/2024,
Relais/auberge/mine, deux processus à priorité réduite : **12/12 nuits identiques à la
base exacte `014fc35`**, chroniques, mesures et état final complet. Les audits `avis` et
`constats` sont également identiques : zéro avis non justifié, dix avis à expliquer déjà
sur la base. Aucun plantage dans les trois versions mesurées.
La comparaison avec `origin/main 0bad227` diverge dès Relais/1985, minute 0 ; l'identité
complète avec la base établit que cet écart précède E1. `origin/main` est le `main` publié
du point de reprise ; la branche locale `main`, ancienne (`c870c8b`), n'a pas été déplacée.
Les références manquantes ont été calculées une fois et rangées dans le cache commun ;
les douze nuits du lot ont été relues du cache pour la seconde comparaison, sans rejeu.
Aucune comparaison de temps CPU n'en est tirée. Bruts :
`C:\Users\msics\donjon\artifacts\e1-348\` (`empreintes-main.json`, `empreintes-base.json`,
`synthese-finale.json`). Le lanceur laisse ses codes de sortie à `null` dans
`fin-bancs.json` ; les conclusions reposent sur les résultats JSON complets et leurs journaux.

**Limites.** Socle interne uniquement : aucun appelant du jeu ne passe de limite,
aucun schéma, prompt ou rendu nouveau. Le franchissement d'une limite n'a encore aucun
effet ; réalisation datée, expiration, archivage de l'issue et renégociation appartiennent
aux lots suivants. Version 2 refusée tant que cette révision n'est pas portée. Aucun
calendrier, gain autonome PNJ ou respect des délais en partie n'est annoncé. Ni suite
complète, ni Luna, ni banc long lancés.
