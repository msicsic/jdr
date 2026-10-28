# Tâche Codex 257 (A5, lot 5) : faire ou confier, sur les seules croyances du mandant

Cinquième lot d'A5. Conception : `docs/taches/rapport-codex-245-conception-a5.md` (lot 5 et sa note) ; plan :
`docs/plan-agendas.md` § 6.6 et § 9 ; arbitrages du 2026-10-28 dans `docs/etat-dev.md`. Déjà fusionnés : ascendant (248),
statut sourcé (254), filiation (252, `agendas.confier`), jugement du mandaté (256, `echanges.confier(mandat=...)`,
`agendas.devis_mandat`, `relations.autorite_mandat`), suivi d'une délégation à échéance (242). Lis-les d'abord.

## L'invariant
**Pour un sous-but social d'un agenda (amener, informer), le PNJ compare le faire lui-même au le confier à un tiers, sur
ses seules croyances : coût de son propre plan, coût estimé du plan du tiers tel qu'il le croit (sa position crue, ses
moyens crus), chance d'acceptation estimée de son point de vue (relations, autorité qu'il croit avoir, refus retenus),
fiabilité crue ; égalité départagée par identifiant. Déplacer réellement le candidat hors de sa perception ne change pas
le choix.** Deux fonctions séparées, appelées chacune à un seul endroit : le choix du prochain sous-but, puis le choix du
mandataire. Le mandat retenu passe par `echanges.confier(mandat=...)` (jugement réel du mandaté) ; un refus est retenu
selon sa cause (refus retenus existants) et le mandant fait lui-même ou essaie un autre tiers, sans boucle.

Ce lot n'ajoute **ni compte rendu** (lot 6), **ni réaffectation sur retard** (lot 7, au-delà du suivi 242), **ni
évolution de l'ascendant** (lot 8), **ni parole joueur** (lots 9-10), **ni donnée de scénario** (lot 11 ; épreuves en
profils de test). Si le devis vu du mandant exige une projection des connaissances qu'il ne peut pas tenir dans le créneau
sans lire l'esprit du tiers, arrête-toi à ce constat et propose le lot neutre préalable (rapport 245).

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le PC fixe**, au plus 2 processus, priorité réduite.

**Fichiers autorisés d'avance** : `agendas.py`, `planification.py` (devis vu du mandant, `_entrees` pour les lectures
nouvelles), `deliberation.py` (raccord du choix), adaptations des devis sociaux et de `echanges.confier` si le contrat
l'exige ; tests `tests/test_agendas_*`, `tests/test_amener_*`, intermédiaires et voisins, **arbitrage avec preuve**.
**Pas** : `pnj_propositions.py` (marchés), `social.py` et `esprits.py` (lot 255 en cours), le MJ, les scénarios.

## Vérification
- Scènes (profils de test) : Gorm, qui doit amener Brune à la galerie, confie à Aubin quand Aubin est cru plus proche et
  susceptible d'accepter, fait lui-même sinon ; une information à transmettre, autre cas ; refus d'Aubin puis Gorm fait
  lui-même ; candidat déplacé hors de la perception de Gorm : même choix ; égalité par identifiant ; demande sociale à
  Brune par le mandataire, jamais un portage implicite. Monde et rendu identiques après rechargement, même laps d'un bloc
  ou découpé.
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache (ta base `integration`), compteur 219, lancé
  détaché ; écarts expliqués (des agendas `amener`/`informer` existent déjà dans la crue), suspects sans hausse par nuit,
  coût des recherches rapporté (`tools/mesure_cout.py` mine 1985 4 h si les devis s'alourdissent).
- Pas de suite complète.

## Livraison
- Branche `codex-faire-ou-confier` poussée. Rapport d'une page `docs/taches/rapport-codex-257-faire-ou-confier.md` ;
  entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\confier-257\`. Termine
  par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
