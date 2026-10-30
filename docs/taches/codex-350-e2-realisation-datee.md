# Tâche Codex 350 : E2, le verdict temporel dépend d'une réalisation datée unique

Deuxième lot de l'échéance négociée, après E1 (lot 348, fusionné : référence temporelle canonique d'une obligation,
lue par `agendas`). Conception : `docs/conception-menace-echeance.md`, sections 3, 5 (ligne E2 et preuve commune P)
et 6 (arbitrages acceptés le 2026-10-30, à ne pas rouvrir). Lis `AGENTS.md`, `docs/etat-dev.md` (court), la conception
et le rapport 348. Pour un lot ancien (224 service non défait, 238 trace des services, 242 suivi des délégations),
cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant (un seul)
**Une obligation qui porte une limite (E1) reçoit un verdict « tenue à temps » ou « en retard » d'après un instant de
réalisation unique, daté par le moteur au moment où l'effet promis devient réel (livraison remise, tâche accomplie),
jamais d'après le moment où quelqu'un le constate.** Le verdict est enregistré une fois, sauvegardé, identique en laps
continu ou découpé et après recharge. Dépasser la limite clôt la prestation datée et passe par le traitement comptable
existant (remboursement unique), sans sanction nouvelle ni délai de grâce (arbitrage 3) ; la connaissance du retard et
toute réaction relationnelle ne viennent que d'une preuve reçue (constat, parole entendue). Une étape d'un plan devenue
sans objet après la clôture est arrêtée.

Toujours sans appelant qui crée une limite négociée : les épreuves posent la limite par données de test, avec l'API
d'E1. Aucun schéma joueur, rendu nouveau ni consigne au MJ (E4 à E6).

## Épreuves (preuve P en plus)
Livraison d'une part et tâche ponctuelle, chacune réalisée à T−1, T et T+1 dixième ; constat tardif d'une réalisation
à temps (reste « à temps ») ; remboursement unique en retard, jamais deux fois ; arrêt de l'étape périmée ; mêmes mots,
monde et comptes après recharge. Obligations sans limite : comportement exact inchangé.

## Vérification
Tests ciblés et voisins (preuve des engagements, comptes, services rendus, socle des agendas). Changement de
comportement sur les seules obligations à limite (aucune dans les scénarios) : **empreintes 2 h, quatre graines, Relais,
auberge, mine** doivent rester identiques ; sinon expliquer l'écart. Pas de suite complète, ni Luna, ni banc long.

## Contraintes
**Poste : le PC fixe.** Fichiers prévus : `donjon/agendas.py`, points de réalisation dans `donjon/echanges.py` et
`donjon/biens.py`, `pnj.py`/`temps.py` seulement si l'ordonnancement l'exige. Ne touche ni `paroles.py`, ni
`narration.py`, ni `page.html` (lots 349 et 351 en cours). Priorité réduite, deux processus au plus.

## Livraison
- Branche `codex-e2-realisation-datee`, base `integration`, poussée vers origin
  (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-350-e2-realisation-datee.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md`, section « Lots non fusionnés ».
- Bruts dans `C:\Users\msics\donjon\artifacts\e2-350\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
