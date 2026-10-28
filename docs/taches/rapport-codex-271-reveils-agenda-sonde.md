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
ne justifient rien. Les premiers lancements ont rencontré les droits Windows
des répertoires temporaires ; les vérifications avec sauvegardes ont été
relancées hors bac à sable, avec priorité réduite.

**Campagne détachée à terminer :** vingt paires de nuits de **4 h**, cinq
scénarios × quatre graines, sur le moteur courant ; un processus réduit,
nuits sonde/témoin successives. Deux observateurs avant/après dans la nuit
sondée, état complet, empreintes, chronique, mesures, récit, souvenirs et vues
rechargées comparés au témoin. `bilan.json` publiera les compteurs avant/après
et rappellera la référence 265 (suspects **1**, à expliquer **47**, cycles
**489**, préemptions **46**, changements de moyen **9**). Résultats finaux non
encore revendiqués ; signal de fin écrit en dernier :
`C:/Users/msics/donjon/artifacts/reveils-271/fin.json`.

**Limites.** Horizon existant de 60 minutes, relevés aux transitions de décision
et mémoire bornée des reçus : une preuve disparue ou non relevée reste inconnue.
Le lien structurel au plan ne démontre pas la nécessité individuelle de chaque
entrée par retrait contrefactuel. Aucune certification générale d'absence de
boucle. Bruts, scripts et preuves :
`C:/Users/msics/donjon/artifacts/reveils-271/` (`captures.json`, `campagne.py`,
`detecteur_avant.py`, puis `bilan.json` et `fin.json`).
