# Lot 127 — mesure déterministe du coût des nuits

2026-10-26, PC fixe. Branche `codex-mesure-cout`, **non fusionnée**, base
`integration` **62429a8**. Outil et tests seulement, aucun fichier de `donjon/`
modifié, aucun Luna, aucune suite complète. Aucune clé Git de signature
configurée sur ce poste : commit non signé.

**Invariant.** `tools/mesure_cout.py` enveloppe `choisir`, `chercher`,
`_explorer_etats` et `gestes` dans un processus isolé, sans consommer le
générateur à l'avance ; restauration même en cas d'erreur. Nœuds de **toutes
les passes**, découvertes abandonnées comprises, au lieu de la dernière
passe seulement ; nœuds de certificats séparés, leurs générations incluses.
Une proposition immédiate ou différée vaut un geste généré. Le compteur
moteur compte les nœuds examinés, terminaux compris, pas seulement développés.

**Reproduction.** `C:\Users\msics\donjon\.venv\Scripts\python.exe
tools/mesure_cout.py --reference 42bb9c0 --branche 62429a8 --verifier
--sortie artifacts/cout-127.json`. Trois nuits par commit : auberge fixe/tiré,
mine fixe, graine 1985, 12 h. Deux mesures instrumentées et un témoin sans
sonde par nuit. Worktrees détachés nettoyés, références figées en commits,
cache partagé `artifacts/references/<commit>/mesure_cout/` (configuration,
source de la sonde et vérification dans la clé). Deux calculs réduits au plus.
JSON : totaux, moyennes horaires, cellules heure × PNJ × but, empreintes.
Heure de début de recherche ; `__choix__` pour un choix comparant plusieurs buts.
Graphes réutilisés distincts des réponses mémorisées : sans réponse mémorisée,
une recherche reste « neuve » selon le banc. Détails dans « Outils de mesure ».

**Mesures.** A = `42bb9c0`, B = `62429a8`. CPU témoin sans sonde, indicatif :

| Nuit/version | Choix | Recherches | Neuves/reprises | Nœuds | Gestes générés | CPU s |
|---|---:|---:|---:|---:|---:|---:|
| Auberge fixe A | 8 644 | 4 998 | 1 556/3 442 | 936 174 | 2 853 744 | 67,94 |
| Auberge fixe B | 10 704 | 9 012 | 2 254/6 758 | 310 656 | 2 520 196 | 106,25 |
| Auberge tiré A | 8 384 | 3 013 | 1 328/1 685 | 694 876 | 2 453 078 | 55,31 |
| Auberge tiré B | 8 722 | 5 083 | 1 528/3 555 | 699 224 | 5 165 837 | 177,30 |
| Mine fixe A | 7 052 | 4 399 | 1 813/2 586 | 993 617 | 11 634 905 | 167,19 |
| Mine fixe B | 6 677 | 4 818 | 1 065/3 753 | 195 001 | 1 062 697 | 53,09 |

Ratios B/A fixe/tiré/mine : CPU **1,56/3,21/0,32**, recherches
1,80/1,69/1,10, nœuds 0,33/1,01/0,20, gestes 0,88/2,11/0,09.
Le meilleur suivi varie : recherches en fixe, gestes en tiré, nœuds à la mine.
CPU par geste : 23,81→42,16 / 22,55→34,32 / 14,37→49,96 µs ; ce quotient
inclut tout le reste de la nuit, ce n'est pas le coût propre de `gestes`.
CPU instrumenté A→B : 71,66→114,23 / 59,02→177,12 / 180,73→55,02 s.
Versions et témoins successifs, charges variables : **aucun gain CPU causal**.

**Compteurs et CPU historiques.** Les [lots 98](rapport-codex-98-profil-compare.md)
et [109](rapport-codex-109-recherche-tiree.md) ont les mêmes nombres de recherches
sur 8–12 h : ancien→actuel, fixe ×1,58, tiré ×1,86 ; choix ×1,35 / ×1,19.
Les générations du lot 109 donnent environ ×0,65 / ×2,12, contre les nœuds
consignés ×0,31 / ×0,89. CPU de la tranche : lot 98 ×1,57 / ×3,29 ; lot 109
×1,49 / ×3,05. **Parmi ces compteurs comparables, les recherches suivent le
mieux le CPU fixe, les générations le CPU tiré.** Aucun compteur unique ne
reproduit les deux : le coût unitaire change aussi (lot 109, génération fixe
971→1 848 µs, tirée 911→1 244 µs, mesures inclusives instrumentées).
Le [lot 114](rapport-codex-114-verif-integ.md) donne le CPU 12 h ×1,65 / ×2,64,
sans générations publiées : aucun classement supplémentaire possible.
Ces versions diffèrent de 62429a8 ; leurs bruts ne sont pas présents aux
chemins indiqués. Aucun ajustement statistique entre versions différentes.

**Vérification et limites.** **Six nuits sur six**, deux exécutions aux compteurs
identiques et empreintes identiques au témoin sans sonde (18 nuits longues).
Sommes des cellules vérifiées contre chaque total. Quatre tests ciblés verts : ventilation et
frontière horaire, cache et changement de graine, refus de cacher une divergence,
vraie nuit courte avec/sans sonde. Exécution hors bac à sable nécessaire pour
les ACL des dossiers temporaires Windows. Empreintes de chronique, récit, souvenirs,
mesures, repères du banc et état final complet ; aucun compteur ajouté au moteur.
Les développements stricts après filtrage des terminaux ne sont pas exposés.
Les entiers mesurent un volume de travail et ne
prouvent ni un gain CPU de 5 %, ni un coût constant par opération, ni l'identité
du comportement entre deux versions différentes du jeu.
