# Tâche Codex 24 : A1, le socle des agendas (sans changer les nuits)

Branche `codex-a1-socle` (elle porte ce fichier, issue de `codex-a0-echelle` 2ddebe4, A0 livré et non encore
fusionné), worktree dans `tmp-worktrees/`. **Lot court (30 à 45 min) : suis « Rythme des lots » d'`AGENTS.md`.**
Lis `docs/plan-agendas.md` § 5 (modèle de données) et § 9 (A1) pour le contexte, sans en faire davantage, puis
`donjon/relations.py` et `tests/test_relations_socle.py` : A1 est l'équivalent de 3a pour les agendas.

## L'invariant
`donjon/agendas.py` est le **seul accès** aux engagements d'un PNJ (`esprit["engagements"]`) et aux agendas :
lectures (les engagements en cours, ceux qui portent sur une condition, un objet ou une personne…) et écritures
par opération nommée (prendre, tenir, abandonner, annuler, échoir…), tirées des usages actuels. Tous les sites
y passent : `deliberation`, `echanges`, `dialogues`, `paroles`, `biens`, `esprits`, `monde`, `narration`,
`corps`, `stratege`, `planification` (une lecture), `tools/audit_nuits.py`, et les autres que tu trouveras.
- **Stockage inchangé** dans ce lot : `esprit["engagements"]` garde sa forme et sa place, pour que l'état final
  reste identique octet pour octet. La conversion en agendas d'origine `parole`/`contrat` (§ 5) viendra avec le
  premier lot qui en a besoin ; écris dans le module, en une phrase, comment elle se fera.
- `profil["agendas"]` (agendas de départ du scénario) : lu par le module, aucun scénario n'en déclare, rien ne
  s'active, et **aucun champ nouveau n'est écrit** dans `data` tant qu'il n'y a pas d'agenda.
- Contrôle AST (`tests/test_agendas_socle.py`, sur le modèle de `test_relations_socle`) : aucun code du jeu ni
  des outils ne lit ou n'écrit `["engagements"]` hors de `agendas.py` ; le test dit combien il en relève sur
  42bb9c0.

## Vérifications (rien d'autre)
- Le test AST ; un cas réel (une part promise puis tenue, Relais) et un autre de même nature (une tâche payée
  acceptée puis abandonnée) après rechargement, par le module.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).
- Empreintes : `tools/comparer_bancs.py --reference 2ddebe4 --empreintes`, 2 h, quatre scénarios × 4 graines :
  identiques (réutilise la référence si `artifacts/references/` l'a déjà). Pas de banc 8 h, pas de Luna.
- Doc : `docs/plan-agendas.md` § 9 A1 « Fait » (l'accès, ce qui reste à convertir) ; `docs/etat-dev.md`,
  « Branche `codex-a1-socle`, non fusionnée », compte de tests.

Q (trajets réels) et R (signes) sont en cours de fusion et touchent `planification.py`, `pnj.py`, `signes.py` :
garde tes changements dans ces fichiers au strict minimum (l'accès aux engagements), pour une fusion simple.

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport d'une page
`docs/taches/rapport-codex-24-a1-socle.md` : l'API du module, les sites convertis, le contrôle AST, les
empreintes, les limites.
