# Tâche Codex 433 : une entité créée par une proposition est désignable dès sa création

Défaut établi par le lot 432 (`docs/taches/rapport-codex-432-refus-rendu-attendu.md`, fusionné, « Cause de R58 » ;
capture versionnée `tests/data/refus-rendu-432.json.gz`, bruts `C:\Users\msics\donjon\artifacts\refus-rendu-432\`,
PC fixe). Sur la capture réelle du lot 423, `preparer_complements` ajoute `detail_aubin_mains` sur sa copie ;
`noms.reference` lui calcule `element_47`, mais ce nouvel objet n'a pas encore d'entrée dans `references_personnes`.
`voix.reel(element_47)` renvoie donc `None`, et le rendu refuse une entité pourtant visible. Le 432 a rendu ce refus
corrigeable (`attendu`), sans réparer l'inscription. Le même chemin attend toute création interactive admise (lots
421, 422, 427, et 431 en cours) : sans référence résoluble, le geste qui suit la création ne peut pas viser l'objet.

Lis `AGENTS.md` (contrat du MJ, « Interactif »), `docs/etat-dev.md` (court), le rapport 432, et `donjon/noms.py`,
`donjon/voix.py` (`reel`), `faits_locaux.preparer_complements`.

## Invariant (un seul)
**Toute entité ajoutée par une proposition admise (complément, détail, objet matérialisé) reçoit sa référence publique
dans le registre commun au moment de sa création, sur la même copie transactionnelle ; sa référence se résout dans les
attestations, le rendu, la suite jointe et après recharge, exactement comme une entité préexistante. Une proposition
rejetée n'inscrit rien.** Une seule voie d'inscription, commune aux compléments, aux matérialisations G12/G14 et aux
qualifications ; aucune exception d'objet. Le contrôle de non-fuite reste entier.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/noms.py`, `donjon/faits_locaux.py`, `donjon/voix.py` au besoin,
tests. Lot en cours sur des fichiers voisins : 431 (admission préalable, `portee_narrative.py`, `mj.py`) ; évite
`mj.py` et `portee_narrative.py`. Lots en cours : 402 (calcul), 419, 429 (K1). Pendant S1, n'ajoute aucun registre
d'esprit (le registre des références est celui du monde). Deux processus au plus, priorité réduite.

## Vérification
Cas réel : la capture R58 rejouée avec MJ simulé : l'enrichissement des mains d'Aubin est admis, décrit, et sa
référence résout avant et après recharge. Autre cas : une matérialisation G14 (éclat de bois de l'atelier, ou pierre
mouillée du Relais) suivie de son geste (`prendre`) dans la même proposition, objet unique visé, état et vue après
recharge ; proposition rejetée : registre inchangé. Tests voisins verts (rendu 432, ciblage d'ambiance, création
interactive, qualification, noms, références). Pas de suite complète, ni Luna.

## Livraison
Branche `codex-reference-neuve`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
de l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-433-reference-neuve.md` ; entrée
« non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
Bruts dans `C:\Users\msics\donjon\artifacts\reference-neuve-433\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS :
<fichier de fin>` ou `QUESTION : …`.
