# Lot 230 — Tenir le lieu annoncé à un appel

28 octobre 2026 — Branche `codex-rendez-vous-tenu`, non fusionnée ; base
`1e09926` de l'intégration. Aucun Luna ; aucun changement aux fichiers des
lots 195, 218, 225/229 ou 228. Bruts :
`C:/Users/msics/donjon/artifacts/rendez-vous-230/` (`banc-final.json`, `bilan-consolide.json`).

**Invariant.** `appel.decider` refuse l'invitation incompatible avec un départ
prioritaire ; un trajet vers l'appelant permet « J'arrive ! ». `_attendre_qui_vient`
retient aussi les départs sans rapport avec l'interlocuteur. Seul un palier
strictement supérieur autorise `rompre_attente` : clôture avant reprise,
annonce par l'ouïe, destination invalidée si entendue. Raccords au choix,
à la défense et à l'alerte ; ni nouveau palier ni délai anti-appel. `tenir` et
`plan_venir` conservent la destination jusqu'au contact, au constat vide ou à
la rupture entendue : délai/chemin coupé ne prouvent pas l'absence. Sauvegarde inchangée.

**Reproduction.** Scène historique `mireille_cherche_odile`, joueur au grenier,
rejouée sur copies : six invitations de Mireille, dont cinq à Mathurine,
**→ une**, trois voix **→ deux**, demande de vivres conservée ; oracle historique
inchangé. `bd45f65` donne une promesse de vivres à Mathurine dans cette scène,
mais possède déjà le défaut : chroniques **en cache**, hameau 7/42/2024,
Gorm invite Maël à **35**, part à **292**, sans retrouvailles ni rupture annoncée.

**Vérifications.** **105 ciblés consolidés verts / neuf fichiers**, dont douze nouveaux tests.
Scène réelle, hameau (appel déclaré : 221 permet d'abord une question à Aubin),
autre paire au Relais, palier égal/supérieur, urgence immédiate, rupture
audible/inaccessible, joueur visible, chemin coupé après échéance. Monde,
rendu et ouïe rechargés, laps entier/découpé.

**Banc : 20 paires × 4 h contre `1e09926`.** Les vingt références manquantes
ont été calculées une fois et mises en cache. Zéro plantage/usurpation.
Passe finale : vingt références relues du cache ; état final, chronique et avis
identiques à la première mesure de branche.
Les deux suspects 219 sont intégralement identiques, nuit/PNJ compris ;
préemptions **87 → 70**, à expliquer **85 → 70**, cycles **521 → 524**,
dérives ouvertes **241 → 216**. Pas de nouvelle alerte de répétition ou
d'alternance par nuit/PNJ ; une répétition d'agenda disparaît en crue 2024.

| Scénario | Appels | Réponses | Retrouvailles | Suspects 219 |
|---|---:|---:|---:|---:|
| Relais | 2 → 2 | 8 → 9 | 2 → 1 | 0 → 0 |
| Mine | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| Auberge | 2 → 2 | 3 → 3 | 1 → 1 | 2 → 2 |
| Crue | 6 → 7 | 22 → 23 | 4 → 2 | 0 → 0 |
| Hameau | 1 → 1 | 4 → 4 | 1 → 1 | 0 → 0 |

Totaux sur quatre graines. Nouvelle alerte `fige_presse`, **Gorm/crue 7** :
130 minutes de devoir en attente, sans attente de rendez-vous au relevé final.
Même devoir en attente à la fin de la référence, mais entrecoupé de gardes.
**3 → 4 alertes** : aucune amélioration uniforme de l'attente revendiquée.
Observations non certifiées nouvelles pour Aubin (Relais 2024/crue 7), malgré la baisse globale.

**Suite complète unique : 2 508 tests / 290 fichiers, 2 530,264 s,
sept échecs et une erreur bruts.** Trois échecs reproduits sur la copie
`1e09926` : Lucien (trois salles au lieu d'une), deux MiMo (`6 != 5`), laissés
intacts ; **suite non verte**. Cinq prémisses/oracles repris : clôture du départ
urgent ; demande réussie après rupture sans fausses retrouvailles ; capture
auberge (deux vues historiques inchangées) ; gain de préparatifs conditionné aux
devis négatifs, cas dédiés conservés ; recharge avec lanterne déclarée à sec et
au contact, la nuit pouvant la laisser portée avec du combustible. Paiement,
livraison, recharge et rendu rechargés contrôlés. Décision/clôture finalisées
pendant la passe, puis neuf fichiers repris ; aucune seconde suite complète.
Créneau dépassé par les validations, dont 42 minutes pour la seule suite.

**Limites.** Rupture inaudible ou départ muet du joueur : lieu vide à constater,
aucun savoir distant. Un chemin coupé peut laisser la venue en attente des
besoins supérieurs. Attente du lieu, pas de chaque case. Ni absence universelle
de boucles, ni disponibilité après rencontre, ni repas de Mathurine garantis.
