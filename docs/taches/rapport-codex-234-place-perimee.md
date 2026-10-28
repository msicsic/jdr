# Lot 234 — placement et rapprochement : un même jugement

Branche `codex-place-perimee`, **non fusionnée ; ciblés et banc validés**.
Merge demandé de `origin/integration` **`d9e5166`** (233/236/238/239/240) dans
**`860fa0b`**, sans rebase, seul conflit documentaire. Moteur propre au 234
inchangé depuis **`5f73166`** ; tests d’Ilse **`89fdfb8`**, Lucien **`ffd814f`**.

**Invariant.** `pnj._jugement_placement` et `_pas_placement` sont communs à
`signes.place` et `_rejoindre_un_proche` : lieu cru localisable, objectif
atteignable, trajet améliorant dans le séjour et la portée du geste, sans
dégradation intermédiaire. Un premier pas à distance arrondie égale est permis.
`_marcher` maintient ce prédicat dans ses détours. Une cible impossible cède ;
une posture seule ne réserve pas le geste. Posture réactualisée sur la position
effective, même après une durée sans déplacement. Aucun champ, mode, prompt
ni exception d’acteur. Un détour exigeant une dégradation temporaire cède au séjour.

**Preuves.** Cinq nouveaux tests / treize sous-cas : Ilse/Relais et Hugues/auberge,
cible inconnue, démentie, paroi, mouvement manqué, détour à distance égale.
Contre-épreuves rouges archivées ; monde/rendu rechargés, laps entiers/découpés.
Après arbitrages :
**46/46 ciblés initiaux verts**, puis **31/31 verts** sur Lucien, 225, placement
et sécurité. Aubin reste à **8 passages/30 min** contre 188 à la première
livraison ; garde livrée, réserve refermée/verrouillée.

**Ilse.** Chronique complète : Aubin jamais localisé, Brune vue au refuge.
Ilse termine **`[6,0]`**, Brune **`[7,1]`**, lumière **niveau 2**, sécurité
**69,685**. Selon l’autorisation conditionnelle, assertion de proximité vers
Brune ; contrôles ajoutés de localisation crue et de lumière. Lignes publiques
de compagnie et apaisement conservés. Preuve `croyances-ilse-d9.json`.

**Lucien : la correction change la nuit historique — vol réussi à la place
de la garde éclairée.** Le recours auparavant bloqué change sa place et
l’information reçue. Le test garde le contrôle 229 à 95 min : témoin toujours
cru, pas de reprise. Toute reprise ultérieure exige une entrée nouvelle qui
lève l’obstacle. À **107–109 min**, avant chacun des gestes exécutés, aucun
témoin cru présent, vu ou à portée d’oreille ; aucun passage par le désespoir.
Le vol est donc légitime selon 225. Ballot posé à l’étable, repris par Anselme,
vu porté par lui, puis localisation perdue. Huit pièces cherchées à 114 ;
contrat de tâche **palier 4** en attente d’information, garde **palier 13**
non prioritaire. Test : **zéro aller-retour injustifié 219**, recherche inchangée
et aucun déplacement de 120 à 165 ; état et rendu rechargés identiques.

**Séparation explicitement autorisée.** La scène dédiée à la lanterne exclut
la pulsion sur le ballot et l’explique : biens pressants, sécurité apaisée,
bougeoir connu. Toutes les assertions de garde, possession, lumière,
changements de lieu et recharge sont conservées. Le scénario historique garde
ses contrôles de témoin, tâche, recherche et absence de navette.
**Suite complète laissée au superviseur**, nouvelle règle **`4422f13`**. Passe arrêtée sur instruction après **1545 tests / 166 fichiers achevés**, zéro échec, une erreur Windows `os.replace` à la sauvegarde initiale du test TUI de coffre vide, avant l’application. Ce seul test, inchangé, repris **vert en 3,602 s** ; cause système non identifiée. Résultats partiels archivés ; cette passe n’a été ni achevée ni relancée.

**Banc final : vingt paires de 4 h contre `d9e5166`.** Quatre références du
cache, seize manquantes rangées une fois ; aucune rejouée. Aucun plantage ni
usurpation. Suspects 219 **2 → 2, épisodes identiques**, aucune hausse par nuit
ni nouvelle alerte. Max passages/PNJ/h Relais/mine/auberge/crue/hameau
**9/10/15/24/22 inchangés**. Cycles **499 → 499**, préemptions **49 → 49**,
à expliquer **66 → 65**, dérives **222 → 218**. Mireille auberge 2024 à 226 :
zéro suspect des deux côtés, mêmes gestes principaux ; Maël hameau 7 : zéro
demande promise des deux côtés. Ces anciens écarts disparaissent après fusion,
sans modifier échanges, propositions ou compteur. Temps non comparés.

AST : seuls `signes.place`, `pnj.agir`, `_marcher`, `_rejoindre_un_proche` et
deux auxiliaires nouveaux diffèrent ; fonctions exclues et MJ intacts.
Aucun Luna, deux travailleurs réduits au plus ; créneau dépassé. Absence
universelle de boucles non garantie. Bruts et scripts :
`C:/Users/msics/donjon/artifacts/place-234/reprise/` (`banc-d9-final*`,
`suite-d9-interrompue.json`, `tui-reprise-d9.txt`, `cibles-lucien-autorisees-d9*`, `lucien-d9-*`,
`causes-d9-mireille-mael*`). Les reprises précédentes restent archivées.
