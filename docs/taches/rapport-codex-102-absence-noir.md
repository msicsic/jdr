# Lot 102 — Non-perception et absence

26 octobre 2026. Branche `codex-absence-noir`, non fusionnée, base `e218907`.
Invariant : ne pas voir n'établit pas une absence. Reproduction console avant
correction sur copie : fausse absence affichée et sauvegardée sous verdict
neutre, malgré Ilse `[2,4]`, Brune `[4,5]` et Corvus dans l'antichambre noire.
La phrase exacte et son verdict historiques ont aussi été rejoués.

`perception.couverture_vue` calcule l'étendue réellement vue à partir du champ
spatial courant (ou de l'éclairage par pièce), sans liste d'entités cachées ni
exploration mémorisée. `MJ._echanger` la transmet aux voies communes de narration.
La règle de portée de l'audit refuse une absence hors couverture, même dans un
segment mixte classé neutre ; son `attendu` restitue la perception actuelle.

**Vérifications.** Neuf tests ciblés verts : cas réel et objet présent dans le
noir refusés puis corrigés, vue éclairée et fouille exécutée toujours admises ;
état, affichage, conversation et narration vérifiés après recharge.
Suite complète unique : **1 982 tests, 16 ignorés, 208 fichiers, 1 907,24 s**,
deux processus réduits ; seule erreur : remplacement temporaire TUI avant
action (`WinError 5`), **test isolé vert en 3,05 s**, sans changement de code
ni seconde suite. Un import du lanceur auxiliaire a été corrigé avant ce rejeu.
Passe Luna unique, ChatGPT `gpt-6-luna`, medium/libre, priorité réduite, copies :

| Script | Appels/tour MJ, référence lot 99 → lot 102 | s/tour, référence → lot 102 |
|---|---:|---:|
| signes-noir | 2,00 → 2,00 | 7,92 → 11,59 |
| soir-noir | 4,20 → 4,20 | 13,12 → 13,38 |
| atelier | 2,77 → 3,18 | 9,85 → 9,27 |

17 tours MJ, 58 appels, 10,6 s/tour ; aucune fausse absence observée ni défaut
de recharge. Références `b0042c9` uniquement relues ; charges différentes,
aucune conclusion causale de latence.
`soir-noir` conserve « Ta demande n'a pas été exécutée. Reformule-la. » après
trois appels, et une voix prétend avoir déjà refusé son nom alors qu'elle l'a
donné : défauts distincts, hors périmètre. La mention de Brune signalée par le
détecteur reprend le nom prononcé par Corvus.

**Limite.** La couverture est déterministe ; le classement sémantique de la
phrase reste faillible : le verdict historique erroné rejoué tel quel laisse
encore passer la phrase. Les tests simulés prouvent la chaîne de refus et de
sauvegarde, pas la compréhension de Luna. Bruts dans `artifacts/absence-noir/` et
`artifacts/bancs-multi/20261026-022930-37884/`.
