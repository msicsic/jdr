# Tâche Codex 247 : les quatre échecs de la suite complète de l'intégration bf4cede

La suite complète lancée par le superviseur sur l'intégration `bf4cede` (après les fusions 218, 228, 229, 230, 232 à 234,
236, 238 à 240, 242 et 244) donne **2 620 tests, quatre échecs, zéro erreur** (journal
`C:\Users\msics\donjon\artifacts\suite-integ-bf4cede\suite.log` sur le PC fixe, recopié dans ton dossier de bruts) :

1. `test_pas_compagnons.test_promesse_hameau_1985_annoncee_retrouvee_apres_recharge` : attend
   `lieu_beneficiaire=None`, reçoit `'antichambre'` ;
2. `test_service_non_defait.test_hameau_1985_prestataire_mobile_bloc_decoupe` : `assertIsNone(lieu)`, reçoit
   `'antichambre'` ;
3. `test_etapes_chainees.test_captures_mine_et_auberge_memes_plans_visites_monde_et_rendu_recharges`
   (`scenario='auberge'`) : empreinte `visites` différente ;
4. `test_verifier_eau.test_on_ne_descend_pas_ou_l_eau_va_noyer_et_on_ne_s_y_chauffe_pas` : un plan descend vers
   l'échoppe ou la crypte, ou se chauffe au brasero.

Ces fichiers passaient séparément sur leurs branches : ce sont des interactions entre lots fusionnés. Les deux premiers
touchent le champ `services_rendus.lieu_beneficiaire` du lot 238 et sa reprise par le lot 233 (oracle réancré sur le lieu
cru au constat) ; le troisième une empreinte de visites ; le quatrième le contrat de l'eau.

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le PC fixe**, au plus 2 processus, priorité réduite.

## Ce qu'on attend, échec par échec
- Trouver **le commit de fusion qui introduit l'échec** (bissection sur les fusions de `integration` entre `4306c14` et
  `bf4cede`, fichier de test seul, worktree détaché) et la cause dans le code.
- Trancher : **défaut du moteur** (corriger le contrat commun, sans cas particulier) ou **oracle périmé** par un
  changement de comportement légitime d'un lot fusionné (réancrer avec preuve : ce que le monde et le rendu montrent
  après rechargement, et pourquoi l'ancienne attente n'est plus la bonne ; assertion jamais affaiblie sans preuve).
- Pour le 4 (eau), le défaut moteur est à supposer d'abord : un PNJ ne doit ni descendre là où l'eau va noyer ni se
  chauffer à un feu menacé ; ne le réancrer que si la scène elle-même a changé de prémisse.

**Fichiers autorisés d'avance** : les quatre fichiers de tests et les fonctions fautives que la bissection désigne, en
raccord minimal. Si la cause est dans `biens.services_proteges`, `planification` (eau, routes) ou `deliberation`,
corrige-la sur place en le disant. Pas le MJ.

## Vérification
- Les quatre tests verts, plus les fichiers de tests voisins de chaque fonction modifiée.
- Si du code moteur change : empreintes 2 h (`tools/comparer_bancs.py --empreintes`), scénarios touchés et Relais,
  quatre graines, référence `bf4cede` du cache ; écarts expliqués.
- Pas de suite complète.

## Livraison
- Branche `codex-suite-bf4cede` poussée. Rapport d'une page `docs/taches/rapport-codex-247-suite-bf4cede.md` (par échec :
  fusion fautive, cause, verdict, preuve) ; entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans
  `C:\Users\msics\donjon\artifacts\suite-247\`. Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.
