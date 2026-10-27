# Lot 220 — Ne pas redemander un emprunt rendu sans entrée nouvelle

Branche `codex-bourse-redemandee`, **non fusionnée**, base `fb2dd65` vérifiée.
Aucun Luna, aucun fichier interdit modifié. Calculs à priorité réduite,
deux travailleurs au plus. Bruts exclusivement
`C:/Users/msics/donjon/artifacts/bourse-220/` ; aucune clé de signature Git configurée.

**Diagnostic.** Sur `4d4c625`, captures rechargeables à 285 et 287, première demande de
Mathe à 288 ; demandes et restitutions répétées dès 289. Une seconde capture
à 290 conserve la boucle engagée. L'acquisition par demande suffit au but
`argent`, mais crée une obligation de rendre ; l'objet ne sert plus au plan,
est rendu, puis redevient candidat. Le succès efface les refus, aucune mémoire
durable de cet essai terminé ne filtre le prêt suivant. Le compteur 199 ne
couvre pas ces changements de moyens sous un même but. Sur la base actuelle,
rejeu initial 285→320 : Odon prend la bourse à 287 et refuse la réclamation
de Bram ; la boucle historique ne naît plus sur ce trajet. Cela ne prouve
pas l'invariant ; son introduction et le lot qui a changé cette trajectoire
ne sont pas datés par ce diagnostic.

**Contrat commun.** `biens.clore` ferme la permission, constate la possession
pour les participants et retient les entrées du prêt rendu. `echanges.remettre`
couvre aussi un retour au propriétaire sans permission ; un don ou une vente
ne devient pas une restitution. La mémoire durable est sauvegardée et validée
par `biens.verifier`. `planification.Vue.refuse` et `echanges.demander` consultent
le même prédicat ; le cache du graphe inclut ce jugement. Ni le temps, ni la
réobservation, ni le bénéfice social de la restitution ne relancent l'essai.
Un nouvel épisode de besoin, un moyen porté ou des fonds nouveaux, davantage
de pièces crues, une nouvelle propriété ou un prix devenu accessible changent
les entrées ; l'achat garde son contrat distinct. Aucune constante modifiée.

**Vérifications.** Ciblés : **35 tests distincts verts**, dont cinq nouveaux
également verts dans la suite complète (6,393 s).
Capture historique 290→305 : restitution à 290, aucune nouvelle demande de
Mathe/Rémy, bourse chez Rémy et propriétaire Rémy ; temps réel en bloc ou
découpé, monde et rendu rechargés identiques. Lampes au Relais et à l'auberge,
retour volontaire/imposé, joueur emprunteur, nouveau besoin ou fonds, achat
et don couverts. **Vingt paires 4 h**, cinq scénarios × quatre graines :
**20/20 chroniques et audits identiques, 19/20 empreintes finales identiques**.
Hameau 7 rejoué une fois : seule la mémoire du retour de la torche de Brune
à Sève diffère ; sans ce nouveau champ, empreinte exactement égale à la
référence. Zéro plantage/usurpation, aucune nouvelle boucle mesurée.
Échanges **712→712**, demandes **147→147**, répétitions textuelles **18→18**
(ce compteur brut inclut des répétitions légitimes). Compteur 199 inchangé :
**16 suspects / 144 à expliquer / 494 cycles accomplis**. Référence exacte
absente du cache : vingt nuits calculées une fois et rangées ; temps du cache
non comparés. S/F/D du lot 183, fonction `cats` exacte, PNJ inactifs inclus,
avant = après, moyennes sur 4 h :

| Relais | Mine | Auberge | Crue | Hameau |
| --- | --- | --- | --- | --- |
| 11,25 / 3,75 / 1,5 | 22 / 4,25 / 1,607 | 12 / 4,25 / 1,063 | 14 / 6,75 / 2 | 31 / 8 / 2,542 |

Mine 1985 **12 h**, branche : **138 échanges, 47 demandes, neuf répétitions
textuelles**, zéro demande de bourse par Mathe/Rémy, zéro plantage/usurpation,
199 **0 / 21 / 63**, trois observations `fige_presse` et cinq `noir_long`.
Pas d'attribution de l'écart à l'ancienne archive 212
au seul lot 220 : la trajectoire actuelle a déjà changé avant le correctif.
**Suite complète unique : 2 437 tests / 283 fichiers, 1 980,589 s**, deux
échecs, zéro erreur. Les deux assertions MiMo `6 != 5` sont reproduites
sur la copie exacte de `fb2dd65` (deux méthodes, 1,529 s) ; aucun autre échec,
aucune seconde suite. Dernière lecture : admission du prix nul dans le nouveau
schéma de sauvegarde ; cinq ciblés repassés verts après cette seule borne,
sans changement des décisions mesurées. Vérification au-delà du créneau.

**Limites.** La mémoire nouvelle ne reconstitue pas les restitutions d'avant
son installation ; une ancienne partie apprend au prochain retour. Le test
historique exerce donc une restitution réelle, et non un marquage manuel de
la sauvegarde. Ce lot ne certifie pas l'absence de toutes les boucles du jeu
ni la détection exhaustive par 199 ; les changements d'état retenus sont ceux
du contrat d'emprunt décrit ci-dessus.
