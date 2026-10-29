# Tâche 279 (diagnostic seul) : les six coups de la crue 2024

La vérification d'intégration 274 (`docs/taches/rapport-codex-274-verif-integ.md`, fusionné ; archives
`C:\Users\msics\donjon\artifacts\verif-integ-0bad227\audit-12h\`) relève, nuit crue 2024 (départ tiré, joueur passif,
12 h, code `0bad227`), 15 entrées de frappe en neuf secondes et six coups portés ; Brune est inconsciente au relevé 600
et rétablie à 605. Aucun coup ne suit l'instant d'inconscience, aucun décès ; la même nuit sur `c870c8b` (archives
`C:\Users\msics\donjon\artifacts\verif-integ-c870c8b\`) n'avait pas de violence.

## Ce qu'il faut établir
Qui frappe qui, à quel instant, pour quel but et sur quel plan ; si chaque coup est justifié par les règles existantes
(défense, protection, prise d'un moyen au prix de la faute, désespoir corporel ; lots 4b, 4c, 223) ou s'il révèle un
défaut (riposte en boucle, secours non acquitté, cible non revalidée, prix de violence mal compté). Le premier écart de
la nuit entre `c870c8b` et `0bad227`, et le lot qui l'introduit si on peut le désigner par les seuls rapports et la
chronique (pas de bissection longue). Les captures avant le premier coup, après le dernier, et à 600/605 : monde, rendu
et scène identiques après recharge.

**Diagnostic seul : aucun fichier de `donjon/`, `tools/`, `tests/` ni scénario modifié.** Rejeu de la nuit actuelle et
de la nuit `c870c8b` détachée (worktree détaché, jamais le dépôt principal), un processus à priorité réduite à la fois.
Pas de Luna, pas de suite complète, pas de banc comparatif. **Poste : le PC fixe.** Si un défaut est établi, propose un
petit lot avec son invariant, sans le corriger.

## Livraison
Branche `codex-coups-crue-2024` : rapport d'une page `docs/taches/rapport-codex-279-coups-crue-2024.md` et entrée dans
`docs/etat-dev.md`, commit, poussée ; si elle échoue depuis le PC fixe, laisse le commit local et donne son hash, sans
passer par l'API GitHub. Bruts dans `C:\Users\msics\donjon\artifacts\coups-279\`. Termine par `LOT TERMINÉ` (résumé
d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
