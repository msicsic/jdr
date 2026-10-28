# Tâche Codex 238 : remettre la suite au vert (trois échecs préexistants)

La suite complète de l'intégration a trois échecs connus depuis plusieurs lots (suite sur `2844ef7`,
`C:\Users\msics\donjon\artifacts\integ-218\suite.log` sur le PC fixe) :
1. `tests.test_detecter_changements_avis.DetecterAvisTests.test_torche_hameau_1985_service_perdu` : attente historique
   d'une perte de service (torche de Brune pour Ilse, hameau 1985) qui n'arrive plus. Apparue à la fusion 224 (`346c1aa`)
   par interaction avec 221 (le lot 195 l'a établi : les deux tests passent sur la branche 224 seule `0ae525f`). Le lot 224
   protège justement un service payé : la perte ne doit pas être fabriquée pour satisfaire l'oracle.
2. et 3. `test_fournisseurs_jeu…test_mimo_correction_avant_action_sur_deux_scenes` (atelier) et
   `test_restes_fusions…test_mimo_rejets_et_actions_sur_deux_scenes_apres_reprise` : `6 != 5` appels. Rapport du lot 128 :
   validation `jsonschema` 4.26.0 d'un ancien segment d'audit simulé, rejeté avant reprise.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Tests et outils seulement** ; si un défaut du jeu ou de l'adaptateur
MiMo est en cause, arrête-toi et pose la `QUESTION`.

**Poste : le PC fixe** (`C:\Users\msics\donjon`), au plus 2 processus, priorité réduite.

## Ce qu'on te demande
- Pour chaque test : la cause exacte, puis le verdict (oracle périmé ou défaut). Oracle périmé : rétablis l'intention du
  test (pour 1 : le détecteur 219 classe correctement une perte d'état payé ; trouve ou construis une scène où la perte est
  réelle et physique, par exemple combustible épuisé, et garde l'assertion de classement). Pour 2 et 3 : rends le faux
  segment d'audit conforme au schéma actuel si c'est lui qui est périmé, sans changer l'adaptateur ni le compte attendu
  d'appels sans preuve.
- **Aucune assertion affaiblie sans preuve**, aucune capture réancrée sans la dire.

## Vérification
- Les trois tests verts, leurs fichiers entiers verts ; suite complète une fois à la fin (`tools/tests.py --processus 2`) :
  **zéro échec** attendu, sinon dis lesquels et pourquoi.

## Livraison
- Branche `codex-suite-verte` poussée (pas `main`). Si la poussée est bloquée, laisse le commit local et dis-le.
- `docs/etat-dev.md` : « Branche `codex-suite-verte`, non fusionnée ». Rapport d'une page
  `docs/taches/rapport-codex-238-suite-verte.md`. Bruts dans `C:\Users\msics\donjon\artifacts\suite-238\`. Termine par
  `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.
