# Lot 101 — Mots courants et emploi technique

Branche `codex-mots-courants`, non fusionnée, base `31e3f9c`. Le garde commun
`narration.voix_auteur` sépare les désignations techniques et les réserves sur la preuve
des emplois concrets. Une réserve n'a pas besoin de nommer le moteur : passif de preuve
sans support concret, négation impersonnelle de ce qui confirme ou indique, absence
d'information restent refusés lexicalement avec leur `attendu` d'ambiance. Un acte
accompli et un support concret sont distingués par leur construction grammaticale.
Aucune sélection de sujet, propriété, objet ou scénario ; aucun changement au prompt,
à la chaîne de correction ou au repli.

La livraison initiale (`2d54461`, `4920a9e`) avait indûment transféré les réserves
historiques au seul audit sémantique. Cette révision rétablit **à l'identique**
`tests/test_ambiance.py` de `31e3f9c`, ainsi que ses refus et ses `attendu`. Elle conserve
les admissions de « données » participe, des actes d'un compagnon, du moteur d'un moulin,
d'un scénario envisagé et des unités ordinaires. Les identifiants en snake_case et la
grille numérique restent refusés.

Vérification de la révision : **25 tests ciblés verts** (ambiance, mots courants,
gardes justes, orientation), puis **92 tests verts en 36,28 s** sur les huit fichiers concernés, deux processus
à priorité réduite. Dans la vraie boucle console avec MJ
simulé, la phrase réelle de `soir-appel`, les actes d'un compagnon et les emplois concrets
de preuve sont admis ; les réserves sur une origine ou un son sont corrigées avant
affichage. Après rechargement : narration persistée, objets, joueur, temps, regard et
carte contrôlés. Les cas historiques vérifient aussi l'absence d'enregistrement d'un
texte refusé malgré des métadonnées d'audit altérées. Bruts :
`artifacts/revision-101-cibles.*`, `artifacts/revision-101-reprise.*`.

Vérification initiale conservée : suite complète unique, **1 979 tests, 16 ignorés,
1 976,44 s**, deux échecs sur les formes nominales du moteur corrigés, reprise de
21 tests verte. Pas de nouvelle suite complète ni de nouvelle passe Luna pour cette
révision, conformément à la demande. La passe initiale sur copies reste disponible :
`soir-appel`, 18 appels / 4 tours MJ (4,5) ; `ressources`, 12 / 3 (4), aucun refus,
repli, erreur ou défaut de recharge (`artifacts/luna-101/`). Le cas exact « les planches
ne t'ont pas encore été données » reste prouvé par MJ simulé.

Limite : les relations grammaticales ne prouvent pas tout sens en français. Les
paraphrases et les constructions polysémiques restent en partie sémantiques ; aucune
garantie universelle d'absence de faux refus. Cette limite ne relâche plus les réserves
de preuve historiques, contrôlées de façon déterministe même sans source interne nommée.
