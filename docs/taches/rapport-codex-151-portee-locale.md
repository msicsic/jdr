# Lot 151 — Refus local de portée

27 octobre 2026. Branche `codex-portee-locale`, **non fusionnée**, base
`4641dc3` (intégration). Aucun changement de `main`.

## Invariant et changement

Dans la boucle de validation de `MJOpenAI._echanger_prepare`, `HorsDePortee`
retourne directement `reponse_du_moteur(exc)`. Le joueur lit le refus exact,
sans explication de Luna ni audit, sans déplacement, temps, jet ou geste.
L’`attendu` reste dans la trace MJ. Les autres erreurs gardent la correction
ordinaire ; la parole attendue conserve son traitement moteur antérieur.
Assemblage des requêtes, fournisseurs, schéma et consignes inchangés.

**Limite de livraison : L5 partiel.** La préparation existante s’arrête au
premier refus : toutes les cibles éloignées d’une proposition composée ne sont
pas recensées. Les vérifications suivantes ne prouvent pas non plus que toute
la proposition serait valide au contact. Un essai de collecte dans le contrôle
commun de proximité a montré que les préparateurs ont d’autres validations
dépendantes de la distance (géométrie du passage, combustible accessible).
Cet essai a été retiré ; aucun contournement par objet, scénario ou texte.
Garantir les deux propriétés exige une reprise coordonnée des préparateurs,
hors du périmètre de fichiers de ce brief. Le raccourci seul est livré.

## Vérifications

- Ciblés retenus : 28 tests verts (portée, révisions, relances), puis cinq
  tests de portée verts, dont deux nouveaux. Vraie console, sauvegarde et
  rechargement : barricade à six mètres, prise de crochets, même saisie au
  contact donnant une fiche, cible inconnue corrigée. Un seul appel
  d’interprétation pour le refus, aucun audit. Comparaison de tout l’état hors
  conversation et archive du refus exact ; souvenirs initiaux préenregistrés.
- Suite complète unique : **2 162 tests, 242 fichiers, 16 ignorés, zéro échec
  d’assertion, une erreur TUI Windows**, 3 514,6 s. Le seul test TUI concerné
  est repris seul, vert (3,5 s), sans changement de code ni seconde suite.
  Un worker à priorité réduite pour cohabiter avec l’autre lot (au lieu des
  deux indiqués au brief) ; la vérification a dépassé le créneau du lot.
- Luna `gpt-6-luna`, copies, une passe de neuf scripts : sept
  `sous-obstacle-*`, atelier et Relais. Référence `cdaf371` jouée une fois,
  neuf parties manquantes rangées dans le cache ; aucun rejeu.

| Mesure | Référence | Lot |
|---|---:|---:|
| Tours MJ / appels | 29 / 72 | 29 / 80 |
| Appels par tour | 2,48 | 2,76 |
| Secondes par tour | 7,96 | 8,68 |
| Tours finissant sur « Approche-toi » | 3 | 4 |
| Replis / erreurs / défauts de recharge | 0 / 0 / 0 | 0 / 0 / 0 |

Coup de pied du Relais : **3 → 1 appel**, 10,92 → 4,99 s, refus exact du
moteur. Saut avec perche : **3 → 1 appel**, 10,74 → 4,19 s. La question de
passage du Relais reste à un appel. Les autres variations de Luna font monter
le total ; aucune amélioration globale ni gain de vitesse garanti sur ce poste
partagé. Le choix sémantique du geste et de ses cibles reste probabiliste.
La passe mesure le raccourci retenu ; l’essai de collecte retiré n’est pas livré.

Bruts : `artifacts/portee151/` et
`artifacts/bancs-multi/20261027-013300-15628/`. Les premiers essais de tests
ont échoué sur les droits temporaires du bac à sable ; exécutions utiles hors
restriction. Aucune clé Git de signature configurée : commit non signé.
Code `3805393`. Branche seule poussée ; aucune fusion.
