# Lot 132 — Non-perception et absence

26 octobre 2026 — branche `codex-non-perception`, non fusionnée.

**Cause.** Les fils `057766f` du lot 123 donnent Gorm dans
`personnages_connus`, cinq objets vus sans lui et une couverture partielle de
la galerie. Aucun constat individuel négatif. P1 refuse « tu ne le vois pas »
car la couverture partielle ne prouverait pas son invisibilité ; p2 refuse
« Tu ne sais pas où se trouve Gorm » parce que cette vue ne renseigne pas sur
sa position. Extraction conservée dans `artifacts/non-perception-132/cause.json`.

**Invariant.** Ne pas voir une entité déjà connue est un constat du moteur,
indépendant de l'étendue de la vue ; cela n'établit aucune absence.
`perception.non_vus_connus` projette seulement référence et désignation publiques,
depuis les mémoires existantes, sans position actuelle ni entité inconnue.
`MJ._echanger` transmet cette preuve par la voie commune. `narration.attestations`
produit une formulation exacte par entité, prouvée localement par le mécanisme
du lot 95 et recalculée avant sauvegarde. La règle d'audit distingue ce constat,
l'ignorance de position et l'absence soumise à couverture. Aucun lexique de
formulations, exception de scénario ou changement du contrôle des fuites.

**Vérification.** Tests ciblés : cas réel Gorm sous vue partielle et objet
connu dans une autre salle, texte exact sans audit et paraphrase avec audit,
console et état après recharge ; entité inconnue exclue, preuve retirée quand
l'entité devient visible et attestation périmée refusée à la sauvegarde.
Les parcours du lot 102 refusent toujours les absences injustifiées dans le
noir avec Ilse/Brune présentes. 18 tests ciblés verts, puis trois tests finaux
verts (dont le contrôle de sauvegarde ajouté). Les erreurs de préparation des
nouveaux tests ont été corrigées avant la suite complète. Le bac à sable
Windows bloquait les copies temporaires ; tests repris avec élévation.

Suite complète unique : **2 076 tests, 228 fichiers, 1 110,50 s**, deux
processus réduits, **deux échecs, zéro erreur**. Les deux échecs sont les MiMo
`6 != 5` déjà documentés par les lots 128 à 130 :
`test_fournisseurs_jeu.test_mimo_correction_avant_action_sur_deux_scenes`
(atelier) et `test_restes_fusions.test_mimo_rejets_et_actions_sur_deux_scenes_apres_reprise`.
Même assertion et mêmes parcours ; référence non relancée. Aucun autre échec,
pas de seconde suite. Bilan non entièrement vert ; bruts `suite.{json,log}`.

**Luna, une passe.** ChatGPT `gpt-6-luna`, medium/libre, une exécution,
priorité réduite, copies et coffre principal. Références `057766f` p1/p2
exclusivement relues dans les bruts du lot 123, aucun rejeu.

| Script | Appels/tour référence p1 / p2 → lot | s/tour référence p1 / p2 → lot |
|---|---:|---:|
| signes-guet | 5,00 / 4,00 → 2,00 | 19,59 / 15,42 → 8,43 |
| signes-noir | 2,00 / 2,00 → 2,00 | 11,10 / 10,06 → 6,72 |
| soir-noir | 5,40 / 4,60 → 4,20 | 20,76 / 16,83 → 13,61 |

Huit tours MJ, 27 appels ; aucun refus N6, aucune fausse absence affichée,
aucun repli ni défaut de recharge. Tour Gorm : **6 / 4 → 2 appels**.
Ilse et Brune restent dans l'antichambre rechargée de `signes-noir`.
`soir-noir` conserve une relance (trois obstacles) sur une identité et une
proximité introduites avant présentation ; les gardes déterministes restent
actifs. Le refus final de redonner son identité persiste, hors périmètre N6.
Bruts `artifacts/bancs-multi/20261026-203847-28896/` ; mesures par script dans
`artifacts/non-perception-132/mesures.json`.

**Limites.** La preuve et sa reprise exacte sont déterministes. Le classement
des paraphrases, de « ne pas savoir où » et des absences reste sémantique ;
aucune garantie universelle de compréhension n'est revendiquée. Le dossier
prouve seulement la non-perception visuelle, pas l'absence de son ou l'activité.
Une seule passe Luna, références historiques relues sans rejeu : aucune
attribution causale de latence sur ce poste partagé. Une précision rédactionnelle
finale remplace « borne cette preuve » par « borne les conclusions d'absence »
après le lancement de cette passe, sans second appel de vérification.

Aucune clé Git de signature configurée : commit non signé, branche poussée.
