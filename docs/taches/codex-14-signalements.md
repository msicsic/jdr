# Tâche Codex 14 : les signalements de l'audit des nuits

Branche `codex-signalements` (elle porte ce fichier, issue de `main` 43fa7ac), worktree dans
`tmp-worktrees/`. Lis d'abord `AGENTS.md`, `docs/etat-dev.md` (entrées `audit-nuits`, `besoins`,
`ouie-temoins`, `deliberation-evenements`, `boucles-pnj`, `codex-relations-3b`, `codex-force-4a`),
`docs/audit-nuits.md`, `docs/reverification.md`, `docs/plan-planificateur.md` (« Dynamique des besoins »,
« Les boucles de la revérification ») et `tools/audit_nuits.py` (`analyser` : ce que chaque signalement
mesure).

**Pas de Luna sur ce poste** : ce lot n'en a pas besoin (moteur seul).

## Le constat
Sur `main`, l'analyseur de `tools/audit_nuits.py` lève encore, nuit après nuit, des signalements que
personne n'a expliqués. Sur 8 nuits de 12 h (auberge et crue, rapport `codex-9-lampes-suite`) :
`fige_presse` 23, `noir_long` 11, `illicite_entendu` 11, `voir_alterne` 7,
`illicite_sans_temoin_avec_present` 4, `eau_longue` 2, `appels_nombreux` 1. Cas connus :
- Mireille (auberge) 225 minutes sans but, pressée par son devoir (rapport `codex-13-garde-pret`) ;
- appels à l'aide répétés environ toutes les 30 minutes après un vol vu (désarroi renouvelé, relevé à la
  fusion de 3b ; Gorm trois fois en 70 min, Relais 42) ;
- `voir_alterne` : aller voir alterné avec un autre but.

## Le travail
1. **Mesurer** : audit 12 h, les quatre scénarios × 8 graines (1985, 7, 42, 2024, 3, 11, 99, 500), départ
   tiré, sur `main` (`audit_nuits.py jouer` puis `analyser`). Classer chaque signalement par cause, en
   lisant chroniques, récits et `--rejeu` des cas les plus longs.
2. **Trancher chaque famille** : défaut du moteur (une règle commune manque ou se contredit) ou
   comportement juste que le signalement compte à tort (l'analyseur à préciser, avec la raison). Exemples à
   examiner : un besoin qui presse sans aucun recours possible (doit-il attendre, `minutes_urgentes_en_attente`,
   au lieu de compter « figé » ?) ; un devoir qui presse sans rien à faire ; un geste illicite fait sous les
   yeux d'un présent qui ne le voit ni ne l'entend (noir, dos tourné, inconscient : juste ou non ?) ; un
   désarroi qui se renouvelle sans fait nouveau.
3. **Corriger les défauts** par l'invariant général (règle d'`AGENTS.md`), jamais par un cas de personnage ou
   de scénario ; préciser l'analyseur pour les faux signalements, en le disant.

## Vérifications
- Tests après rechargement (`tests/test_signalements.py`) : pour chaque défaut corrigé, le cas réel (scène
  enregistrée dans `tests/data` si besoin) et un autre de même nature, même laps d'un bloc ou découpé.
- Suite complète verte (`tools/tests.py`) ; `planification.VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h,
  puis 0,2 sur 8 h graine 42, de chaque scénario, sans écart.
- Audit 12 h avant → après (mêmes 32 nuits), signalements par famille ; banc 8 h
  (`tools/comparer_bancs.py`, 4 scénarios × 4 graines) : sans recours, en attente, échanges, vols vus,
  usurpations et violations (aucune), temps. Bancs l'un après l'autre, `--processus 3` au plus (deux autres
  agents calculent sur ce poste).
- Docs : `docs/audit-nuits.md` (section nouvelle : signalements de `main` 43fa7ac, causes, suites),
  `docs/plan-planificateur.md` si une règle change, `docs/etat-dev.md` (« Branche `codex-signalements`, non
  fusionnée », compte de tests).

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-14-signalements.md` : table des signalements avant → après par famille, cause de
chacune, corrections, faux signalements et précision de l'analyseur, limites. D'autres branches touchent la
délibération et le planificateur (relations 3c, force 4b, `GARDE`/`PRET`) : garde les changements localisés.
