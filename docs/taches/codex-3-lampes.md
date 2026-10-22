# Tâche Codex 3 : de l'huile pour une lampe

## Le manque (relevé par la branche `ressources`)
Un PNJ ne demande une part de combustible que pour se chauffer, jamais pour une lampe. À l'auberge,
un pot d'huile puis une burette ajoutés aux données n'ont presque jamais servi : la lanterne de
l'étable reste vide vers la 7e heure. C'est une limite du moteur, pas des données.

## Contexte à lire
`AGENTS.md`, `docs/plan-planificateur.md` (sections « Lumière », « Lumière et garde »),
`docs/plan-social.md` (parts, échanges, refus retenus), `docs/etat-dev.md` (entrées
`lumiere-besoin`, `entretenir-feu`, `pnj-lumiere-garde`, `ressources`). Une source qui consomme se
recharge de ce qu'elle brûle (`perception.recharge` : son contenu déclaré ; une lampe déclare son
huile) ; `alimenter` vaut pour tous ; la part de combustible (`echanges`, `planification`) ne sert
aujourd'hui que le froid et l'entretien d'un feu.

## À faire (règle commune)
1. Ce qu'une source brûle se demande, s'achète ou se prend comme toute part, pour le but qui emploie
   cette source : la lumière (une lampe, une lanterne, une torche si elle se recharge) comme la
   chaleur. Le donneur sert la part (il recharge la lampe ou remet l'huile), selon les mêmes règles
   (garde, méfiance, refus retenus selon leur cause, prix).
2. Le planificateur trouve ces moyens par ses gestes (pas de branche « huile ») : pour avoir de la
   lumière, recharger sa lampe vide avec ce qu'il porte, ce qu'il sait posé quelque part, ou une part
   demandée ou achetée à qui en a.
3. Données : remets à l'auberge (et à la mine si utile) l'huile que `ressources` avait essayée, en
   quantité qui garde la rareté, maintenant qu'elle peut servir.
4. Le joueur peut demander ou acheter de l'huile par la même règle (parole typée existante).

## Vérifications
- Tests après rechargement : le cas réel (auberge, la lanterne de l'étable vide ; quelqu'un demande de
  l'huile et la recharge) et un autre cas de même nature (mine, une lampe vide rechargée au bidon de
  la réserve ou par une part demandée).
- Suite complète verte (priorité réduite) ; `planification.VERIFIER` sur une nuit de chaque scénario.
- Bancs 8 h, `main` puis branche : auberge et mine (4 graines chacune, `--joueur dortoir` /
  `--joueur galerie`), plus Relais 8 graines `--joueur chambre_cloche` et crue `--joueur
  chambre_cloche` 4 graines : minutes dans le noir, lampes rechargées, parts d'huile demandées,
  données, achetées, refusées, minutes sans recours et en attente, usurpations et violations (aucune),
  temps d'une nuit. Et `tools/audit_nuits.py analyser` sur l'auberge et la mine, 8 graines × 12 h.
- Docs : `docs/plan-planificateur.md`, `docs/plan-social.md`, `docs/etat-dev.md` (« Branche
  `codex-lampes`, non fusionnée », compte de tests).

## Rapport
Dans `docs/taches/rapport-codex-3-lampes.md` : règle, fonctions, données, cas vérifiés, mesures
avant → après, limites.
