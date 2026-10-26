# Lot 98 b — relever les obstacles une fois (2026-10-26)

Branche `codex-profil-compare`, **non fusionnée**, base **677f4c1** (moteur
**61c854a**). Aucun changement des relances, décisions, coûts ou scénarios ;
aucun Luna. La décision sur leur cadence reste à l’utilisateur.

**Invariant.** Pendant `_moyenne`, le monde cru et son sol sont constants.
Les cases libres sont exactement le sol moins les positions rendues par
`spatial._bloquantes`, avec les mêmes règles de position, incorporation et
blocage. Le relevé est local à l’appel, sans cache supplémentaire ni état
sauvegardé : un balayage des objets remplace un balayage par case.
Le chemin `pur` garde `_case_libre` case par case et recalcule les tables ;
`spatial.VERIFICATION` contrôle toujours les moyennes gardées avec cet oracle.
La clé existante de la moyenne reste inchangée. Contrat documenté dans
`docs/plan-planificateur.md`.

**Mesure du levier.** Le profil 98 attribuait à cet appelant **59,31 des
65,00 s instrumentées** de `_bloquantes` en fixe. Les couples ci-dessous
mesurent le gain observé, sans extrapoler les secondes de `cProfile`.
Graine 1985, 12 h ; paires simultanées, priorité réduite, deux calculs au plus,
sans cache de temps, poste partagé et affinité libre. Chaque flèche compare
uniquement les versions lancées ensemble ; branche répétée entre cohortes.

| Nuit | `42bb9c0` → branche, CPU | Rapport | Base → branche, CPU | Gain | 8–12 h ancien → branche / base → branche |
|---|---:|---:|---:|---:|---:|
| Auberge fixe | 120,11 → 232,05 s | ×1,93 | 250,27 → 240,92 s | 3,74 % | 96,80→153,39 / 164,08→158,84 s |
| Auberge tirée | 98,81 → 281,53 s | ×2,85 | 292,23 → 286,16 s | 2,08 % | 71,11→235,73 / 245,30→240,86 s |
| Mine fixe | 292,47 → 95,70 s | ×0,33 | 91,72 → 89,97 s | 1,91 % | 255,31→49,42 / 48,36→47,72 s |

**Contrôles.** Onze tests ciblés verts, dont un nouveau test sur les captures
auberge et mine à 480 minutes : tour moteur comparé à l’oracle direct,
diagnostics hors durées, monde, lignes joueur, `regarder` et `scene_percue`
identiques après recharge. Deux démarrages du lanceur ciblé ont été bloqués
par les permissions temporaires du bac à sable Windows ; reprise hors bac
à sable réussie, aucun correctif moteur ajouté pour ce problème d’exécution.
`comparer --calcul` : **trois nuits base/branche identiques**, et trois
identiques entre répétitions branche ; douze recharges vertes.
Choix, recherches et nœuds inchangés (356 339 / 635 920 / 187 010 nœuds).
Empreintes 2 h, quatre scénarios × quatre graines : **16 identiques** ;
référence 677f4c1 absente, calculée une fois depuis l’archive locale et rangée
dans le cache partagé autorisé, sans nouveau worktree ni modification du code du dépôt principal.
`VERIFIER` + `spatial.VERIFICATION=1`, auberge 42 tirée, 2 h : **aucun écart ni
borne**, 1 221 nœuds, **392,25 s CPU**, recharge correcte.
Suite complète unique : **1 972 tests, 16 ignorés, aucun échec ni erreur**,
207 fichiers, deux processus à priorité réduite, **2 079,91 s écoulées**.
Le fichier moteur livré garde le SHA-256 enregistré avant les couples CPU.

**Limites et suite.** **Seuil ×1,5 non atteint**, fixe comme tiré ; ce lot
ne permet pas d’avancer `main`. Une paire par nuit ne donne
pas de garantie statistique ; les charges concurrentes peuvent varier.
Les répétitions de branche varient de 1,6 à 6,0 % entre cohortes : les gains
observés ne sont pas établis statistiquement.
Pas de deuxième levier ouvert : la vérification demandée occupe le créneau.
Le créneau de 45 minutes est dépassé par les douze nuits CPU, le contrôle
renforcé et la suite complète prescrits.
Bruts, conditions, recharges, archives et lanceur séquentiel dans
`artifacts/obstacles-98b/` ; reproduction CPU/empreintes par
`tools/banc_obstacles_98b.py` (archives locales de la base et de `42bb9c0`).
