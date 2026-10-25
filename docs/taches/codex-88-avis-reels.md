# Tâche Codex 88 (A3, suite) : les avis de menace se disent dans les nuits réelles

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). Pas de Luna. **Un seul poste** : priorité réduite, au plus 3
processus ; le lot 87 (`deliberation.py`, `planification.py` : recherches bornées) tourne en même temps. Ce lot touche
`donjon/social.py` (avis, `_auditeur`), `donjon/esprits.py` et, s'il le faut, la lecture des relations ; pas
`planification.py` ni `deliberation.py`.

Environnement : Python `C:\Users\msics\donjon\.venv\Scripts\python.exe` ; pas de Luna dans ce lot. Termine ton dernier
message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, le **rapport du lot 80** (`docs/taches/rapport-codex-80-avis-menace.md`), `docs/plan-relations.md` § 7.3 et
3f, `docs/etat-dev.md` (entrées `codex-avis-menace` 80, `codex-constats-partages` 55, `codex-deja-dit` 64), puis
`donjon/social.py` (`nouvelles`, `bavarder`, `_auditeur`, l'avis de menace), `donjon/esprits.py` (la croyance `prevision`),
`donjon/eau.py` (`attendue`), `donjon/relations.py`.

## Le constat
Le lot 80 fait dire à un PNJ son avis sur la menace d'un lieu à qui il croit en danger et dont il se soucie (altruisme +
empathie + affection envers lui ≥ 100). Les tests le prouvent dans une scène préparée, mais dans les nuits réelles (banc 4 h et
audits 12 h de la crue 500 et 2024) : **zéro avis, zéro adoption**. La crue 500 garde ses 4 « eau longue » (Gorm au refuge,
Ilse dans la conduite).

## D'abord, mesurer
Sur les nuits crue 500 et 2024 (12 h) : à chaque minute où un PNJ croit une salle menacée dans l'heure, qui il croit dans
cette salle, et lequel des filtres empêche l'avis (pas de croyance de présence de l'autre, souci < 100, déjà dit, pas de minute
de confidence libre, auditeur hors de portée de voix…). Chiffre chaque filtre.

## L'invariant (selon ce que la mesure montre)
**Un PNJ qui croit un proche en danger dans un lieu menacé le prévient dès qu'il peut lui parler**, par la règle commune des
nouvelles. Corrige le filtre qui bloque sans raison : par exemple, le seuil de souci appliqué comme une somme qui n'atteint
jamais 100 avec les profils réels (le plan dit « s'il s'en soucie » : dis quelle lecture des relations le représente le mieux
et pourquoi), ou la priorité d'un avis de danger face aux autres nouvelles (une seule confidence par minute). Pas de seuil
retouché pour un personnage ni de règle propre à la crue ; les valeurs de profil des scénarios ne changent pas.

## Vérification (minimale)
- Tests après rechargement, même laps découpé : un cas réel de la crue 500 (capture enregistrée à la minute où l'avis aurait dû
  partir) : l'avis part et l'auditeur l'adopte ou non selon la règle des sources ; un autre cas de même nature.
- Banc rapide (`tools/comparer_bancs.py --reference <base> --processus 3`, 4 h, 4 graines, crue et Relais) puis l'audit 12 h
  des crues 500 et 2024, branche seule : avis exprimés et adoptés, minutes dans l'eau, `eau_longue`, où chacun finit.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` (3f), `docs/etat-dev.md` (« Branche `codex-avis-reels`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-88-avis-reels.md`.
