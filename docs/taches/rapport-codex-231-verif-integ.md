# Vérification d’intégration 4306c14 — lot 231

28 octobre 2026, PC fixe, branche `codex-verif-integ-4306c14` depuis
`cee90ea` ; diff `donjon/ tools/` vide contre `4306c14`, avant et après.
Jeu inchangé, aucun pull, Luna, suite complète ni rejeu de référence.
Un seul travailleur de calcul, en fond, priorité réduite vérifiée.
Référence : les 49 archives du lot 212, relues exclusivement.

**49 nuits lancées une fois, 47 achevées, deux plantages : intégration non verte.**
32 audits × 12 h, huit rixes × 8 h, cinq contrôles × 8 h (`VERIFIER`, spatial
0,2), quatre hameaux × 12 h. **Pureté des candidats violée** : mine 42 à
415 min et rixe 42 à 350 min, assertion de `planification.vues_du_choix`
« Une méthode candidate a modifié le monde ou l’esprit ». Les deux mêmes
contrôles étaient achevés sur `4d4c625`. Petit lot : garantir une évaluation
sans écriture avant l’arbitrage ; auteur et champ modifié restent à isoler.
**Auberge 42, Lucien à 435 : 75 bornes**, contre zéro : 73
`ancienne_borne` avec résultat égal au recalcul complet ; deux recherches
`garder:grenier` sans réponse malgré des optimums 126,36 et 127,29.
Limite de recherche à instruire, distincte d’une restriction incorrecte.
Zéro autre écart VERIFIER/spatial consigné ; deux contrôles interrompus.

Moyennes **4d4c625 → 4306c14**, huit nuits/scénario, quatre au hameau,
12 h ; durées en PNJ·min, passages = maximum PNJ/heure. Tâches = promesses
offertes/acceptées/tenues/rompues ; S/F/D = signatures/familles/diversité moyenne.

| Mesure | Relais | Mine | Auberge | Crue | Hameau |
|---|---:|---:|---:|---:|---:|
| Sans recours | 15,62 → 2,50 | 3,12 → 58,12 | 137,50 → 4,38 | 49,38 → 0 | 0 → 10 |
| Attente | 471,88 → 470,62 | 1 071,88 → 1 321,25 | 416,88 → 430 | 905 → 1 162,50 | 1 021,25 → 1 761,25 |
| Noir | 292,50 → 296,88 | 1 021,88 → 891,25 | 726,25 → 818,75 | 359,38 → 61,25 | 575 → 270 |
| Eau | — | — | — | 64,38 → 96,25 | 33,75 → 6,25 |
| Appels/aide | 1,88/0 → 1,62/0,25 | 5,38/1,38 → 17,50/1,62 | 21,88/2 → 21/2,75 | 5,75/2 → 3,38/1,38 | 4,75/1,25 → 5,75/2,25 |
| Bascules/passages | 0/10 → 0,12/11 | 0,25/19 → 0,25/24 | 0,50/52 → 0,62/246 | 1,25/43 → 0,62/28 | 0,50/39 → 0/22 |
| Échanges | 48,62 → 52,88 | 187,88 → 158,62 | 173,12 → 188 | 89,12 → 68,12 | 173,50 → 158 |
| Propositions/acceptées | 9,12/2,50 → 8,38/3,38 | 14,75/0,75 → 14,12/0,50 | 10/0,62 → 10,25/0,50 | 11,25/2,12 → 9,75/1,75 | 20/4,25 → 19,25/4,50 |
| Offres identiques < 60 min | 0 → 0 | 0,25 → 0,25 | 0,12 → 0 | 0,25 → 0,12 | 0,25 → 0,25 |
| Avis/adoptés | 0/0 → 0/0 | 0/0 → 0/0 | 0/0 → 0/0 | 1,25/0,62 → 0,88/0 | 3,50/1,50 → 1,75/0 |
| Disputes/services constatés | 0/1,75 → 0/1,12 | 0/3,12 → 0/2,88 | 0/3,62 → 0/2,88 | 0/2,25 → 0,38/1,88 | 0,50/3,75 → 0,75/4,25 |
| Tâches | 1,25/0,62/0,62/0 → 1,50/1/1/0 | 0,88/0/0/0 → idem | 0,38/0/0/0 → 0/0/0/0 | 0,88/0,25/0,25/0 → 1/0,25/0,25/0 | 1,50/0,75/0,75/0 → 3,50/1/1/0 |
| Constats/avertissements redits | 12,12/0,25 → 10,12/0,50 | 36,25/1,12 → 37,25/1,38 | 52/3 → 47/2,25 | 31,75/0,50 → 19,25/0,25 | 68,50/2,25 → 21/1,50 |
| S/F/D | 28,62/5,88/3,28 → 31/5,88/2,97 | 73,62/6,88/3,21 → 99,75/6,75/3,43 | 80,75/6,38/3,06 → 109,62/6,12/3,08 | 40,50/7,88/4,06 → 35,62/7,12/3,59 | 73/8,50/3,96 → 80,25/9/3,88 |
| 219 suspects/à expliquer (sommes actuelles) | 3/27 | 4/90 | 6/105 | 0/85 | 15/53 |
| 227 physique/départ cru (sommes actuelles) | 8/0 | 0/0 | 1/0 | 0/1 | 4/0 |

**Compteurs.** Référence 199 : suspects 13/13/67/126/96 ; classes 219 et
causes 227 non mesurées, comparaison directe impossible. Sur les 47 nuits
achevées : **31 suspects 219, 390 à expliquer ; 23 pertes payées : 22
physiques, une après départ cru, zéro geste fautif, zéro tiers, zéro cause
inconnue**. Zéro usurpation, coup ou mort relevé ; aucun captif/volonté brisée
attesté. Quatre `ecarts` de pas laissés à autrui, comme 212.

**Suivis et petits lots, sans correctif.** Mine 1985 : demandes de bourse
Mathe/Rémy **228 → 0** sur la chronique entière ; renoncements moyens mine
**1,75 → 0,25**. Crue 2024 : **16 coups/sept touchés → zéro** ; Gorm a
**5 → 12** mises en sommeil, puis atteint l’évacuation à 365 (avant : 243).
Hameau 42 : onze questions « où », une seule Gorm→Maël sur Aubin (115),
pas de rafale historique de ce trio. Anselme auberge 2024 : alternance
poêle/garde après 330 non retrouvée sous sa forme 212.

Alertes nouvelles dans les mêmes nuits de référence : **Anselme, auberge 7,
420–479 : 246 passages**, dont 68 couloir et 68 salle commune ; à 430–431,
navettes sous le même but de garde (le maximum ancien d’Anselme était 22/h).
Petit lot : cohérence entre but durable, trajet et progression réelle,
non couverte par le seul retour entre buts 219. **Gorm, hameau 1985,
541–545 : onze retours chaleur/devoir** ; l’ancien même but chaleur existe
à 552–606, sans cette rafale. **Maël, hameau 42, 419–451 : quatre suspects**
entre restitution de torche et inspection ; ces buts/retours sont absents
de la même nuit ancienne. Petits lots sur la stabilité commune des recours
et engagements ; causes exactes non certifiées. Les autres suspects et
leurs correspondances anciennes sont archivés, sans assimilation à des bugs.

Rendez-vous 230 : **28 → 39 départs dans la minute d’un « Ici, viens ! »**, sans
retrouvaille ni fin d’attente textuelle préalable ; auberge **12 → 12**, aucun
de Mireille. Ce sont des occurrences candidates : urgence, échéance et
identité du partenaire ne sont pas certifiées par ce comptage. Deux archives
actuelles interrompues sans chronique complète sont exclues.

**Limites et preuves.** Aucune garantie générale des boucles, de la captivité
ni du monde/rendu après rechargement : archives sans monde complet. Les
deux plantages excluent leurs mesures finales et leurs avis. Temps non
comparés. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/verif-integ-4306c14/` : lanceur, journaux,
49 archives, `analyse/manifest.json`, mesures et `complement231.json`
(cas et correspondances avec 212). Aucune clé de signature Git configurée.
