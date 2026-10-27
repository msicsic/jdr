# Lot 215 — Richesse perdue dans la crue (diagnostic)

27 octobre 2026, `codex-richesse-crue`, départ `3e86d1f` vérifié.
**Aucun jeu modifié, aucun Luna.** Bruts :
`C:/Users/msics/donjon/artifacts/richesse-215/`.

Crue/hameau, graines 1985/7/42/2024, 4 h, joueur passif dans la chambre
de la cloche. Archives `ef86cab`/`aadab7c` réemployées ; moteur archivé
`5a97ab3` identique à `d2243c2`. S/F/D : dix familles et `cats` du lot 183 ;
**texte exact distinct ≠ interaction réussie**. `ef86cab` → intégration inclut
également 207 : tous les écarts ne sont pas attribuables à 205.

| Moyennes par nuit | Avant 205 | Avant 211 | `d2243c2` |
|---|---:|---:|---:|
| S/F/D crue | 23,75/6,75/2,813 | 23/6,75/2,625 | 14/6,75/2 |
| S/F/D hameau | 27,25/6,75/2,333 | 29,5/7,5/2,292 | 31/8/2,542 |
| Attente crue, PNJ·min | 77,5 | 102,5 | 178,75 |
| Attente hameau, PNJ·min | 27,5 | 111,25 | 128,75 |

**Signatures absentes/nouvelles contre avant 211**, dans l'ordre des graines :
crue **0/0, 19/9, 14/5, 22/5**, total **55/19** ; hameau
**25/26, 14/13, 14/15, 18/23**, total **71/77**.
Contre avant 205 : crue **65/26**, hameau **79/94**.
Vingt signatures absentes contre avant 211 subsistent avec une autre issue.
L'inventaire exhaustif `pertes-detail.md/json` donne qui, interlocuteur/objet,
première minute, autre issue éventuelle et contexte actuel, sans fabriquer une
causalité distante. Exemples : Aubin→Gorm, vivres, crue 7 à 3 ; don
Aubin→Brune à 4 ; Brune→Aubin, vente de torche, crue 2024 à 2 ;
promesse de flamme Brune→Aubin, hameau 1985 à 0.

| Perte → cause | Juste ou manque → lot, par priorité |
|---|---|
| Compagnie/contact obtenus par position réelle inconnue ; Ilse/Aubin, crue 7/42/2024, instants 753/1034. Les rencontres, ventes, repas et avis divergent ensuite. | **Perte juste** : ne réintroduire aucun savoir caché ; restaurer tous les textes serait un mauvais objectif. Captures `historique-211-*.json`. |
| `_plan_abri.sures` et `s_enquerir` exigent une personne localisée. Ilse attend au beffroi ; `rejoindre(Aubin)` propose pourtant inspection/appel, non choisi. Même lacune de raccord pour l'enquête de ressource, contrairement aux demandes de biens. | **P1 : contact nécessaire → recherche/appel commun**, avec coûts, dangers et indices 37/69 inchangés. Captures `crue-7-attente-ilse-10`, `crue_hameau-42-attente-brune-160`, `crue_hameau-7-attente-aubin-200` (`.json`). Routes parfois bloquées : aucun succès garanti. |
| « Où est X ? » n'est pas un recours autonome existant ; l'enquête exclut les personnages. `rejoindre` utilise le lieu cru ; sans lieu, `_chercher` inspecte les lieux les moins récemment visités. | **P2 : renseignement de localisation auprès d'un tiers**, croyance sourcée, jamais vérité cachée. Même capture Aubin/hameau 7 ; gain non mesuré, témoin informé à établir. Aucun délai ne réarme les recherches. |
| Gorm, crue 7 à 80 : brasero inaccessible par péril d'eau. Plans retrouvés seulement pour cloche **déléguée** ou rondes **satisfaites** ; hameau 1985 à 130, crypte aussi inaccessible. | **Perte juste**, aucun recours omis démontré. Captures `crue-7-attente-marchand-80`, `crue_hameau-1985-attente-marchand-130`. Ne pas changer d'objectif par exception ; alternances d'agenda à 196 c. |
| Refus sociaux, feu sans moyen, réserve inaccessible. Ilse/crue 2024 à 200 connaît les interlocuteurs mais n'a pas de chemin vers les vivres. | **Conserver ces contraintes** ; appeler ne crée ni permission, ni combustible, ni passage sûr. Capture `crue-2024-attente-ilse-200.json`. |

**Attentes actuelles cumulées sur quatre graines** : crue, Gorm/devoir **335**,
Brune/chaleur **255**, Ilse/sécurité **80**, Ilse/faim **45** ; hameau,
Gorm/devoir **285**, devoir+biens **45**, Brune/chaleur **140**, Aubin/chaleur
**45** PNJ·min. `recours.json` détaille croyances, refus et pulsions éligibles
pour les 22 situations capturées ; `attentes.json` conserve tous les relevés.

**Validation/limites.** Huit rejeux séquentiels à priorité réduite : chroniques,
mesures et états finaux identiques, zéro plantage. **36 captures** rechargées,
monde/`regarder`/scène identiques : 22 attentes, huit départs, six historiques.
Pas de suite complète, diagnostic sans code modifié. Attente échantillonnée et
pondérée par cinq minutes ; contexte d'une signature ≠ preuve causale complète.
Les sondes initiales précèdent la perception. Aucun gain futur ni garantie
contre les boucles revendiqué.
