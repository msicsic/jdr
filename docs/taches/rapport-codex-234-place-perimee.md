# Lot 234 — placement et rapprochement : un même juge

Branche `codex-place-perimee`, **non fusionnée ; validation non acquise**.
Merge demandé de `origin/integration` **`1c44801`** (229/232) dans `3f8739e`,
seul conflit documentaire. Code final **`5f73166`**, après `c6cc8fa` et `34825a8`.
La référence reste ce commit fusionné, sans suivre les intégrations suivantes.

**Invariant.** `pnj._jugement_placement` et `_pas_placement` servent à
`signes.place` et `_rejoindre_un_proche` : lieu cru localisable, objectif
atteignable, trajet améliorant dans le séjour et la portée du geste, sans
dégrader le placement obtenu. La progression porte sur le trajet : son premier
pas peut conserver la distance arrondie. `_marcher` maintient ce prédicat dans
ses détours. Une cible impossible cède ; le contact fiable accomplit le recours.
Une posture seule ne réserve jamais le geste ; elle est réactualisée sur la
position effective, même après une durée consommée sans déplacement. Aucun
nouveau champ de sauvegarde, mode, prompt ni exception d'acteur.

**Preuves ciblées.** Cinq nouveaux tests / treize sous-cas : Ilse/Relais et
Hugues/auberge, cible inconnue, démentie, inaccessible, mouvement manqué et
détour à distance égale. Douze sous-cas rouges sur les fonctions exactes de
`1c44801` ; le détour est rouge sur `34825a8`, puis vert. Monde et rendu après
recharge, laps entiers/découpés contrôlés. Les cinq fichiers initiaux donnent
**44 tests verts** ; consolidation étendue : **64/65 verts**, zéro erreur.

Les **trois régressions demandées passent sans changer leurs assertions** :
Aubin **188 → 8 passages / 30 min**, même monde/vue en laps découpés ; garde :
une part livrée, réserve refermée/verrouillée après recharge ; Ilse rejoint
Aubin. Chronique finale : Aubin non localisé au départ, vu à **t525** lorsque
Ilse est `[2,1]` ; positions finales **Ilse `[0,4]`, Aubin `[1,5]`**, fanal
perçu niveau **1**, sécurité **69,707**. Aucun assouplissement de l'oracle.

**Suite complète unique sur `34825a8` : 2 530 tests / 293 fichiers,
3 610,030 s, trois échecs, zéro erreur, seize ignorés.** Rejoués avec les
fonctions de `1c44801` : Gorm et Lucien passent, seule la torche échoue.
Le détour corrige ensuite Gorm, confirmé dans la consolidation sur `5f73166`.
**Lucien reste rouge** (`test_dynamique_besoins`, retour de lanterne au grenier).
Première divergence physique à **t45591** : ancienne posture vers Odile sans
pas ; le recours restauré avance de `[2,2]` à `[3,2]` vers Odile crue présente
et fiable. À 107 min il quitte ensuite la salle commune ; il termine chambre
chaude, but sur le ballot, plan vide, bougeoir chez Mireille. La cause de ce
blocage ultérieur n'est pas certifiée. Aucune modification de l'assertion ou
des modules exclus pour l'effacer. Torche **3188/3615** préexistante, lot 238.
Pas de seconde suite complète après correction ; consolidation ciblée explicite.

**Banc final sur `5f73166` : vingt paires de 4 h, vingt références du cache**,
zéro plantage/usurpation. Suspects 219 **2 → 3** : hausse Mireille auberge 2024
à 226 min (`manque:servir`, puis retour au service de Mathurine), cause non
certifiée ; paquet causal archivé. Max passages/PNJ/h Relais/mine/auberge/crue/
hameau : **9/11/17/62/22 → 9/10/17/62/28** (Gorm 2024, heure 3 : 28).
Cycles **507 → 510**, préemptions **58 → 43**, à expliquer **87 → 74**,
dérives **204 → 203**. Nouvelle alerte Maël hameau 7 : huit demandes promises ;
alternance Lucien auberge 42 : observation, pas preuve de boucle. Les passes
intermédiaires sont conservées ; aucune référence rejouée. Temps non comparés.

Périmètre confirmé par AST : `signes.place`, `pnj.agir`, `_marcher`,
`_rejoindre_un_proche` et les deux nouveaux auxiliaires. `ouie`, `echanges.tenu`,
`pnj_propositions`, `biens.services_proteges`, `menager_flamme`, `social` et MJ
intacts. Aucun Luna, deux travailleurs réduits au plus ; créneau dépassé.
Les trajets exigeant une dégradation temporaire cèdent au séjour. Absence
générale de nouvelles boucles **non garantie**. Bruts et scripts :
`C:/Users/msics/donjon/artifacts/place-234/reprise/` (`banc-plateau*`,
`suite-finale*`, `consolidation-plateau*`, `lucien-*`, `croyances-ilse-plateau*`).
