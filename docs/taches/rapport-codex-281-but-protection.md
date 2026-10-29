# Lot 281 — le but de protection nomme le protégé

29 octobre 2026, branche `codex-but-protection`, **non fusionnée**, base
intégration `3470a92`. Bruts :
`C:/Users/msics/donjon/artifacts/protection-281/`.

## Invariant et correction

`planification.reagir` rend désormais `proteger qui=aide[0]` lorsqu'un
protecteur intervient ; les étapes gardent leurs cibles d'agression.
Fuite, riposte, reddition et enquête sur un cri gardent leur contrat.
Aucun scénario, prompt, modèle, recours ou geste social modifié.

Lecteurs vérifiés par recherche : `recit_pnj._but`, épisodes et données de
`Recit`, `paroles.engagements_enregistres` et `but_actuel`, relevés
`audit_nuits._releve`, identité/résumé/achèvement des décisions dans la
sonde 219 (`detecter_changements_avis`), `deliberation.choisir` (motif,
égalité du but et date de maintien), `defense.choisir`, `pnj` (inspection
et exécution du plan). Aucun ne requiert que `qui` soit l'agresseur : le
rendu nomme déjà `qui`, et l'exécution prend la cible dans le plan et
revalide la protection. Ces lecteurs restent inchangés ; les nouveaux
tests les raccordent au but corrigé. Les copies du but enregistrées
après ce choix portent le protégé. **Aucune migration des anciennes
sauvegardes** ; les anciens libellés déjà enregistrés restent historiques.

## Preuves et mesures acquises

**Deux nouveaux tests verts**, 2,006 s, priorité réduite. Capture 279
`0bad227-596-avant-coup.json` conservée sans modification dans
`tests/data/protection-281-avant-coup.json.gz` (SHA-256 décompressé :
`b4dca41b8f155b46f3003ce29f527ce3eeea5a9ce0652c74400bbedcf9b346d0`).
Le rejeu conserve les **quinze gestes, six coups portés et seize PV** du
diagnostic, mêmes auteurs, cibles, instants et dégâts, sans forcer les jets.
Aux sept interventions, Gorm protège Aubin et frappe Brune ; date de
maintien 596 conservée. L'autre épreuve 4c protège Ilse contre Brune.
Chaque intention contrôlée est rechargée : monde, rendu et scène
identiques ; texte MJ, récit, audit et résumé de la sonde nomment le
protégé. Les deux scènes vérifient aussi l'identité d'un laps entier et
du même laps découpé avec recharge intermédiaire.

## Validation restante, détachée

Les **18 fichiers ciblés** sont lancés via `tools/tests.py --processus 2` :
nouveaux tests, défense/combat/secours, récit/paroles, agendas et sonde.
Le calcul détaché attend leur résultat, archive leurs traces puis compare
les deux scènes courtes au `reagir` exact de `3470a92` (chargé sans changer
le checkout). Il conserve les captures et tous les résultats de coups.
Ensuite : `tools/comparer_bancs.py --reference 3470a92 --empreintes --heures 2`
sur Relais, mine, auberge, crue, hameau, graines 1985/7/42/2024, deux
travailleurs réduits. Référence réutilisée depuis son cache quand présente ;
seules les nuits manquantes sont calculées. Aucun temps comparé au cache.

**Résultats ciblés consolidés et empreintes encore à relire** dans
`tests-cibles.json`, `preuves.json`, `empreintes.json` ;
`fin-verification.json` est écrit en dernier et indique le succès ou
l'erreur. Une divergence d'empreinte devra être instruite : seuls le
champ et ses textes peuvent différer. Pas de Luna ni de suite complète.
Le lot ne certifie pas la cohérence sémantique générale des narrations.
