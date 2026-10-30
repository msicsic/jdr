# Tâche Codex 373 : S0, conception de la mémoire unifiée des PNJ (rapport seul)

Première étape du [plan de l'esprit social](../plan-esprit-social.md) (étape notée E0 au § 11 ; numérotée **S0** dans la
feuille de route pour ne pas la confondre avec les lots E1 à E9 de l'échéance négociée). **Conception seule : aucun
fichier sous `donjon/`, `tests/` ou `tools/` modifié** ; un processus Python léger à la fois si tu dois lire des
captures ou compter des lectures.

Lis `AGENTS.md`, `docs/etat-dev.md` (court), le plan de l'esprit social **en entier** (surtout § 2, 4, 10, 11 et 13 :
les décisions du 2026-10-30 sont acquises, ne les rouvre pas), `docs/plan-relations.md` (axes, épreuves),
`docs/plan-agendas.md` (A6, table de naissance), et les rapports qui ont créé les registres cités au § 2.1 du plan
(cherche-les dans `docs/historique-lots.md` par mot-clé, sans le lire en entier).

## Ce qu'on attend
1. **Inventaire exhaustif**, mesuré dans le code (pas de mémoire) :
   - chaque lecture de `memoire` (souvenirs) : type de souvenir, fonction lectrice, question posée (« un souvenir de type X
     depuis telle minute ? »), fenêtre implicite, tests qui en dépendent ;
   - chaque registre hors mémoire (`faits_dits`, `refus`, `recherches`, `indices_recherche`, `presence_recherche`, `secours`,
     `detresses_appelees`, `aides_attendues`, `attentes_bornees`, `renoncements`, `donne`, `preuves_relations`, `visites`,
     `voix`, `noms`, `voix_entendues`, `rejoint`, `rejoindre`, `urgences`, agendas, engagements, et tout registre plus
     récent : soupçons du lot 372, obligations datées d'E1 à E4, fin de garde du lot 337…) : clé, écriture, effacement,
     validation à la recharge, lecteurs, présence dans `planification._entrees` ;
   - les croyances (`esprits.croyances`) : attributs, sources, confiance, révision ; lesquelles portent sur « ce qui
     change » (position des personnes, feux) — elles relèvent du lot à part sur l'hypothèse datée, à signaler sans le faire.
2. **Schéma des trois couches et du registre** (§ 4 du plan) : épisodes (âge et importance), faits (identité, source, date,
   confiance, règle commune de contradiction), dossier par personne connue (compte des échanges, faits marquants, valeurs
   estimées, traits crus), registre de ce qui est dit ; **pour chaque registre existant, la vue qui le remplace et sa
   règle d'invalidation déclarée** ; ce qui doit rester dans `data` (déterminisme, laps découpé, sauvegarde) ; le contrôle
   AST du seul module d'accès (comme `relations.py`, `agendas.py`).
3. **Plan de migration en lots d'un invariant**, chacun « empreintes identiques » (S1 a, S1 b…) : ordre, risques (les ~50
   tests ponctuels, `planification._entrees`, coût), et la frontière exacte avec S2 (dossier et compte des échanges, qui
   recoupe les obligations et dettes d'E1 à E4 et des tâches payées).
4. **Interfaces** : avec le lot « position crue des personnes comme hypothèse datée » (où vit l'hypothèse, comment elle
   s'invalide) ; avec la séparation colère/grief (§ 4.1) ; avec la projection publique A1 (lot 346) pour ce que Luna reçoit.
5. **Questions à l'utilisateur**, avec ta recommandation pour chacune.

## Contraintes
**Poste : le PC fixe** (ou le laptop selon la charge). Documentation seule ; ni Luna, ni banc, ni suite.

## Livraison
- Branche `codex-s0-conception-memoire`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; poussée autorisée).
- `docs/conception-memoire-unifiee.md` (la conception, inventaire en annexe si long) et un rapport d'une page
  `docs/taches/rapport-codex-373-s0-conception-memoire.md` ; entrée « non fusionnée » de 8 lignes au plus dans
  `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts éventuels dans `C:\Users\msics\donjon\artifacts\s0-memoire-373\`.
- Termine par `LOT TERMINÉ` ou `QUESTION : …`.
