# Tâche Codex 242 : le mandant suit ce qu'il a confié

Décision du 2026-10-27 (revue vierge 187, `docs/etat-dev.md` « Décisions prises le 2026-10-27 ») : **suivi d'une
délégation** : le mandant va voir où en est sa charge confiée, au lieu de rester figé (Gorm, 220 min au Relais à attendre
une charge confiée). Contexte : `docs/plan-agendas.md` (mandat A5), rapports 146 e (`confier`), 213 (contrat
d'engagement), 225 (réessai lié à l'obstacle, jamais au seul délai), 240 (aide stable sous adoption).

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste : le laptop** (l'utilisateur y travaille) : au plus 2 processus, priorité réduite.

**Fichiers** : les agendas et engagements confiés (`agendas.py`), la décision du mandant qui attend (`deliberation.py` :
attente d'une aide, sans toucher à `_classer` ni à la condition d'ouverture du lot 240 sauf raccord justifié), et leurs
tests. **Pas** : `pnj_propositions`, `biens`, `echanges` (lot 228), `pnj.py` et `signes.place` (lot 234), `ouie.py`,
`social.py`, le MJ.

**Bruts dans `C:\Users\msics\donjon\artifacts\delegation-242\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

## Ce qu'on te demande
1. Retrouver un cas réel d'attente figée d'un mandant (Gorm au Relais, ou un autre dans les bancs 4 h) sur l'intégration
   actuelle ; s'il n'existe plus, le dire et reproduire par une scène d'auteur.
2. **Invariant** : un mandant qui attend la réalisation d'une charge confiée la juge d'après ses croyances : l'échéance
   convenue (ou la durée estimée du devis du mandataire), les constats et les nouvelles. Quand l'échéance crue est passée
   sans constat de réalisation, il va constater (le lieu du résultat ou le mandataire), en relance, reprend la charge
   lui-même s'il en a les moyens, ou la confie à un autre ; une réalisation constatée ou annoncée clôt l'attente. Jamais
   un délai arbitraire : l'échéance vient de l'engagement. Même règle pour le joueur mandataire et pour un PNJ. Aucune
   règle propre à Gorm ou au Relais.

## Vérification
- Tests après rechargement : cas réel ou scène, un autre cas de même nature (autre scénario ou autre charge), réalisation
  à temps (pas de visite inutile), réalisation constatée en route, même laps d'un bloc ou découpé, monde et rendu
  rechargés.
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache, compteur 219 et S/F/D : suspects sans hausse,
  minutes « en attente » avant/après.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
- Branche `codex-suivi-delegation` poussée (pas `main`). Si la poussée est bloquée, laisse le commit local et dis-le.
- `docs/etat-dev.md` : « Branche `codex-suivi-delegation`, non fusionnée ». Rapport d'une page
  `docs/taches/rapport-codex-242-suivi-delegation.md`.
