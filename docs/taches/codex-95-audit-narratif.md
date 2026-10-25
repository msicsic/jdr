# Tâche Codex 95 : l'audit narratif ne fait attendre le joueur que pour ce qu'il contrôle

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). **Luna disponible** : copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth` ; `tools/banc_multi.py --connexion chatgpt`. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 2 processus de calcul, Luna en
4 exécutions au plus ; le lot 92 b (planificateur, CPU) et le lot 94 (vérification lourde) tournent en même temps. Ce lot touche
le MJ (`donjon/narration.py`, `donjon/mj.py`, le schéma de l'audit), pas `planification.py`. Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Objectif de l'utilisateur** : le temps avant la réponse au joueur, sans relâcher le contrat du MJ (`AGENTS.md`).

Lis `AGENTS.md`, le rapport du lot 93 (`docs/taches/rapport-codex-93-latence-par-appel.md` : l'audit narratif fait **41 %** de
l'attente, ~5,4 s par tour, premier delta ~1,2 s, donc l'essentiel est la génération du rapport), `docs/contrat-mj.md`
(« Ce que le MJ reçoit d'un refus d'audit », portée mécanique, comptes), puis `donjon/narration.py` (`controler`, le schéma de
l'audit, ce que le moteur lit de chaque champ : verdict, `portee_mecanique`, sources, comptes, présentations, éclairages…).

## D'abord, mesurer
Sur l'intégration **29ccf1e**, avec l'instrumentation du lot 93 (deux passes des six scripts du lot 93, référence en cache si elle y
est) : pour l'audit narratif, jetons de sortie par appel et par champ du rapport, nombre de segments, part des segments dont la
prose est **exactement** un texte du moteur (issue, refus, résultat rendu) ou une citation déjà validée, et part des champs que le
moteur ne lit jamais.

## L'invariant
**L'audit narratif ne produit et ne reçoit que ce que le moteur lit pour décider.** Leviers, dans cet ordre, sans en affaiblir
aucun contrôle : (a) un segment dont le texte est exactement un texte établi par le moteur, ou une citation validée, n'est pas
soumis à l'auditeur (contrôle déterministe, comme le contrôle de voix d'auteur) ; si tous les segments le sont, pas d'appel ;
(b) le rapport ne demande que les champs que le moteur lit, réponses courtes bornées par le schéma (pas de motif libre long quand
un champ typé décide) ; (c) les entrées inutiles à l'audit retirées. Pas d'audit sauté pour de la prose libre, pas de nouveau mode,
pas d'exception de scénario.

## Vérification
- Tests après rechargement avec MJ simulé : texte du moteur seul (aucun appel d'audit), prose libre (audit), mélange (seuls les
  segments libres audités), refus et `attendu` inchangés.
- **Rejeu des refus justes** (méthode du lot 93) : chaque audit refusé dans les parties de référence, rejoué sur ses entrées
  exactes avec le nouveau rapport ; un refus juste perdu bloque (sauf s'il porte sur un appel inchangé : alors rejoue-le aussi sur
  la référence pour montrer la variance).
- Luna, **deux passes** des six scripts, référence `29ccf1e` (cache) contre la branche : secondes par tour (moyenne, médiane),
  par fonction, appels par tour, relances, refus, replis.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-audit-narratif`, non
fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-95-audit-narratif.md`.
