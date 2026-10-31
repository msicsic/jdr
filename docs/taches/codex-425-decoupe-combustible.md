# Tâche Codex 425 : découper un combustible compté par usages

Limite relevée par le lot 422 (G13, fusionné ; `docs/taches/rapport-codex-422-g13-qualification.md`, « Limites ») :
la découpe d'une planche **combustible** du Relais échoue déjà sur la base. Le morceau hérite de l'usage de
combustible sans compteur, et le moteur refuse l'état (`Combustible invalide`). Bruts :
`C:\Users\msics\donjon\artifacts\g13-qualification-422\diagnostics-base.log` (PC fixe). La découpe d'une planche
ordinaire à l'atelier fonctionne.

Lis `AGENTS.md`, `docs/etat-dev.md` (court), le rapport 422 et le contrat des lots (lot 78, cherche « pièce de lot »
dans `docs/historique-lots.md` ; lot 423, `contrats_lots`). Charges et combustion : `perception.recharge`, `matiere.py`.

## Invariant (un seul)
**Découper un bien qui porte une ressource comptée (charges de combustible, minutes de combustion) répartit cette
ressource entre le morceau et le reste en proportion de la masse, avec les mêmes champs que le bien d'origine ; la somme
est conservée et chaque partie reste un état valide.** Même règle pour le joueur et pour les PNJ, et pour toute
ressource comptée, pas seulement le bois.

Établis d'abord la cause sur la base (champ hérité sans compteur, ou compteur non partagé). Corrige la fonction
commune de découpe (`decouper`, les opérations, `matiere`), sans exception de scénario ni d'objet. Une découpe qui
laisserait une partie sous l'unité de la ressource est refusée avec un `attendu` (`donjon/refus.py`).

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/operations.py`, `donjon/matiere.py`, tests. Lots en cours : 402,
419, 424 (empreintes du 374), 426 (K0, `echanges.py`). Pendant S1, n'ajoute aucun registre d'esprit. Deux processus au
plus, priorité réduite.

## Vérification
Cas réel (planche du Relais découpée, morceau mis au feu : le feu brûle la part attendue) et autre cas (une bûche de
la réserve de l'auberge, ou une torche) dans la vraie boucle, avec MJ simulé et recharge : conservation de la somme,
partie trop petite refusée. Tests voisins verts (`test_lots`, `test_fabrication*`, `test_qualification`). Empreintes
2 h, quatre graines, Relais et auberge, si le code touche un chemin des PNJ. Pas de suite complète, ni Luna.

## Livraison
Branche `codex-decoupe-combustible`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
dépôt de l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-425-decoupe-combustible.md` ;
entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents
graves). Bruts dans `C:\Users\msics\donjon\artifacts\decoupe-combustible-425\`. Termine par `LOT TERMINÉ`,
`CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
