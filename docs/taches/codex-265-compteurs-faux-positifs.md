# Tâche Codex 265 (outils) : trois faux positifs des compteurs 219 et 227

Trois diagnostics fusionnés établissent des faux positifs des sondes de `tools/detecter_changements_avis.py` (compteur
219 des retours, compteur 227 des états payés perdus), sans défaut du moteur :
- **263** (`docs/taches/rapport-codex-263-torche-eteinte.md`) : le 227 classe fautive l'extinction d'une torche payée
  alors que le service était **déjà clos** sur le départ observé du bénéficiaire (`biens.clotures_services_du_choix`,
  ancrage `services_rendus.lieu_beneficiaire` du 238) ; la sonde garde le paiement mais pas l'historique des clôtures.
- **264** (`docs/taches/rapport-codex-264-retours-241.md`), Bram mine 2024 : le 219 signale
  `repetition_sans_entree_nouvelle` quand le but revient **par un autre moyen** (achat raté, puis confier), alors que
  `renoncement_tient` distingue les moyens d'un même but.
- **264**, Gorm hameau 7 : le 219 signale `non_justifie_retour_etat_initial_exact` quand un **rendez-vous intermédiaire
  est réellement clos** (`appel.retrouves`) entre l'abandon et le retour ; `_est_accompli` ne reconnaît pas `attendre`.

Bruts : `C:\Users\msics\donjon\artifacts\torche-263\`, `...\retours-264\`, et l'archive 241
`...\verif-integ-c870c8b\` (cas exacts, à rejouer au besoin sur `c870c8b`).

## L'invariant
**Les sondes classent un retour ou une perte d'état payé d'après ce que le moteur a réellement constaté et publié :
clôture de service publiée avec sa preuve, changement de moyen admissible pour un même but, clôture attestée d'un
rendez-vous intermédiaire.** Un vrai retour sans entrée nouvelle et une vraie perte fautive restent signalés. Aucune
exception par personnage ou scénario ; la sonde observe sans modifier le jeu (identité avec et sans sonde conservée).

Lot de 30 à 45 minutes. **Outils seulement : aucun fichier de `donjon/` modifié.** Si la sonde a besoin d'une
information que le moteur ne publie pas, dis-le sans modifier le moteur. **Poste : le laptop**, un processus à priorité
réduite. Pas de Luna, pas de suite complète.

**Fichiers autorisés** : `tools/detecter_changements_avis.py`, `tools/audit_nuits.py` et `tools/comparer_bancs.py` en
raccord, `tests/test_detecter_changements_avis.py`, `tests/test_transitions_scenario.py`.

## Vérification
- Les trois cas reconnus comme justifiés sur leurs captures ou nuits exactes ; un vrai suspect historique (rapport 219,
  `docs/taches/rapport-codex-219-audit-transitions.md`) toujours signalé ; une perte fautive construite en scène toujours
  classée fautive.
- Vingt nuits de 4 h (cinq scénarios × quatre graines) sur l'intégration actuelle, avec et sans sonde : états,
  chroniques et mesures identiques ; compteurs avant/après rapportés.

## Livraison
- Branche `codex-compteurs-faux-positifs` poussée (sinon commit local, et dis-le). Rapport d'une page
  `docs/taches/rapport-codex-265-compteurs-faux-positifs.md` ; entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans
  `C:\Users\msics\donjon\artifacts\compteurs-265\`. Termine par `LOT TERMINÉ` (résumé d'une ligne),
  `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
