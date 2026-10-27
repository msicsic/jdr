# Lot 182 — attente et noir du hameau : diagnostic

27 octobre 2026, laptop, `codex-attente-hameau`, base `1598b57`.
**Aucun code modifié, aucun Luna.** Neuf nuits historiques de 12 h, deux
calculs réduits au plus ; aucun temps comparé. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/attente-182/` (`synthese.json`).

**Deux marches établies.** Attente / noir / eau, en PNJ·minutes :

| Commit, jalon | Hameau 42 | Hameau 7 |
|---|---:|---:|
| `7adc788`, référence | 0 / 100 / 105 | 15 / 95 / 405 |
| `50def29`, 146 e | 0 / 100 / 105 | 15 / 95 / 405 |
| `e036279`, 163 | 1 435 / 80 / 10 | 495 / 580 / 40 |
| `6d87361`, 167 | — | 720 / 715 / 25 |
| `ee835d2`, 167 c | 1 435 / 80 / 10 | 720 / 715 / 25 |

146 e : chroniques/relevés/mesures identiques à la référence. En 42,
163 et 167 c : chroniques/relevés identiques, deux compteurs de rumeurs
seulement diffèrent. En 7, 167 et 167 c : chroniques/relevés identiques.
Archives 174 reproduites : chroniques/relevés identiques, toutes les mesures
identiques en 7. Ces deux nuits expliquent **2 140/2 230 (96 %)** de la hausse
d’attente ; 7 porte **+620** de noir, contre **+490** nets sur quatre graines.

**42 : prévisions anciennes et isolement.** Sève/Ilse/Aubin attendent la
faim dans la chambre de la cloche : **380/305/275 min** échantillonnées,
entrées exactes **343**, **418 + 45,8 s**, **449 + 6,6 s**. Maël : sécurité
dès **448**, puis chaleur au relevé 540, **275 min** dans l’antichambre.
Gorm : devoir/biens/chaleur **190 min** ; Sève : sécurité 10. Aucun répit ni
attente bornée dans les quatre captures. À 345, Sève connaît la réserve
crue verrouillée, ignore Gorm depuis 283 ; Aubin/Ilse ont répondu « rien »
à 342. Il reste **cinq parts réelles**. Sa pente **+20 cm/h** de 117 rend
l’échoppe attendue à **110 cm**, route alimentaire interdite. À 420, Ilse
voit Gorm mais conserve **+24 cm/h** de 179 ; Maël conserve **+21 cm/h** de
181 malgré l’échoppe revue sèche à 450.

Sur copies froides : faim Sève/Ilse **épuisée en 168/128 nœuds**, sans
plafond ; abri de Maël introuvable. Neutraliser les pentes rend ces trois
recours possibles (`sensibilite-pentes.json`) : **pas un correctif**.
`eau.observer` enregistre le sec sans niveau ; `eau.estimation` /
`esprits.prevision_propre` retiennent les anciennes mesures positives,
appliquées par `eau.attendue`, `Vue.descente` et les routes. 163 éloigne les
PNJ des lieux où ils remesureraient la décrue. L’attente respecte leurs
croyances ; invariant défaillant : **une observation sèche récente doit
contraindre une extrapolation incompatible au présent**, sans inventer de
pente nulle ni lire l’eau cachée. Petit lot proposé : cette borne dans le
contrat observation/prévision/routes/clé de recherche/sauvegarde ; vérifier
Sève et Maël après recharge. Résultat général à prouver.

**7 : froid sans recours, noir non urgent, puis interposition.** Ilse attend
la chaleur dès 321 : bûches « impossible », planches « nécessaire »,
enquêtes Maël/Sève « rien », aucun répit/plafond. À 330, abri/lumière sont
planifiables, mais sécurité **2,11 < 60** : aucun candidat urgent manqué.
Première divergence de 167 : **Gorm s’interpose devant Ilse à 347**.
Sève : attente alimentaire **10 → 285 min** ; froid Ilse/Maël : −50 ensemble.
À 535, Sève croit la porte verrouillée (`dit:ilse`, 53), sans clé/crochetage,
ignore Gorm ; la porte réellement ouverte n’est pas vue de près. Deux parts
restent ; faim épuisée en **28 nœuds**, aucune enquête restante. Attente
justifiée par les croyances ; enquêter sur l’obstacle serait un autre lot
général, pas une permission de traverser une porte crue verrouillée.

**Preuves/limites.** `entrees-exactes-42/` : quatre recharges état/rendu
identiques ; rejeu 110–450 identique au témoin. **48/48** captures
échantillonnées rechargées identiquement (`recharge-*.json`). Rendu vérifié :
`regarder` + `fiche`, pas Luna ni continuation depuis un choix interrompu.
1985/2024 seulement relues ; aucune garantie générale. Auberge sans eau
active : cause identifiée inapplicable, noir non attribué, aucun banc ajouté.
Aucune suite complète ni clé de signature ; branche seule, `main` intacte.
