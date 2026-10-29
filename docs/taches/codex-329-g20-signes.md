# Tâche Codex 329 : G20, les signes et attitudes rendus par le moteur

Lot G20 de la [feuille de route de la refonte du MJ](../plan-refonte-mj.md), après G5 (lot 323, branche
`codex-g5-perception`, livrée et en attente de fusion). **Base : la branche `codex-g5-perception`**, pas `integration`.
Lis `AGENTS.md` (contrat du MJ, « Mécanique » : les signes perçus sont des informations mécaniques), `docs/conception-refonte-mj.md`
(ligne G20), le rapport 176 (banc `attitudes`, branche `codex-banc-attitudes` non fusionnée, versée dans G20) et le rapport 323.

## L'invariant
**Une attitude ou un signe affiché d'un personnage (« Ilse tremble », « Brune semble guetter la réserve ») est le texte
d'un signe ou d'une impression encore perçus par Corvus, rendu par le moteur ; un signe disparu au moment de l'écriture
n'est plus affiché.** Aucun geste, état mental ni intention privée inventés ; une impression reste présentée comme une
impression faillible. L'extraction d'attitude par l'audit narratif commun se retire dans ce lot pour ces réponses moteur,
la garantie étant fournie ; la prose libre qui prête une attitude garde ses contrôles actuels.

## Vérification
- Les cas du lot 176 repris (banc `attitudes`), un autre PNJ, et un signe qui disparaît entre la préparation et
  l'écriture : texte, scène et carte identiques après recharge ; MJ simulé sans réseau.
- Luna : **une passe** de `signes-ecart`, `signes-guet` et `attitudes`, référence lue du cache : zéro extraction
  d'attitude par audit commun, aucun geste ni état mental inventé. Si la revue automatique bloque Luna, laisse la commande
  exacte dans `C:\Users\msics\donjon\artifacts\g20-329\luna-a-jouer.txt`.
- Tests ciblés des fichiers touchés ; pas de suite complète ni de banc PNJ.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Recouvrements possibles avec le lot 328 (G6, même base) :
signale-les.

## Livraison
- Branche `codex-g20-signes`, base `origin/codex-g5-perception`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-329-g20-signes.md`, entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g20-329\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
