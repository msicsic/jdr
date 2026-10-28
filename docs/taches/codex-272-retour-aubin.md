# Tâche Codex 272 (diagnostic) : le dernier retour suspect, Aubin au Relais 2024 (117518)

Après les lots 265 et 271 (fusionnés), le compteur 219 (`tools/detecter_changements_avis.py`) ne garde qu'un retour
suspect sur vingt nuits de 4 h : **Aubin, Relais, graine 2024, retour à `117518`** (dixièmes de seconde depuis le
départ), classé `repetition_sans_entree_nouvelle`. Bruts du banc 271 : `C:\Users\msics\donjon\artifacts\reveils-271\`
(nuit `relais-2024` compressée, `bilan.json`).

Invariants en jeu : **réessai lié à l'obstacle** (lot 225 : un but abandonné ne revient que sur une cause levée ou un
moyen nouveau, jamais par le délai) et **continuité de l'engagement** (lot 213 : un recours ne cède qu'à un palier
supérieur ou une marge `INERTIE + VOL/4`).

**Diagnostic seul : aucun code du jeu modifié.**

## Ce que le rapport doit établir
1. **Reproduire** sur l'intégration actuelle (Relais, graine 2024, départ tiré, joueur passif comme le banc 271, 4 h) ;
   capturer avant l'abandon et avant le retour ; monde et rendu identiques après rechargement.
2. **La cause de l'abandon** (obstacle retenu ou non, sa forme, palier qui l'a interrompu) et **ce qui autorise le
   retour** : une entrée nouvelle réelle que la sonde ne voit pas (dire laquelle et pourquoi elle lui échappe), ou aucune.
3. **Verdict** : retour justifié (et la preuve que la sonde devrait reconnaître), ou défaut (la règle commune en cause
   en une phrase, sans exception propre à Aubin, au Relais ou au but) et le petit lot de correction proposé.

Lot de 30 à 45 minutes. **Poste : le laptop** (l'utilisateur y travaille), un processus à priorité réduite, une nuit à
la fois. Pas de Luna, pas de suite complète, pas de banc comparatif.

## Livraison
- Branche `codex-retour-aubin` : seulement `docs/taches/rapport-codex-272-retour-aubin.md` (une page) et une entrée
  « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\retour-272\`. Commite ; pousse
  si tu peux, sinon laisse le commit local et dis-le. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
  ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
