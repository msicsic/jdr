# Tâche Codex 215 (diagnostic) : ce que la crue a perdu en richesse et en recours avec les lots 205 et 211

Priorité de l'utilisateur : la richesse des comportements des PNJ. Deux corrections justes, fusionnées le 2026-10-27, la font
baisser dans la crue :
- **205** (un seul juge pour le péril d'eau et l'abri) : attente urgente crue **77,5 → 102,5**, hameau **27,5 → 111,25** PNJ·min ;
  Brune (hameau 2024) active et endort huit fois son agenda ; Gorm 125 min sans but ;
- **211** (un PNJ ne sait plus où est un personnage qu'il n'a pas localisé) : S/F/D crue **23/6,75/2,625 → 14/6,75/2** ; attente
  crue **102,5 → 178,75**.
Les rapports disent que ces baisses viennent en partie d'une connaissance indue (on retrouvait ses proches par leur position
réelle). **Diagnostic seul : aucun fichier du jeu modifié**, pour savoir ce qui est une perte juste et ce qui est un manque à
combler par une mécanique commune.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (212, 213) : **un seul processus**,
priorité réduite. **Bruts dans `C:\Users\msics\donjon\artifacts\richesse-215\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne)
ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 183 (mesure S/F/D, fonction `cats` de `artifacts/dormants-183/analyser.py`), 205 et 211 (bruts
`C:\Users\msics\donjon\artifacts\evacuation-205\` et `localisation-211\` sur ce poste), 37 et 69 (chercher quelqu'un, indices).

## Ce qu'on te demande
1. **Les interactions perdues** : crue et hameau, quatre graines, 4 h, intégration `d2243c2` contre `aadab7c` (avant 211) et
   contre `ef86cab` (avant 205) : lesquelles des signatures S disparaissent (qui, avec qui, quoi), à quelle minute, et pourquoi
   (le PNJ ne sait plus où est l'autre ; il reste à l'abri sans recours ; il cherche sans trouver ; autre).
2. **Les attentes** : ce que fait un PNJ pendant ces minutes « en attente » (quel besoin, quelle croyance manque), et s'il dispose
   d'un moyen commun qu'il n'emploie pas (appeler, chercher, demander où est quelqu'un, aller voir là où il l'a vu en dernier).
3. **Proposition** : pour chaque manque, l'invariant général (par exemple : un PNJ qui ne sait pas où est quelqu'un dont il a
   besoin le cherche ou l'appelle par les moyens communs), en petits lots d'un invariant chacun, classés par effet sur la richesse ;
   ce qui est une perte juste à garder. Une capture rechargeable par cas.

## Livraison
Branche `codex-richesse-crue` (depuis `integration`) : `docs/taches/rapport-codex-215-richesse-crue.md` (une page, tableau
perte → cause → juste ou manque → lot) et une ligne dans `docs/etat-dev.md`. Commit et poussée ; si la poussée est bloquée,
laisse le commit local et dis-le.
