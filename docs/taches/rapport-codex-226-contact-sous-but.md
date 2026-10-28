# Lot 226 — Contact nécessaire sous le but parent

28 octobre 2026 — `codex-contact-sous-but`, **non fusionnée**. `e5afca8` vérifié ;
reprise demandée sur `881db69` (225), avance rapide jusqu'à `b8e433d` (documentation
seule ensuite), conflit documentaire seulement. Aucun Luna ; deux travailleurs
réduits au plus ; aucune clé de signature configurée. Bruts :
`C:/Users/msics/donjon/artifacts/contact-226/`.

**Invariant.** `_plan_abri` et `s_enquerir` n'écartent plus un contact nécessaire
parce que son lieu est inconnu. Le raccord `contacter` reprend `rejoindre` :
inspection/appel/question 221, coûts, dangers, refus et indices 37/69 communs.
Le parent abri/enquête conserve les moyens ; la coupure interdit toute demande
ou installation supposant le contact réussi. L'abri encore inconnu porte
`lieu: null`. Besoin, confiance et moyens sont réévalués ; l'évacuation prime.
**AST contre 881 : seules ces deux fonctions et le raccord changent en production.**

**Cas réels 215.** Les trois attentes sont reproduites avant correction
(`avant.json`). Ilse/crue 7 min 10 inspecte puis appelle Aubin ; Brune/hameau 42
min 160 cherche Ilse pour son enquête de chaleur. Aubin/hameau 7 min 200 reste
justement sans recours : les ressources sont déjà connues, une nouvelle enquête
ne lève pas leurs obstacles. Autre cas autonome : Hugues à l'auberge.

**20 paires finales de 4 h contre `881db69`**, cinq scénarios × quatre graines ;
vingt références manquantes complétées une fois puis cachées. Première mesure sur
`346c1aa` archivée séparément. Zéro plantage/usurpation. Classes 219 : suspects
**4 → 2**, deux restants identiques ; cycles **523 → 521**, préemptions **67 → 87**,
à expliquer **59 → 85**, autrui **1 → 1**. Appels **5 → 11**, dont crue **0 → 6**.
Attente moyenne PNJ·min ; S/F/D moyens du lot 183 :

| Scénario | Attente avant → après | Suspects | S/F/D avant → après |
|---|---:|---:|---|
| Relais | 0 → 0 | 0 → 0 | 11,5/4,25/1,625 identiques |
| Mine | 0 → 0 | 0 → 0 | 23/4,25/1,75 identiques |
| Auberge | 0 → 0 | 2 → 2 | 11,5/4,5/1,094 identiques |
| Crue | 218,75 → 108,75 | 2 → 0 | 16,5/7,25/2,438 → 24,5/7/3 |
| Hameau | 92,5 → 76,25 | 0 → 0 | 40,5/8,5/2,667 → 40,5/8,75/2,708 |

**Validation.** Huit nouveaux tests : monde/rendu/scène rechargés, laps découpés,
parent apaisé/démenti et refus. **35 ciblés verts après 225**. Seule suite complète
achevée : **2 494 tests / 289 fichiers, 2 558,203 s, 15 échecs bruts, zéro erreur**.
Cinq sont reproduits sur `881db69` : voix inconnues du joueur, compteur de service,
lanterne de Lucien et deux MiMo. Dix écarts propres au lot résolus en reprises :
prémisses explicites, demande effectivement formulée, rendez-vous visé et constat
réel. Captures d'Odon/Josse et Anselme/Lucien : nouveaux plans/monde/journal,
**empreintes des deux vues historiques inchangées**, recharges intégrales gardées.
**17 ciblés finaux + deux reprises verts ; cinq préexistants restent, suite non verte.**
Première passe interrompue sur demande d'intégration (10 fichiers/100 tests verts),
pas de seconde suite achevée ; moteur inchangé depuis le banc. Créneau dépassé.

**Limites.** Aucune rencontre garantie ; le récit de banc affiche `None` pour
l'abri non localisé. **Absence de toute boucle nouvelle non certifiée** : huit
sommeils de l'agenda de Gorm en crue 2024 (1–181 min), reprises annoncées sur
croyance nouvelle, causalité non isolée. Dérives **200 → 241**, états payés perdus
sans durée spécifiée **8 → 9** : Brune quitte Aubin puis éteint la torche à 7 min,
limite de présence du 224, sans violation de durée établie. Baisse d'attente et
non-hausse des suspects validées ; ces autres familles restent hors périmètre.
