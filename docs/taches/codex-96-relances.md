# Tâche Codex 96 : la première famille de relances du MJ évitée à la source

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). **Luna disponible** : copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth` ; `tools/banc_multi.py --connexion chatgpt`. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 2 processus de calcul, Luna en
4 exécutions au plus ; le lot 92 c (planificateur, CPU) et le lot 94 (vérification lourde) tournent en même temps. Ce lot touche
le MJ (`mj.py`, `narration.py`, `paroles.py`, `couverture_action.py`, `refus.py`, consignes), pas `planification.py`.
Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Objectif de l'utilisateur** : le temps avant la réponse au joueur. Après les lots 91, 93 et 95, un tour MJ coûte ~3,2 appels et
~11,7 s ; chaque relance (interprétation corrigée, récit révisé) ajoute un appel de 4 à 5 s.

Lis `AGENTS.md`, les rapports des lots 93 et 95 (`docs/taches/rapport-codex-93-latence-par-appel.md`,
`rapport-codex-95-audit-narratif.md`), `docs/contrat-mj.md` (refus, `attendu`, ce qui n'appelle pas de relance), puis la boucle
d'un tour dans `donjon/mj.py`.

## D'abord, mesurer
Sur l'intégration **7b2691f**, deux passes des six scripts du lot 93 (relais, crypte, atelier, echanges, soir-appel,
noms-dialogue ; la partie de référence est rangée dans le cache) et le fil complet (`--fil`) : chaque appel **en plus du
minimum** d'un tour (interprétation corrigée après un refus du moteur ou de forme, contre-revue non conforme, récit révisé après
un audit, rapport illisible redemandé), avec sa cause exacte (`attendu`, motif d'audit) et s'il était **justifié** (la première
réponse contredisait vraiment l'état ou les mots du joueur) ou **évitable** (faux refus, ou information que le MJ n'avait pas dans
son contexte). Tableau des familles par nombre d'appels et de secondes.

## L'invariant
Pour la **première famille évitable** (et elle seule) : ce qui la cause est corrigé dans le contrat commun (le moteur fournit
d'avance au MJ l'information qui lui manquait, ou le contrôle qui refusait à tort juge sur la bonne donnée), jamais par une
exception d'exemple, un mot-clé ou une consigne ajoutée pour un cas. Les refus justes restent refusés.

## Vérification
- Tests après rechargement avec MJ simulé : le cas réel de la famille et un autre de même nature, sans relance ; un refus juste
  de même forme toujours refusé.
- Rejeu des refus justes de la référence sur leurs entrées exactes (méthode des lots 93 et 95 ; en cas d'écart, cinq rejeux de
  chaque côté pour séparer la variance).
- Luna, deux passes des six scripts, référence `7b2691f` (cache) contre la branche : appels et secondes par tour (moyenne,
  médiane), par fonction, relances, refus, replis.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md` si le contrat change, `docs/etat-dev.md` (« Branche
`codex-relances`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-96-relances.md` (le tableau des familles,
celle traitée, le gain, les suivantes).
