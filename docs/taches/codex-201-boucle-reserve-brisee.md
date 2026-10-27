# Tâche Codex 201 (lot 196 a) : un objet brisé ou ouvert n'est plus cru verrouillé, et une intention ne s'exclut pas elle-même

Premier lot correctif du diagnostic 196 (`docs/taches/rapport-codex-196-changements-avis.md`, § 2, 4.2, 4.3 et 5 « Lot 196a »),
mesuré par le compteur du lot 199 (`tools/detecter_changements_avis.py`, intégré à `tools/audit_nuits.py` et
`tools/comparer_bancs.py`). Demande de l'utilisateur du 2026-10-27 : **une parade générale aux changements d'avis, pas au cas
par cas.** Ce lot traite la boucle la plus fréquente (358 retours non justifiés sur 385) : **dans la crue, après que Brune a
brisé la réserve (graine 7 vers 137 min, 42 vers 141, 2024 vers 213), Gorm alterne sans fin entre la pulsion « réserve
verrouillée » et garder l'antichambre / aller voir.** Le diagnostic d'Argon y voit trois défauts liés, **à vérifier sur le cas
réel avant de corriger** :
- le moteur refuse de fermer une porte détruite (`portes.valider_fermeture`), mais le choix et le planificateur ne lisent pas
  la croyance `fin == "detruit"` et la croient encore à refermer ;
- `esprits.constater` laisse `verrouillee = True` sur une porte vue ouverte, et une clé d'état (« vide ») bascule entre ce qui
  a été essayé et ce qui a été vu ;
- `deliberation.retabli_par_son_plan` écarte de `_candidats` la pulsion même que l'intention courante poursuit, dès que son plan
  contient « verrouiller ».

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot peut calculer sur ce poste : au plus 2 processus, priorité réduite.
Fichiers : `esprits.py`, `deliberation.py`, `planification.py` (gestes et `_entrees`), `portes.py` si le contrat commun y vit, et
leurs tests. **Bruts dans `C:\Users\msics\donjon\artifacts\reserve-201\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

Lis `AGENTS.md`, le rapport 196 en entier, le rapport 199, les rapports 103 (garde-manger), 175 et 179 (croyance `fin`), puis
`esprits.constater`, `deliberation._candidats`, `retabli_par_son_plan`, `satisfaite`, `planification.gestes`, `_entrees`,
`portes.valider_fermeture`.

## L'invariant
**Ce qu'un PNJ croit de l'état d'un objet est cohérent et lu par un seul juge : une porte ou un contenant qu'il a vu ouvert ou
brisé n'est plus cru verrouillé ; une installation crue détruite ne fait naître ni pulsion de la refermer ni geste pour le faire,
au choix comme au plan comme à l'exécution ; un constat par l'essai et un constat par la vue du même état donnent la même
croyance ; et une intention n'est jamais écartée des candidats par la garde qui protège son propre plan.** Même règle pour tout
PNJ et le joueur ; aucune règle propre à Gorm, Brune, la réserve ou la crue.

## Vérification
- Reproduire d'abord la boucle sur la base (crue 7, 42, 2024 ; captures rechargeables juste avant) et confirmer ou corriger le
  diagnostic d'Argon (dis lequel des trois défauts joue vraiment et comment).
- Tests après rechargement : Gorm cesse d'alterner une fois la réserve brisée et choisit un recours cohérent (garder, réclamer,
  prévenir…) ; un autre cas de même nature (autre porte ou contenant forcé, autre scénario) ; une porte seulement fermée reste à
  refermer ; une pulsion dont le plan contient « verrouiller » n'est plus auto-exclue ; même laps d'un bloc ou découpé ; monde et
  rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont hameau) × quatre graines (références du cache), **avec le compteur des changements
  d'avis** (départ du lot 199 : crue 367, hameau 18, autres 0) : la crue doit baisser fortement, aucun scénario monter ; aucune
  usurpation, plantage ni boucle nouvelle ; `VERIFIER` + `spatial.VERIFICATION` 0,2, crue 7, 2 h.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-reserve-brisee` poussée (pas `main`) ;
`docs/etat-dev.md` (« Branche `codex-reserve-brisee`, non fusionnée ») ; rapport d'une page
`docs/taches/rapport-codex-201-reserve-brisee.md`.
