# Tâche Codex 116 : un rapport d'audit narratif ne peut pas être incohérent par construction

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). **Luna disponible** : copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth` ; `tools/banc_multi.py --connexion chatgpt`. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 2 processus de calcul, Luna en
4 exécutions au plus ; le lot 114 (vérification lourde, 2 processus) et le lot 115 (`pnj_propositions`, `echanges`) tournent.
Ce lot touche le schéma et le contrôle de l'audit narratif (`narration.py`, `mj.py`). Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Objectif de l'utilisateur** : le temps avant la réponse au joueur.

## Le constat (attribution du lot 113)
Première famille d'appels supplémentaires du MJ : **rapports d'audit narratif illisibles**, verdict et portée mécanique
incompatibles (contrôle du lot 83 : favorable + portée négative, ou négatif + portée établie → illisible, redemandé) :
**9 → 44 appels supplémentaires, 37 → 161 s, relances 2 → 13** entre b0042c9 et 91a4351 (vingt scripts, deux passes). Le lot 95
(rapport limité aux données de décision, champs sans objet omis, motif retiré des segments admis) et le lot 112 (extraction
`rappels`) ont changé la forme du rapport depuis. Attribution complète, appel par appel : `C:\Users\msics\donjon\artifacts\relances-113\`
(`91a4351-attribution.json`, `familles.json`, `qualification.json`) ; rapport `docs/taches/rapport-codex-113-relances-doublees.md`.

## D'abord, établir la cause
Sur les rapports illisibles archivés : quelles combinaisons verdict/portée Luna produit, sur quels segments (ambiance, parole,
résultat, perception), et ce que le schéma lui permettait ; depuis quel lot la fréquence a monté (83, 95, 112 ?), par rejeu des
entrées exactes avec le schéma de chaque version si nécessaire.

## L'invariant
**Le format imposé à l'auditeur ne permet que des rapports cohérents** : la portée mécanique et le verdict ne se contredisent pas
par construction (par exemple, des variantes de schéma par verdict, ou la portée dérivée de champs typés qui la déterminent), au
lieu d'un contrôle après coup qui redemande ; un rapport réellement contradictoire reste refusé. Aucun contrôle supprimé, aucun
refus juste perdu, aucune consigne ajoutée pour un cas.

## Vérification
- Tests : chaque combinaison verdict/portée produite par le schéma est cohérente ; les rapports illisibles archivés rejoués avec le
  nouveau schéma (entrées exactes) deviennent lisibles avec le même verdict ou un verdict juste ; un rapport contradictoire forgé
  reste refusé.
- Rejeu des refus justes de la référence (méthode des lots 93/95, cinq rejeux de chaque côté en cas d'écart).
- Luna, **deux passes** des vingt scripts du lot 111 si le temps le permet, sinon des six scripts du lot 93, contre 91a4351 en cache :
  appels et secondes par tour (moyenne, médiane), relances, rapports illisibles.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-rapports-illisibles`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-116-rapports-illisibles.md`.
