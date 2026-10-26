# Lot 129 — calibration des signes, critère révisé

Branche `codex-signes-critere`, non fusionnée, base `56afc2e` (integration).
**Critère non atteint.** Décision du 2026-10-26 appliquée au plan : justesse
≤ 0,7 à PSY ≤ 9, ≥ 0,8 à PSY ≥ 13, méprises strictement < 20 % des lectures.

**Invariant.** `signes.lire`/`interpreter` gardent le dé, la règle et le contrat de
perception/sauvegarde ; seules les constantes communes passent à **3/2/7**
(pénombre/dissimulation/bande sans conclusion). Aucun réglage par personne, sorte
ou scénario ; aucun autre module moteur modifié. L'outil ajoute `--heures`, le
contrôle de durée à la reprise, `classer` et un plafond de deux processus.

**Mesure.** Sans Luna, 48 nuits de **4 h** : quatre scénarios × graines
1985/7/42/2024 par défaut ; Gorm/Relais et Hugues/auberge à PSY 8/11/14/16
par le réglage commun de `banc_pnj --regler`. Grille conditionnelle **112** réglages
(pénombre et dissimulation 2–5, bande 5–11, 63 historiques inclus) : **aucun admissible**.
Classement : abstention minimale parmi les admissibles ; sinon dépassement maximal,
somme, puis abstention. Méprises globales sur défaut + lecteurs réglés,
justesse par tranche sur ces derniers.
Le minimax retient 3/2/7 : basse 0,75 (+0,05), haute 1,00, méprises globales
26,58 % (+6,58 points), abstention combinée 36,18 %.

**Confirmation indépendante des décisions figées :** 48 nouvelles nuits libres de 4 h.
Justesse = justes / lectures retenues ; abstention = sans conclusion / essais.

| Population | 4/3/8 : justes / lectures | 3/2/7 : justes / lectures | Abstention avant → après |
|---|---:|---:|---:|
| Défaut (PSY 10–12) | 470/612 = 0,768 | 491/675 = 0,727 | 40,12 → 35,96 % |
| Réglée PSY 8 | 9/11 = 0,818 | 9/12 = 0,750 | 52,17 → 47,83 % |
| Réglée PSY 11 | 9/9 = 1,000 | 9/10 = 0,900 | 60,87 → 56,52 % |
| Réglée PSY 14–16 | 26/26 = 1,000 | 26/26 = 1,000 | 43,48 → 43,48 % |

Méprises globales (deux populations) **144/658 = 21,88 % → 188/723 = 26,00 %** ;
abstention globale 40,93 → 36,91 %. Par défaut **142/612 = 23,20 % → 184/675 = 27,26 %** ; lecteurs réglés
**2/46 = 4,35 % → 4/48 = 8,33 %**. Le compromis manque la borne basse de **0,05**
et la borne globale de **6,00 points** (7,26 points sur défaut seul) ; il réduit l'abstention au prix
de méprises supplémentaires. Aucun succès général revendiqué : petites tranches
(23 essais bas, 46 hauts), grille conditionnelle, nuits de 4 h et non de 8 h.
Le bilan détaillé par sorte et par lecteur reste dans les bruts.

**Tests ciblés : 39 verts**, 10,17 s ; guet réel Relais 7 à 441 min et autre guet
à l'auberge, état/rendu rechargés. Seuls dés contrôlés adaptés : 13→12 (dissimulation
−1), 16→14 sur la capture (pénombre et dissimulation −1 chacune) ; mêmes PSY 14
réussies/PSY 8 abstentions. Quatre tests de classement : dénominateurs, bornes,
abstention, compromis, absence d'échantillon.

**Banc rapide** : 4 h × quatre scénarios × quatre graines contre `56afc2e`.
Les 16 références de 4 h manquaient (seules les empreintes de 2 h existaient) :
calculées une fois puis cachées, avant les 16 nuits de branche. Mesures des signes
identiques aux nuits par défaut ci-dessus ; zéro plantage/usurpation de chaque côté.
**Absence de répétition nouvelle non acquise** : mine 2024, Mathe lit huit fois
« peur » contre six, deux retours supplémentaires après méprise « froid » (104→117
et 197→207 min, marge −8 auparavant sans conclusion). Nouvelle alerte `repetition`,
avertissements redits totaux 5→8, alternances aller voir/autre but 1→2 (crue 7 ajoutée).
Aucune boucle au même bruit prouvée ; ni alerte masquée ni règle spéciale ajoutée.

Suite complète unique : **2 075 tests, deux échecs MiMo `6 != 5`, zéro erreur**,
  **995,11 s** ; les deux échecs reproduits seuls sur la base intacte `56afc2e`
  (2 tests, 1,34 s). Quatre tests finaux de classement verts (0,17 s).

Bruts : `artifacts/signes-129/` (`corpus-4-3-8.json`, `grille.json`, `classement.json`,
`confirmation-3-2-7.json`, `bilans.json`, tests et comparaison). Toutes les commandes
Python utilisent `C:\Users\msics\donjon\.venv\Scripts\python.exe`, deux processus
réduits au plus, bancs successifs, sans Luna ni sauvegarde de partie.
Aucune clé Git de signature configurée sur ce poste : commit non signé.
