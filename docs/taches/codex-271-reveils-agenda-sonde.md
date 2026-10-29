# Tâche Codex 271 (outils) : la sonde 219 reconnaît les réveils d'agenda justifiés

Le lot 268 (`docs/taches/rapport-codex-268-agenda-brune.md`, fusionné) montre que chaque réveil de l'agenda `a1` de
Brune (hameau 2024) suit une entrée nouvelle réelle : un objet pris (crochets, pied-de-biche), une position nouvellement
apprise (Gorm cru en antichambre), un engagement effectivement accompli, un bien racheté. Le compteur 219
(`tools/detecter_changements_avis.py`) les laisse pourtant en `entree_nouvelle_a_expliquer` : deux retours actuels
(Brune `591` et `929`), quatre dans l'historique `881db69`. Le lot 265 (fusionné) ne les couvre pas : son changement de
moyen exige un geste manqué puis évité.

## L'invariant
**Un retour au même but est classé justifié quand la sonde observe, entre l'abandon (ou le sommeil) et le retour, une
entrée que le moteur publie et que le plan du retour emploie : possession nouvelle, croyance de lieu changée sur une
cible du plan, engagement clos par le moteur.** Une entrée sans rapport avec le plan du retour ne justifie rien ; un vrai
retour sans entrée nouvelle reste suspect. La sonde observe sans modifier le jeu (identité avec et sans sonde).

Lot de 30 à 45 minutes. **Outils seulement : aucun fichier de `donjon/` modifié.** Si la sonde a besoin d'une
information que le moteur ne publie pas, dis-le sans modifier le moteur. **Poste : le laptop**, un processus à priorité
réduite. Pas de Luna, pas de suite complète.

**Fichiers autorisés** : `tools/detecter_changements_avis.py`, `tools/audit_nuits.py` en raccord,
`tests/test_detecter_changements_avis.py`.

## Vérification
- Les réveils de Brune `591` et `929` (intégration, hameau 2024, 4 h, départ tiré, joueur passif `chambre_cloche`)
  reconnus ; au moins deux réveils historiques du 268 sur `881db69` (bruts `C:\Users\msics\donjon\artifacts\agenda-268\`).
- Contre-épreuves en scène : entrée nouvelle sans rapport avec le plan du retour (toujours à expliquer) ; retour sans
  entrée (toujours suspect) ; le suspect historique Mireille auberge 1985 `36720` (archive 219) toujours signalé.
- Vingt nuits de 4 h (cinq scénarios × quatre graines) sur l'intégration actuelle, avec et sans sonde : états,
  chroniques et mesures identiques ; compteurs avant/après rapportés (référence : bilan du lot 265,
  `C:\Users\msics\donjon\artifacts\compteurs-265\bilan.json`). Calcul long détaché.

## Livraison
- Branche `codex-reveils-agenda-sonde` poussée (sinon commit local, et dis-le). Rapport d'une page
  `docs/taches/rapport-codex-271-reveils-agenda-sonde.md` ; entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans
  `C:\Users\msics\donjon\artifacts\reveils-271\`. Termine par `LOT TERMINÉ` (résumé d'une ligne),
  `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
