# Lot 105 — composer les seuls effets de route (2026-10-26)

Branche `codex-suites-par-noeud`, **non fusionnée**, base **dcd7b31**,
code signé **0aa644a**.
Aucun changement de décision, relance, scénario, coût ou borne ; aucun Luna.

**Invariant.** `_mesurer` compose les effets de portes du trajet sans écraser
les écritures du successeur. La base recopiait tous ses faits, puis `Etat.apres`
les recopiait encore, même sans changement. Le moteur compose désormais les
seules valeurs différentes et reprend le successeur si rien ne change, sans
mutation en place. Mêmes possessions, faits, ordre des gestes et additions ;
aucune nouvelle lecture du monde, table, clé ou donnée sauvegardée.

Un seul levier mesuré : cette reconstruction. La base partageait déjà les
faits inchangés et mémorisait les trajets par contexte. Normalisation générale,
séquences de plusieurs gestes et règle du planificateur conservées.

**CPU normal, 12 h, graine 1985.** Chaque flèche compare deux exécutions
lancées ensemble ; la branche est répétée dans les deux cohortes.

| Nuit | `42bb9c0` → branche | Rapport | Base → branche | Gain | 8–12 h ancien → branche / base → branche |
|---|---:|---:|---:|---:|---:|
| Auberge fixe | 119,97 → 210,38 s | ×1,75 | 227,64 → 217,42 s | 4,49 % | 96,47→135,09 / 150,16→142,19 s |
| Auberge tirée | 96,42 → 257,25 s | ×2,67 | 280,42 → 260,81 s | 6,99 % | 71,73→216,16 / 237,09→219,34 s |
| Mine fixe | 280,06 → 86,22 s | ×0,31 | 90,41 → 86,88 s | 3,90 % | 245,95→44,94 / 47,20→44,94 s |

**Seuil auberge ×1,5 non atteint**, aux deux départs : ce lot ne suffit pas
à avancer `main`. Variations entre répétitions branche : 3,35 % fixe,
1,38 % tiré, 0,77 % mine ; gains observés, sans preuve statistique.
`comparer --calcul` : trois nuits base/branche identiques, trois répétitions
branche identiques ; douze recharges correctes. Mêmes choix, recherches et
nœuds (356 339 / 635 920 / 187 010).

Génération `_suites`, moyenne CPU de vingt répétitions par version, divisée
par les nœuds de recherche, en µs/nœud : **196,67→177,68 mine 480**,
**209,73→199,24 auberge 480**, **284,13→249,70 auberge 600**.
503/148/1 486 états développés, 2 383/1 067/11 205 successeurs ; six recherches
identiques à la base à chaque répétition. But lumière : zéro ou un état,
temps non interprétable. Horloge CPU Windows quantifiée à 15,625 ms ; moyennes
indicatives, encodage des empreintes exclu. Reproduction :
`comparer_gestes_noeud.py --mesurer --repetitions 20`.

**Contrôles.** Trois tests ciblés verts : composition des effets et priorité
des écritures du destinataire, captures mine/auberge à 480 et auberge à 600
(états, tous les successeurs ordonnés, coûts hexadécimaux et nœuds), puis tour
moteur, monde et rendu après recharge contre la composition de la base.
Deux lancements bloqués par les permissions temporaires Windows ; reprise
hors bac à sable verte, 10,84 s.
Empreintes 2 h, quatre scénarios × quatre graines : **16 identiques**.
Référence dcd7b31 : huit nuits relues du cache, huit manquantes jouées une
seule fois depuis l'archive locale puis rangées dans le cache partagé autorisé.
`VERIFIER` + `spatial.VERIFICATION=1`, auberge 42 tirée, 2 h : aucun écart
ni borne, **1 221 nœuds, 350,44 s CPU**, monde et rendu rechargés corrects.
Suite complète unique : **1 994 tests, 16 ignorés, aucun échec ni erreur**,
212 fichiers, deux processus réduits, **1 806,26 s**. SHA-256 moteur identique
à celui des paires CPU ; aucun défaut restant reproduit.

**Limites.** Poste partagé, priorité réduite, affinité libre, deux calculs au
plus, aucun cache de temps utilisé pour mesurer un gain. Une paire par nuit,
aucune garantie statistique. Fréquence des recherches inchangée. Le créneau
de 45 minutes est dépassé par les vérifications prescrites. Bruts/archives :
`artifacts/suites-105/` ; paires/empreintes : `tools/banc_suites_105.py`.
