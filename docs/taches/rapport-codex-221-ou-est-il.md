# Lot 221 — Demander à un tiers où est quelqu'un

28 octobre 2026 — `codex-ou-est-il`, **non fusionnée** ; base initiale `4fe33ef`,
puis intégration `bd45f65` (213/219) fusionnée dans `813d45b`. Seul conflit :
`docs/etat-dev.md`, résolu en conservant les deux historiques ; aucun conflit de code.
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

**Reprise après intégration : 38/38 tests ciblés verts, 49,729 s.**
Aucune seconde suite complète, conformément à la demande : aucun conflit de code.

**Banc final contre `bd45f65` : cinq scénarios × quatre graines × 4 h**,
classes 219 actives, vingt références calculées une fois et mises en cache.
**Critère satisfait dans les cinq scénarios** : répétitions suspectes inchangées.
Les cinq épisodes suspects sont même intégralement identiques à la référence :
Mathé/mine 1985 (acheter), Mireille/auberge 1985 (servir), Tilo/auberge 42
(demander), Brune/crue 42 et 2024 (proposer). **Aucune nouvelle répétition
suspecte issue des questions ; zéro plantage/usurpation.**

| Scénario | Suspects | Préemptions | À expliquer | Attente urgente | S/F/D moyens |
|---|---:|---:|---:|---:|---|
| Relais | 0 → 0 | 5 → 16 | 7 → 6 | 0 → 0 | 9,50/3,50/1,44 → 12/4,25/1,63 |
| Mine | 1 → 1 | 2 → 2 | 15 → 14 | 0 → 0 | 25,50/4,50/1,96 → 26,25/4,50/1,96 |
| Auberge | 2 → 2 | 16 → 15 | 4 → 4 | 0 → 0 | 11/4,25/1 → 10,25/4,50/0,97 |
| Crue | 2 → 2 | 8 → 6 | 17 → 13 | 196,25 → 218,75 | 17,50/7,50/2,63 → 17,25/7,50/2,50 |
| Hameau | 0 → 0 | 22 → 28 | 18 → 32 | 97,50 → 87,50 | 31/7,50/2,67 → 40,50/8,50/2,63 |

Classes : totaux sur quatre graines ; attente : moyenne PNJ·min du compteur moteur ;
S/F/D du lot 183, inactifs compris. Totaux : suspects **5 → 5**, préemptions
**53 → 67**, à expliquer **61 → 69**, cycles accomplis **468 → 501** ;
satisfaction/démenti d'autrui **0 → 1**, autres classes nulles.
**22 questions** (Relais 5, Mine 4, Auberge 1, Crue 1, Hameau 11).

Un trio revient au hameau 42 : **Gorm → Maël, au sujet d'Aubin**, minutes
115 et 147, deux refus « méfiance ». Le diagnostic reproduit la chronique :
la rancune perçue envers Maël passe **0 → 14**, autres axes inchangés. Le refus
social suit ces axes et se réarme à ce changement, sans délai ; un changement
défavorable autorise donc aussi un réessai. **Limite du contrat social signalée**,
aucune répétition suspecte 219 nouvelle. Trace : `diagnostic-question-bd45f65.*`.

**Limites.** La hausse de l'attente urgente en crue et des entrées « à expliquer »
au hameau demeure visible ; aucune amélioration uniforme de richesse ou d'attente
n'est garantie. Le précédent résultat 199 (16 → 22) concernait la base antérieure
et n'est pas le critère 219. Sur la capture 215 inchangée, dix minutes ne déclenchent
pas naturellement la question : P1 reste distinct. Bruts de cette reprise :
`reprise-bd45f65-cibles.*`, `banc-bd45f65.*`, `bilan-bd45f65.*`.
