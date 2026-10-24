# Tâche Codex 40 : ce qu'on ne voit pas d'un regard n'est pas le résultat d'une fouille

Branche `codex-absence-vue` (elle porte ce fichier, issue de l'intégration **8443458**), worktree dans
`tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un invariant, vérification
minimale, rapport d'une page. **Luna disponible sur ce poste** (`SEUIL_AUTH` vers le coffre du dépôt principal ;
copies seulement).

Un autre lot tourne sur l'autre poste (38, coût des recherches). **Ne touche ni `planification.py`, ni
`part_estimee.py`, ni `obstacles.py`.**

Lis `AGENTS.md`, `docs/etat-dev.md` (entrée `codex-perception-geste`, lot 34), `docs/contrat-mj.md`, le rapport
`docs/taches/rapport-codex-34-perception-geste.md`, puis `donjon/narration.py` (`INSTRUCTIONS_AUDIT`, le classement
des verdicts, `invention_protegee`), `donjon/mj.py` (ce que reçoit l'auditeur : `perception`, `objet:<id>`).
Bruts de la vérification : `C:\Users\msics\donjon\artifacts\verif-luna-8443458\relecture.txt` (atelier n° 9 et
n° 12, les deux passes) et la référence `artifacts/verif-luna-3b6415b/`.

## Le constat (vérification Luna d'intégration 8443458 contre `main` 42bb9c0, deux passes)
Depuis le lot 34 (« le résultat d'une perception active, positif ou négatif, est mécanique… sans perception
exécutée, c'est invention_protegee »), l'auditeur classe `invention_protegee` une absence constatée d'un simple
regard : « Tu ne vois pas d'autres outils traîner dans la cour. » Atelier n° 9 (« y a-t-il des outils… ») :
2 appels sur `main`, 6 dans chaque passe de l'intégration, puis un repli (passe 1) ou une réponse détournée
(passe 2) ; atelier n° 12 (passe 2) : même refus, puis le MJ renvoie une question au joueur. Six refus de cette
nature sur l'intégration, aucun sur `main`.

## L'invariant
Ce que Corvus voit ou ne voit pas **maintenant**, dans la portée de la perception courante que l'état fournit
(les objets `objet:<id>` perçus sont exactement ceux qu'il voit), est **mécanique avec la source `perception`**,
y compris l'absence d'un objet visible (« tu ne vois pas d'autre outil ici »). Seul ce qu'une perception active
découvrirait au-delà (fouiller, chercher des traces, écouter derrière une porte, ce qui est caché, dans un
contenant fermé, hors de vue ou dans le noir) exige une perception exécutée par le moteur ; sans elle, c'est
toujours `invention_protegee`. Corrige la règle commune (consignes de l'auditeur, et ce qui lui est fourni pour
juger la portée de la vue s'il le faut), pas le cas des outils ni la cour de l'atelier. Le lot 34 doit continuer
de tenir : « j'écoute à la porte » sans perception exécutée reste refusé ; une absence affirmée d'un élément caché
ou hors de vue aussi.

## Vérification (minimale)
- Tests après rechargement (le fichier du lot 34 ou un nouveau), chaîne complète avec MJ simulé : l'absence d'un
  objet visible admise avec la source `perception` (le cas réel de l'atelier et un autre de même nature, une autre
  salle) ; une absence derrière une porte, dans un contenant fermé et dans le noir, toujours refusée sans
  perception exécutée.
- Luna, **une passe** : `atelier`, `crypte` (écoute à la porte), `luna-restes-ambiance`, `signes-noir`,
  `tools/banc_multi.py` avec la référence `main` lue du cache ; appels par tour, refus de cette nature, textes
  affichés cités pour atelier n° 9 et n° 12 et crypte « j'écoute à la porte ».
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md` (la portée de la vue et la perception active),
`docs/etat-dev.md` (« Branche `codex-absence-vue`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-40-absence-vue.md` (invariant, fonctions, mesures Luna, limites).
