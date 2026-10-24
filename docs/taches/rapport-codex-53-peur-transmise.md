# Lot 53 — La détresse perçue ne rassure plus

Branche `codex-peur-transmise`, non fusionnée, base `5125d06`, brief `e1622bb`.
Correctif `9b8a590`, signature SSH vérifiée.
24 octobre 2026. Aucun appel à Luna, aucune modification de `main`, des scénarios,
de `planification.py` ni des fichiers du MJ.

**Invariant et réglage.** La compagnie exclut le proche dont le PNJ perçoit la
détresse ; cette détresse ajoute une inquiétude pondérée par le lien. Fraction
retenue : **1/2 d'une unité observable par minute**, soit
`0,5 × (confiance + affection) / 100` point de sécurité par minute. On retient
le maximum des proches concernés, comme pour la compagnie ; plusieurs signes du
même proche ne cumulent pas. Les autres compagnons calmes continuent de rassurer.
Ce réglage ne prétend pas mesurer l'intensité privée de la peur de l'allié.

**Fonctions.** `deliberation.autour` lit les signes réellement perçus, les
impressions encore appuyées par un signe présent et les appels reconnus reçus
pendant la minute courante. `ecart_securite` ajoute le taux `securite.detresse`
au temps vécu existant ; `vecu` n'est pas modifié. Deux raccords de perception
étaient nécessaires : `ouie.entendre` retient l'appel reconnu même lorsque son
auteur est visible ; `pnj._avancer_de` marque la fuite après un vrai pas et
`signes` en projette seulement le comportement, sans agresseur ni destination.
L'appel identifié éveille son auditeur, même si celui-ci voit l'appelant ; sans
vue de l'auteur ni voix reconnue, aucun allié ne lui est attribué.
Une intention de fuite avant tout mouvement ne produit aucun signe.

**Vérification.** Les tests `test_peur_transmise` rejouent Brune frappant Aubin,
Ilse voyant ses tremblements, puis un appel de Hugues entendu par Lucien à
l'auberge, visible ou hors du cône. Ils vérifient sécurité croissante, compagnie
retirée, état complet et rendu identiques après recharge pour un même laps
découpé. Autres contrôles : allié calme, signe caché par le dos ou le noir,
pas de fuite réellement exécuté, absence de révélation de sa cible et lien
plus faible, impression faillible perdant son signe et appel anonyme.
Suite complète unique : **1 776 tests, quatre ignorés**, sans échec ni erreur,
173 fichiers, trois processus à priorité réduite, **707,2 s**. Après le dernier
raccord d'éveil/perception : reprises ciblées vertes de l'ouïe, la défense, la
sécurité, les signes et le temps réel ; les **sept tests nouveaux finaux** sont
également rejoués verts (la suite avait chargé leur version initiale à cinq tests).

**Banc rapide.** 20 nuits de 4 h (cinq scénarios × 1985/7/42/2024) contre
`5125d06` : aucun plantage, violation ni usurpation ; mêmes constats d'audit
avant/après (`fige_presse` Relais/rixe 3, mine 1 ; `noir_long` auberge 1 ;
`voir_alterne` crue 3), aucune boucle nouvelle signalée. Référence calculée une
fois, puis ses 20 nuits reprises du cache pour le dernier raccord d'éveil.
Relais/mine/rixe : récits et mesures inchangés ; auberge 1985/42 : appels de
Lucien conservés, sans nouvelle décision. Crue : sécurité plus haute aux
premiers relevés divergents (Ilse 62→63, Gorm 62→65), puis quelques réactions
différentes (2024 : retournements 74→76, allées voir 5→6). Temps non comparables
à la référence en cache ; aucune conclusion de performance.
Bruts : `artifacts/peur-transmise/` dans le worktree.

**Limites.** Les impressions restent faillibles ; le tremblement perçu inquiète
même si sa lecture évoque le froid. Un appel ponctuel agit jusqu'à la prochaine
frontière de minute, pas jusqu'à la fin supposée d'une émotion privée. La règle
ne force ni question à l'allié ni attention vers ce qu'il fuit. Les conditions
sont relues aux événements et aux minutes du temps vécu existant ; aucune
promesse de réaction continue entre ces instants, ni de suppression universelle
des boucles des PNJ.
