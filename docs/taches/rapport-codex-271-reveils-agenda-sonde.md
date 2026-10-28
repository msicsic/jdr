# Lot 271 — entrées publiées et réveils justifiés

28 octobre 2026, laptop. **Branche `codex-reveils-agenda-sonde`, non fusionnée**,
base `de74ff2`, moteur `1355f7a`. Outils seulement ; aucun fichier de `donjon/`
modifié, ni Luna ni suite complète.

**Invariant.** Une reprise du même but devient `entree_publiee_utilisee` si une
entrée publiée depuis la sortie concerne le plan repris et que ce plan respecte
les renoncements. `relever_entrees` conserve les biens portés et possédés ainsi
que les reçus `engagement_tenu` du moteur. `_entrees_utilisees` compare ces
relevés et les lieux crus ; `_references_plan` lit les identifiants des étapes,
y compris les conditions et contreparties imbriquées. Aucun nom de personnage,
objet, scénario ou but n'intervient dans la règle. Une clôture exige une charge
observée active, retirée, un reçu nouveau daté dans l'intervalle et son objet
référencé par le plan ; le retrait ou l'annulation seuls ne prouvent rien.
La règle s'insère après les preuves 265, avant le classement résiduel ;
`total_justifies` et le raccord générique d'`audit_nuits` comptent cette classe.

**Scènes et preuves.** Brune hameau 2024, départ tiré, joueur passif en
`chambre_cloche` : **591** reconnu par les crochets acquis et proposés à la
vente ; **929** par le lieu de Gorm appris et utilisé pour aller le voir.
Le pied-de-biche n'est pas invoqué : le plan de 929 ne l'emploie pas.
Ces deux reprises sont vérifiées sur le moteur actuel, avec/sans sonde,
état complet et chronique identiques, monde/rendu/scène conservés à la recharge.
Relecture des captures et plans publiés du 268 sous `881db69` (sans nouvelle
nuit historique) : **495, 1393 et 59658** reconnus ; **59658** porte notamment
le reçu du travail accompli sur la torche. **738 reste à expliquer** : lumière
et admissibilité changées, hors des preuves de ce lot. Dix-huit contrôles de
recharge des captures, monde/rendu/scène identiques. Mireille auberge 1985
**36720**, archive 219, reste `repetition_sans_entree_nouvelle`.

**30 tests ciblés distincts verts** dans `test_detecter_changements_avis.py`
(30 en 96,262 s ; trois tests concernés par la dernière précision sur les
charges annulées encore présentes revérifiés en 1,855 s), un processus réduit.
Contre-épreuves en scène rechargée : lieu appris sans rapport avec le plan et
engagement simplement retiré toujours à expliquer ; aucun changement toujours
suspect. Second cas positif : verrouillage réellement exécuté pour Odile,
engagement clos par `agendas.echoir`, puis plan visant le même meuble.
Plans inadmissibles, références textuelles et reçus anciens/charges annulées
ne justifient rien. Sauvegardes vérifiées hors bac à sable après les refus
d'accès Windows aux répertoires temporaires.

**Campagne terminée : 20/20 identités, 180 contrôles verts, zéro plantage.**
Vingt paires **4 h**, cinq scénarios × quatre graines, départ tiré ; nuits
sonde/témoin successives, un processus réduit détaché, **2 466,737 s**.
État complet, empreintes, chronique, mesures, récit, souvenirs, état et vues
rechargés identiques. Deux observateurs avant/après classent les mêmes nuits :

| Compteur | Référence 265, après | Avant 271 | Après 271 |
|---|---:|---:|---:|
| Suspects | 1 | 1 | 1 |
| À expliquer | 47 | 41 | 15 |
| Entrées publiées utilisées | 0 | 0 | 26 |
| Cycles accomplis | 489 | 495 | 495 |
| Préemptions | 46 | 48 | 48 |
| Changements de moyen | 9 | 14 | 14 |
| Progressions réelles | 0 | 1 | 1 |
| Pertes d'état payé | 5 | 4 | 4 |

**Effet propre mesuré : 26 reclassements, tous de « à expliquer » vers la
nouvelle classe**, aucun retour ajouté ou retiré, aucun suspect effacé.
Relais 8, crue 13, hameau 5 ; tous portent un lieu cru changé, dont cinq
également une acquisition/propriété nouvelle. Les clôtures sont couvertes par
la scène ciblée et la capture historique. Brune **591/929** reconnus aussi dans
la nuit complète. Suspect actuel conservé : Aubin, Relais 2024, **117518**.
Dérives **212 → 212** ; pertes physiques **3 → 3**, bénéficiaire parti **1 → 1**,
aucune violation de service. Les écarts entre la référence 265 et l'avant-271
ne sont pas attribués à ce lot ; aucune référence rejouée ni comparaison de
temps entre campagnes. `fin.json` : `ok=true`, vingt paires achevées ;
**aucun calcul actif**.

**Limites.** Horizon existant de 60 minutes, relevés aux transitions de décision
et mémoire bornée des reçus : une preuve disparue ou non relevée reste inconnue.
Le lien structurel au plan ne démontre pas la nécessité individuelle de chaque
entrée par retrait contrefactuel. Aucune certification générale d'absence de
boucle. Bruts, scripts et preuves :
`C:/Users/msics/donjon/artifacts/reveils-271/` (`captures.json`, `campagne.py`,
`detecteur_avant.py`, `tests.json`, `bilan.json`, `fin.json` et vingt nuits
compressées avec les deux analyses).
