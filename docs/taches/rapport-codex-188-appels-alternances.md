# Lot 188 — appels et alternances, diagnostic seul

27 octobre 2026, PC fixe, branche `codex-appels-alternances`, base
`integration 31f7a0d`. Aucun code du jeu, scénario ou test modifié ; aucun
Luna. Un seul calcul à la fois, priorité `BelowNormal` vérifiée. Bruts,
sondes et captures exclusivement dans
`C:/Users/msics/donjon/artifacts/appels-188/`.

**Brune : alerte reproduite, pas de répétition sans indice établie.** Crue
1985, départ tiré, joueur passif dans `chambre_cloche`, 12 h : les douze
appels à Gorm reviennent à **495, 495, 497, 497, 498, 498, 499, 499, 500,
500, 518, 518**. Une seule voie : `_inspecter → appeler → heler`, jamais
deux émissions simultanées. Les cinq premiers appels parcourent cinq lieux
distincts ; les sept suivants suivent chacun la réouverture locale par un
nouveau bruit de pas. À chaque appel, Gorm reste cru absent, de position
inconnue depuis 494 ; aucun pas anonyme ne devient sa présence.

Les réouvertures sont datées en dixièmes de seconde : beffroi **298541**,
échoppe **299542 / 299638**, crypte **299848 / 300000**, antichambre
**310934 / 311005**. Les contenus sont des pas d'intensité 3, anonymes,
sur des cases distinctes. Ainsi les deux appels dans la crypte à 499–500
et ceux de l'antichambre à 518 ont bien un indice intermédiaire. Les paires
à la même minute sont séparées de **10 à 35,8 secondes**. Le registre du
lot 69 conserve les échecs jusqu'à cet indice ; ni la date seule, ni un
changement de but ne le remet à zéro. **Invariant respecté dans cette
nuit : un rappel local exige un contenu perceptif nouveau.** Aucun délai
anti-appel ni correctif proposé ; plusieurs pas situés différemment peuvent
légitimement prolonger une recherche infructueuse.

**Gorm : les onze alternances historiques ne sont plus reproduites, mais
leur disparition ne prouve pas une correction.** Hameau 2024, mêmes départ,
durée et salle passive : **quatre** alternances aux relevés de cinq minutes,
dont **une** entretien/garde. Une seconde nuit avec le chemin exact du banc
(`nuit`, récit et relevés) confirme la première mesure. Avant interruption,
les retours à la garde correspondent à des inspections et faits nouveaux :
à **170 / 237 / 269**, le brasero vu vif à **140 / 207 / 239** atteint le
délai commun `REVOIR_FEU = 30` ; à 237 il est ensuite vu faible, alimenté à
238, puis revu vif. Ce ne sont pas des inversions au même état. Le devoir
pressant passe avant la garde de routine ; `INERTIE = 5` et `REPRISE = 15`
ne sont pas des délais entre visites. Le prix de garde vaut **2**, puis
**2,66** à 351 ; dix choix relus sur captures rendent la même intention.
**Aucun agenda déclaré ou réveillé** dans cette nuit.

**Défaut distinct identifié : recherche ordinaire provoquant un départ
définitif.** À **352 min + 54,7 s**, Gorm franchit l'issue de la digue pour
y chercher Aubin, sous le but « entretenir le brasero ». Il devient `parti`
et disparaît des relevés. À **380 min + 39,7 s**, Aubin fait de même en
cherchant Brune pour la prévenir. L'issue et son effet terminal viennent
du **lot 181, `08ab537`**, absents de `ee835d2`. `_chercher` envisage toutes
les salles atteignables ; la projection suppose pouvoir y inspecter après
la marche, alors que `presence.franchir` retire immédiatement le marcheur
de la simulation. L'arrêt des observations explique la perte de l'alerte ;
il ne permet pas d'attribuer chaque écart antérieur au seul lot 181.

**Invariant à corriger dans un lot suivant :** recherche, devis, route,
exécution et sauvegarde doivent partager la conséquence terminale d'un
franchissement ; aucun plan ne doit promettre une inspection ou un retour
après ce départ. Proposition : représenter cette conséquence dans le
contrat commun des transitions et de leur admissibilité, puis exclure une
transition terminale des plans dont le but exige de rester dans le monde.
Risques : retirer aussi une évacuation légitime, ou diverger entre chemins
avec et sans cases ; ne pas simplement interdire la digue ou modifier le
profil des deux PNJ. Aucun correctif livré.

**Preuves et limites.** **153 contrôles** de captures avant appels/choix :
monde complet, description et sons identiques après recharge. Deux reprises
courtes de Gorm et celle d'Aubin conservent aussi départ et rendu après
recharge ; la reprise depuis 351 retrouve exactement les deux instants
ci-dessus. Les captures prises au milieu d'un choix ne garantissent pas
toutes la même cadence de continuation : celle de 352 décale le départ de
Gorm de 15 secondes. Les archives 174 sont absentes du PC fixe ; rapport
et code relus, aucune référence rejouée. Archive 160 hameau 2024 relue :
huit alternances, sur une autre version que la référence 174. Les onze bascules
anciennes ne sont donc pas expliquées individuellement. Aucune garantie
générale sur toutes les boucles ; aucune suite complète pour ce lot
documentaire. Les bruts détaillent aussi les autres alertes, hors périmètre.
