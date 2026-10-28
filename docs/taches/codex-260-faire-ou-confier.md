# Tâche Codex 260 (A5, lot 5) : faire ou confier, sur les seules croyances du mandant

Reprise du lot 257, arrêté au constat prévu (`docs/taches/rapport-codex-257-faire-ou-confier.md`) : il manquait le devis
d'un acteur vu par un observateur. C'est fait par le lot 258 (`docs/taches/rapport-codex-258-devis-observateur.md`,
fusionné) : `agendas.devis_observateur`, `planification.ContexteDevis`, `relations.autorite_estimee`. Le brief initial
`docs/taches/codex-257-faire-ou-confier.md` vaut toujours pour l'invariant, le périmètre et la vérification ; lis-le, puis
les rapports 245, 256, 257 et 258.

## L'invariant (rappel)
**Pour un sous-but social d'un agenda (amener, informer), le PNJ compare le faire lui-même au le confier à un tiers, sur
ses seules croyances** : coût de son propre plan, coût du plan du tiers **vu par lui** (`devis_observateur`), chance
d'acceptation estimée de son point de vue (`relations.autorite_estimee`, relations et refus retenus, `chance_demande`),
fiabilité crue ; égalité départagée par identifiant. Déplacer réellement le candidat hors de sa perception ne change pas
le choix. Deux fonctions séparées, appelées chacune à un seul endroit : le choix du prochain sous-but, puis le choix du
mandataire. Le mandat retenu passe par `echanges.confier(mandat=...)` (jugement réel du 256) ; un refus est retenu selon
sa cause et le mandant fait lui-même ou essaie un autre tiers, sans boucle.

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : pas de suite complète, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le PC fixe**, au plus 2 processus, priorité réduite.

**Fichiers autorisés d'avance** : ceux du brief 257 (`agendas.py`, `planification.py`, `deliberation.py`, raccords des
devis sociaux et de `echanges.confier`). Le lot 259 (en cours) modifie `planification._mesurer_direct` et `pnj.refus_etape` :
n'y touche pas. **Ce lot change une fonction commune du choix** : lance **tous les fichiers de tests qui exercent
`deliberation.choisir` et les agendas** (trouve-les par grep des appelants), pas seulement les voisins ; le superviseur
lancera la suite complète sur ta branche avant de la fusionner.

## Vérification
Celle du brief 257 : scènes Gorm → Aubin → Brune et information à Ilse en profils de test, refus puis faire soi-même,
candidat déplacé hors perception, égalité ; monde et rendu rechargés, laps d'un bloc ou découpé ; banc rapide 4 h,
cinq scénarios × quatre graines, références du cache, compteur 219, lancé détaché, écarts expliqués, coût des recherches
rapporté.

## Livraison
- Branche `codex-faire-ou-confier-b` poussée (si le contrôle automatique refuse la poussée, laisse le commit local et
  dis-le). Rapport d'une page `docs/taches/rapport-codex-260-faire-ou-confier.md` ; entrée « non fusionnée » dans
  `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\confier-260\`. Termine par `LOT TERMINÉ` (résumé
  d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
