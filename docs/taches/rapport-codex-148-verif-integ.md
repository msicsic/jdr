# Vérification d’intégration 2d504ae — lot 148

27 octobre 2026. Campagnes moteur sur le PC fixe, code de `donjon/` et `tools/`
identique à `2d504ae`, branche `codex-verif-integ-2d504ae`. Aucun changement du
jeu, Luna ni suite complète. Deux calculs au plus, priorité réduite ; campagnes
en fond. Références `057766f` relues sans rejeu. Temps d’horloge indicatifs,
aucune comparaison CPU.

**49 nuits jouées une fois, 48 achevées** : audit 32 × 12 h, rixes 8 × 8 h,
contrôles renforcés 5 × 8 h, hameau 4 × 12 h. Un arrêt de contrôle ci-dessous ;
aucune autre violation, usurpation ou mort observée. **Cinq coups contre des
personnes**, tous crue 2024 : Aubin → Ilse à 633/686, Gorm → Aubin à 633 puis
deux fois à 686 (deux coups portent). Aucune prise, lien, action d’enfermer,
traîner ou tuer spontanée relevée ; aucun captif attesté, aucune volonté brisée
aux relevés, mais captivité non recensée exhaustivement. Aucun écart de recherche
ou spatial enregistré avant l’arrêt ; crue renforcée non vérifiée au-delà de 0.
Borne historique **Lucien, auberge 42/314** inchangée : retenu = optimum
**73,4743** ; aucune autre borne signalée.

Moyennes par nuit sur les huit graines communes, **057766f → 2d504ae** ;
durées en PNJ·minutes, passages = pire PNJ/heure. `=` reprend la référence.

| Mesure | Relais | Mine | Auberge | Crue |
|---|---:|---:|---:|---:|
| Sans recours | 91,88 = | 30 = | 133,12 = | 150,62 → 178,75 |
| Attente | 454,38 = | 1 431,88 → 1 419,38 | 493,12 = | 582,50 → 511,25 |
| Noir | 233,75 = | 1 461,88 → 1 460 | 951,88 = | 92,50 → 205 |
| Eau | s.o. | s.o. | s.o. | 393,75 → 344,38 |
| Appels | 1,12 = | 7,38 = | 14,50 = | 3,25 → 6,25 |
| Aide | 0,38 → 0,50 | 3 → 2,50 | 2,38 = | 1,88 → 3,25 |
| Bascules | 0,25 = | 0,25 = | 1,38 = | 2 → 3 |
| Passages (pire) | 10 = | 21 = | 32 = | 24 → 68 |
| Échanges | 27,88 = | 120,88 → 120,38 | 140,50 = | 69,50 → 78,88 |
| Propositions / acceptées | 1,62 / 0 = | 9 / 0,25 = | 5,38 / 0,88 = | 4 / 0,50 → 4,38 / 0,25 |
| Offres identiques < 60 min | 0 = | 0 = | 0 = | 0 = |
| Avis exprimés / adoptés | 0 / 0 = | 0 / 0 = | 0 / 0 = | 8,50 / 0,12 → 6,12 / 0,38 |
| Disputes | 0 = | 0 = | 0 = | 0,25 → 0,12 |
| Services rendus | 0 = | 0,88 = | 0 = | 0 = |
| Tâches offertes / acceptées / tenues / rompues | 0,75 / 0 / 0 / 0 = | 1,12 / 0 / 0 / 0 → 1 / 0 / 0 / 0 | 0 / 0 / 0 / 0 = | 0,38 / 0,12 / 0 / 0,12 → 0,12 / 0 / 0 / 0 |
| Constats confiés | 6,38 = | 33 → 33,25 | 49,62 = | 21,38 → 27,12 |
| Avertissements redits | 0,12 = | 1,88 = | 1,38 = | 0,88 → 1 |

**Deux défauts à isoler, aucun correctif ici.** Crue **42, Gorm, minute 0** :
`VERIFIER` arrête le premier pas (« Une méthode candidate a modifié le monde ou
l’esprit »). Reproduction instrumentée : `agendas.planifier` passe
`prevenir_crue` d’actif à sommeil (`contenu non cru`) et écrit une chronique
dans `planification.vues_du_choix`. Invariant : évaluer un candidat ne doit pas
écrire l’état ; séparer évaluation et validation des transitions d’agenda.
La même nuit renforcée `057766f` allait au bout. Crue **2024, Brune, 687–715** :
va-et-vient palier/galerie, 28 « reste dans la lumière », 68 passages dans
l’heure ; relevés 690–715 : `fuir Aubin`, sécurité 100, noir. Absent de la même
nuit `057766f`. Invariant à examiner : l’abri ou la lumière ne doit pas ramener
vers le danger que la fuite vient d’écarter (`defense`, `deliberation`, pression
du planificateur). Cause précise non reproduite sur sauvegarde.

**Agendas et suivi.** En crue, Gorm dort dès 0 sur les huit graines ; agenda
atteint en **1985/144** (Ilse, Brune entend), **500/155** (Brune puis Ilse),
**99/176** (Brune, Ilse entend). Réveils 1985 : 128 puis 144 ; 500 : 149 puis
155 ; 99 : 175. Pas de rafale de réveils observée ; cinq agendas non atteints.
Intermédiaires : **une sollicitation, zéro acceptée/aboutie**, mine **7/472**,
Odon → Rémy pour servir le pain de Lucien, refus `mefiance`. Crue **11/210** :
ancienne promesse de verrouillage acceptée puis rompue non observée ; aucune
promesse acceptée dans la nouvelle nuit. Mine **1985, Odon/253** : correction
maintenue, une pièce de la bourse. Mine **2024, Odon/571–696** : quinze appels
persistants, mêmes minutes ; boucle fautive non établie. Crue **2024** : anciens
avertissements torche 146/242/444 non observés ; nouvelle séquence Brune
121/252/253/560, dont Ilse à 252 et 560, sans preuve générale de correction.

**Hameau**, moyennes : sans recours **212,50**, attente **192,50**, noir
**146,25**, eau **280**, appels **8**, échanges **120,50**, avis **12/0,25**
adopté ; pire passage **32**. Aucun coup contre personne ; zéro intermédiaire.
Gorm 42/25 : dix alternances, dont sept entretien/garde, alerte sans boucle
fautive prouvée ; aucune référence hameau en `057766f`. Le dérivé ne déclare
aucun agenda : diffusion par agenda aux six PNJ non exercée.

**Limites.** Absence de défaut observé ne garantit pas toutes les nuits. Les
archives contiennent des relevés et un état social final, pas une sauvegarde
complète : aucun invariant général de rendu après recharge n’est certifié.
Lanceur hameau externe (choix absent de l’audit), moteur et observateurs inchangés.
32 empreintes des archives principales `057766f` conformes au manifeste 131.
Bruts et analyse : `C:/Users/msics/donjon/artifacts/verif-integ-2d504ae/`.
Aucune clé de signature Git configurée ; commit non signé, branche poussée,
sans fusion ni modification de `main`.
