# Lot 324 — G1 A0, oracle de sens

29 octobre 2026 — branche `codex-g1-a0-oracle`, base intégration `884b8d7`,
**non fusionnée**. Aucun fichier de `donjon/` modifié. L'outil
`tools/oracle_g1.py` relit les fils sans jeu ni modèle. Il distingue le
premier et le dernier candidat, l'admission moteur, l'issue exécutée ou
refusée, la confirmation en attente, et le texte effectivement publié avec
la projection rechargée. Un refus antérieur n'efface pas une parole ou une
négociation finalement exécutée.

Les attentes sont versionnées dans `tests/data/oracle_g1.json` : 91 positions,
30 tours MJ, 61 locaux, quinze familles ; six campagnes de six scripts,
36 fichiers scellés par SHA-256 et une preuve complémentaire. Premier gel
`0bb00dc`, avant classement ; relecture des annotations d'issue ensuite
(parole après refus, consultation après reprise, négociation), sans changer
les attentes, seuils ou scores de fidélité. Aucun résultat A1–A6 utilisé.
Les neuf extraits réduits versionnés permettent les tests hors archives.

| Mesure / 30 tours MJ | Réf. 230e7b3 | 294 | 296 | 304 | 311 | c9459ce |
|---|---:|---:|---:|---:|---:|---:|
| Admissions au premier coup | 22 | 18 | 23 | 23 | 21 | 22 |
| Intentions servies fidèles au premier coup, grille 311 | 23 | 14 | 20 | 21 | 20 | 21 |
| Intentions entières fidèles finales, grille 311 | 27 | 18 | 23 | 23 | 23 | 25 |
| Abandons formels | 1 | 3 | 1 | 0 | 3 | 1 |
| Appels | 99 | 98 | 100 | 115 | 104 | 104 |

Les admissions, appels, jetons d'entrée et de préfixe retrouvent le 318 ;
les quinze familles de la référence et du 311 retrouvent exactement le
tableau du 311 (23/27 contre 20/23). Les anciens scores 13/20/20 ne suivaient
pas cette grille : le refus fidèle du coup au 294 et celui du vol au 304
ajoutent chacun un premier coup. Ce ne sont pas des gains nouveaux du jeu.
La référence **c9459ce est une autre passe**, pas la référence chiffrée du
318, qui est **230e7b3**. Elle n'est ni substituée ni moyennée ; elle perd
notamment l'acquisition demandée du pied-de-biche et l'adresse collective
de la question sur le bois.

Les six obligations ont une attente explicite et des prédicats de charge :
prix typé sans négociation, avis/adresse/négation, part contre trois pièces,
question au MJ sans parole, attente puis vol, prise de perche puis saut avec
la même perche. Pour ce dernier cas, `c9459ce/atelier/13`, les étapes sont
présentes mais refusées pour portée ; la perche est absente du porté
rechargé. Il reste **hors des 91**, sans gonfler les scores. Prix affiché via
`propos` n'est jamais crédité comme consultation typée. Les bornes I/V/F/P
du §5 sont publiées sans abaissement ; preuves manquantes marquées `null`.

**Vérification : 15 tests ciblés verts**, dont les faux pendants des six
obligations et des cinq issues ; six campagnes relues, **546 positions
classées, zéro observation inconnue**, sources inchangées. Une première
assertion a révélé l'annotation « refus » d'une parole exécutée après
reprise : annotation rectifiée, assertion conservée. Un seul Python à la
fois, priorité réduite ; aucun calcul long, Luna, banc ni suite complète.

**Portée et limites.** C'est un oracle fermé de non-régression, pas un juge
automatique du français inédit. Une observation modifiée devient
`non_evalue` et produit le code 1 : il faut une annotation humaine justifiée
par l'attente gelée, sans changer cette attente pour accepter la branche.
Le sceau inclut charges, refus, revues, texte et projection rechargée ; il
ne prouve pas une sauvegarde intégrale. Les 61 voies locales sont conservées
et classées comme telles, sans certifier leur réussite. F, les vraies
contre-offres/acceptations, les latences saisie→rendu/confirmation→effet et
les contre-épreuves de tout nouveau refus restent non évalués. A0 ne
valide aucun portage A1–A6 ni l'ensemble des axes I/V/F/P.

Reproduction : `python tools/oracle_g1.py --archives <racine-artifacts>
--sortie <rapport.json>` ; une campagne future fournit les six fichiers par
`--campagne`, sans rejouer la référence. Bruts :
`C:/Users/msics/donjon/artifacts/g1-a0-324/` (`classement.json`,
`verification.json`, `tests.log`, scripts du gel). Aucun calcul actif.
