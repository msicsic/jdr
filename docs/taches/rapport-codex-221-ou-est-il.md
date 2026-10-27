# Lot 221 — Demander à un tiers où est quelqu'un

27 octobre 2026 — `codex-ou-est-il`, **non fusionnée**, base `4fe33ef` vérifiée.
Aucun Luna ; deux calculs au plus, priorité réduite. Aucune clé configurée :
commits non signés. Bruts : `C:/Users/msics/donjon/artifacts/ou-est-221/`.

**Invariant et fonctions.** `s_enquerir`, appelé par `_chercher`, compare la
question à un tiers cru présent à l'inspection/appel (approche, durée, pression).
Plan coupé à la question, contact revalidé. `echanges.enqueter` répond par les
seules croyances du témoin, jamais par la position cachée de la cible. Même réponse
au joueur (contenu `localisation`). Témoin, réception et origine datés sont persistés
avant affichage, relais compris. Une indication dépassée par une recherche
infructueuse ne rouvre pas le lieu. Constats propres récents préservés.

**Réponses retenues.** Le registre `refus` persiste les lieux cités au-delà des
quarante souvenirs et des réponses d'ignorance. Délai, case, confirmation, relais
ou bruit non attribué à la cible ne réarment pas ce témoin. Seuls une localisation
nouvelle ou un déplacement perçu renouvellent le contexte ; aucun savoir privé
deviné. Les refus sociaux suivent leur cause.
**Extension autorisée par le superviseur** : mécanisme des refus dans
`deliberation.py` ; suivi du registre dans `esprits.croire` et validation de
sauvegarde. Fonctions des lots voisins, `social.py`, `pnj.py`, agendas et MJ intacts.

**Preuves.** Capture 215 Aubin/hameau 7 à 200 : question à Ilse, indication erronée
datée 195, provenance persistée. Auberge : Hugues interroge Odile et rejoint
l'étable indiquée à tort. Scène d'auteur au Relais : question autonome d'Aubin,
trajet et retrouvailles de Gorm après son départ. Monde/rendu/scène/conversation
rechargés, laps entier ou découpé, refus et joueur questionneur couverts.
La capture d'auberge 42 à 500 a révélé le réarmement parasite : **11 → 3 questions**
après correction commune, aucune question encore retenue exécutée ; monde,
sons et rendu identiques entre recharge et découpages. **18 nouveaux tests verts**.

**Suite unique : 2 444 tests / 283 fichiers, 3 166,835 s, sept échecs bruts,
zéro erreur, 16 ignorés.** Base `4fe33ef` : **20/20 ciblés verts** ;
après correctif : **38/38 reprises vertes**.
Archives N3/N9 complétées par `localisation:false` ; deux empreintes de graphe
recalées, plans/monde/textes/vues inchangés ; test de clôture d'un rendez-vous
fondé sur un engagement explicitement convenu, plutôt que sur un choix futur
d'appel. Aucune seconde suite complète. Créneau dépassé, notamment par cette suite.

**Banc final : cinq scénarios × quatre graines × 4 h**, compteur 199 actif.
Les 20 références exactes, calculées une fois, sont réutilisées après le correctif.
**17 questions : 12 indications, cinq ignorances ; aucun trio demandeur/témoin/cible
répété dans une même nuit, zéro plantage/usurpation.**

| Scénario | S/F/D moyens avant → après | Questions | Attente urgente PNJ·min |
|---|---|---:|---:|
| Relais | 11,25/3,75/1,50 → 14,25/4,75/1,69 | 5 | 0 → 1,25 |
| Mine | 22/4,25/1,61 → 20/4,25/1,50 | 2 | 0 → 0 |
| Auberge | 12/4,25/1,06 → 11,25/4,25/0,97 | 1 | 0 → 0 |
| Crue | 14/6,75/2 → 13/6,75/2 | 1 | 178,75 → 183,75 |
| Hameau | 31/8/2,54 → 32,75/8,25/2,42 | 8 | 128,75 → 151,25 |

Questions : total sur quatre graines ; attente : compteur moteur ; S/F/D du lot
183, inactifs compris. Appels **20 → 5**, retrouvailles de rendez-vous **13 → 3**
(ce compteur ne compte pas chaque rencontre). **Réserve avant intégration** :
suspects 199 **16 → 22**, entrées changées **144 → 147**, cycles accomplis
**494 → 489** ; nouvelle alerte de lecture sociale au hameau 2024 (huit contre sept).
**Absence globale de boucle nouvelle non certifiée.** Sur la capture 215 inchangée,
dix minutes ne déclenchent pas naturellement la question : P1 reste distinct.
Aucun gain uniforme de richesse ou d'attente garanti.
