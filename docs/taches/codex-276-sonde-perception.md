# Tâche Codex 276 (outils) : la sonde 219 voit les entrées perceptives

Le diagnostic 272 (`docs/taches/rapport-codex-272-retour-aubin.md`, fusionné ; bruts
`C:\Users\msics\donjon\artifacts\retour-272\`) montre que le seul suspect restant du compteur 219 (Aubin, Relais 2024,
retour à `117518`) a un déclencheur réel que la sonde ignore : Ilse, sortie du champ de vision d'Aubin à `117503`,
redevient perçue à `117518` et fait renaître le candidat de secours. `relever_entrees`
(`tools/detecter_changements_avis.py`) ne relève ni les personnages et objets effectivement perçus, ni la provenance
des croyances (`entendu` → `vu`) : son « strict complet » n'est donc pas une identité de toutes les entrées du choix.
Le défaut moteur lui-même (la demande close à tort à `117503`) relève d'un autre chantier, en attente de décision ; ce
lot ne touche que la mesure.

## L'invariant
**La sonde relève, parmi les entrées d'un choix, ce que le PNJ perçoit effectivement et la provenance de ses croyances
sur les cibles du plan. Un retour dont seule une entrée perceptive a changé n'est ni « suspect strict » (une entrée a
changé) ni justifié d'office : il est classé dans une classe distincte, « renouvellement perceptif », qui reste à
examiner.** Elle ne devient une justification que si la classe existante l'exige déjà (entrée publiée employée par le
plan, lot 271). Un retour sans aucune entrée changée, perceptive comprise, reste suspect. La sonde observe sans modifier
le jeu (identité avec et sans sonde).

Lot de 30 à 45 minutes. **Outils seulement : aucun fichier de `donjon/` modifié.** Si la sonde a besoin d'une
information que le moteur ne publie pas, dis-le sans modifier le moteur. **Poste : le laptop**, un processus à priorité
réduite (un banc d'un autre lot y tourne déjà). Pas de Luna, pas de suite complète.

**Fichiers autorisés** : `tools/detecter_changements_avis.py`, `tools/audit_nuits.py` en raccord,
`tests/test_detecter_changements_avis.py`. Ne réintroduis pas la clé `engagements` hors du socle des agendas (contrôle
AST de `tests/test_agendas_socle.py`).

## Vérification
- Aubin Relais 2024 `117518` (intégration, départ tiré, joueur passif `chambre_cloche`, 4 h) classé
  « renouvellement perceptif », avec l'entrée changée nommée (Ilse perçue, provenance de son lieu).
- Contre-épreuves en scène : retour sans aucune entrée changée (toujours suspect) ; retour justifié par une entrée
  publiée employée (classe du 271 inchangée) ; le suspect historique Mireille auberge 1985 `36720` toujours signalé.
- Les tests existants de la sonde inchangés et verts.
- Vingt nuits de 4 h (cinq scénarios × quatre graines) sur l'intégration actuelle, avec et sans sonde : états,
  chroniques et mesures identiques ; compteurs avant/après rapportés (référence : bilan du lot 271,
  `C:\Users\msics\donjon\artifacts\reveils-271\bilan.json`). Calcul long détaché.

## Livraison
- Branche `codex-sonde-perception` poussée (sinon commit local, et dis-le). Rapport d'une page
  `docs/taches/rapport-codex-276-sonde-perception.md` ; entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans
  `C:\Users\msics\donjon\artifacts\perception-276\`. Termine par `LOT TERMINÉ` (résumé d'une ligne),
  `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
