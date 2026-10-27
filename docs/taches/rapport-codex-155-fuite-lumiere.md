# Lot 155 — La lumière et l’abri partagent le danger cru de la fuite

Branche `codex-fuite-lumiere`, **non fusionnée**, base `3b284b6` (brief reçu
par avance rapide). Aucun Luna, fichier MJ réservé, agenda ou scénario modifié ;
`main` intacte.

**Invariant.** Un auteur de violence encore actif dans les croyances rend son
lieu cru impropre à un abri ou au terme d’un recours de lumière. `defense.actifs`
partage les critères déjà utilisés par la fuite (récence, clôture, conscience,
reddition et liens crus), sans lire une position distante réelle.
`lieux_dangereux`, `_plan_abri` et `_plan_lumiere` revalident aussi les recours
conservés. Dans `Vue`, cette présence reçoit la pression sociale d’une peur à
100 sur l’échelle existante ; aucun délai ni coût supplémentaire inventé.
Le terminal `eclaire` exclut ce lieu. Les auteurs actifs entrent dans `_entrees`
avec les peurs sociales, même lorsque seule la date fait expirer la violence :
mémoires, graphes repris et certificats sont ainsi invalidés ensemble.

**Preuve réelle.** Nuit native crue 2024 rejouée sur copie jusqu’à 680, capture
sauvée puis rechargée avant diagnostic. La base reproduit exactement les
navettes de Brune entre palier et galerie jusqu’à 715. Sur cette même capture,
**68 → 8 passages entre 680 et 720**, aucune navette après 688 ; Brune rejoint
le refuge. Capture compressée versionnée dans `tests/data/crue-2024-680.json.gz`.
Même `data` complet et rendu après 40 minutes continues ou par minutes avec
recharge. Autre violence au Relais : Ilse, cinq minutes continues ou vingt
quarts de minute rechargés, mêmes état et rendu. Deux victimes éprouvent aussi
la position crue distante et la réouverture effective de l’abri/lumière après
départ connu, neutralisation perçue et expiration ; changement de clé mémoire
et pression vérifiés.

**Mesures.** 37 tests ciblés verts, puis trois nouveaux tests repris verts sur
le code final. **16/16 empreintes 2 h identiques** à la base :
Relais/mine/auberge/crue × 1985/7/42/2024, chronique, mesures et état complet.
Les seize références manquantes ont été calculées une fois et cachées.
Audit natif **12 h crue 2024 : maximum 68 → 15 passages/heure**, aucune alerte
de va-et-vient, plantage, usurpation ou mort. Subsistent deux observations :
Brune longtemps dans l’eau et Ilse affamée en attente ; pas de correction hors lot.
Banc rapide **4 h crue/rixe × quatre graines : 8/8 identiques**, aucun
plantage/usurpation ni nouvelle alerte. Maximum moyen des passages/heure
**13,25 → 13,25** (crue), **6,25 → 6,25** (rixe). Huit références
manquantes cachées une fois. **VERIFIER + spatial 0,2, 2 h crue 2024 :
zéro écart, borne ou plantage**. Suite complète unique : **2 180 tests,
247 fichiers, 1 230,13 s**, deux échecs MiMo historiques `6 != 5`, zéro
erreur/ignoré. Échecs déjà reproduits sur base intacte par les lots 146 b et
152 ; aucune référence relancée pour eux. Deux processus réduits au plus.
Le premier lancement ciblé a été bloqué par les permissions temporaires Windows ;
les exécutions suivantes ont reçu les droits requis. Audit 12 h repris après
le complément de revalidation des destinations conservées : chroniques,
mesures et relevés identiques au premier audit, hors temps de calcul.

**Limites et livraison.** La sûreté dépend des croyances : le départ réel d’un
auteur non perçu ne le déplace pas dans l’esprit. Une traversée du danger reste
possible à son coût commun ; le correctif ne garantit pas toute absence de
boucle entre autres besoins. Les temps de cache ne sont pas comparés.
Bruts : `artifacts/155/`. Aucune clé Git de signature configurée : commit
non signé, branche seule poussée, sans fusion.
