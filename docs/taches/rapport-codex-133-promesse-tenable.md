# Lot 133 — présence matérielle au devis d'une promesse

Branche `codex-promesse-tenable`, **non fusionnée**, base `3cdcab3`.
Aucun Luna, ni changement du MJ, des scénarios, de `echanges.py`, `agendas.py`
ou des fichiers réservés aux autres lots. Calculs à priorité réduite.

**Cause reproduite.** Audit moteur crue 11, 12 h, départ tiré, joueur dans
`chambre_cloche`, sans VERIFIER ni vérification spatiale supplémentaire :
`audit_nuits.jouer_nuit`, mêmes paramètres que `audit_nuits.py jouer --scenarios
crue --graines 11 --heures 12`. Une sonde en lecture seule capture l'état avant
`proposer`, à **126226**, dans `tests/data/promesse-crue11-210.json.gz`.
Le marché est accepté et l'abandon reproduit à **126336**. Une seconde sonde
établit qu'à cet instant `empeche` passe de faux à vrai après l'échec du premier
geste : croyance `porte.lieu = None`, source `essai`. Aucun geste réussi sur la
porte. Son intégrité n'est **pas la cause de cet abandon** : le devis situe la
porte dans `antichambre` par son `lieu`, tandis que `present_physique` ne la situe
que dans ses salles `relie`, `crypte` et `beffroi`. Ilse est dans l'antichambre.
Ces attaches sont structurelles, déjà disponibles à la recherche ; l'essai ne
révèle donc pas un aléa inconnu légitimant la promesse.

**Contrat commun.** `planification._mesurer_direct` exige désormais la présence
physique de toutes les cibles désignées par `pnj._a_toucher`. `Vue.present`
réutilise `Monde.present_physique` sur les lieux et ouvertures crus, puis les
effets projetés du plan, contenants et porteurs compris. Aucun état réel mobile
inconnu n'est substitué à une croyance. `_mesurer_direct` applique aussi ce
contrôle hors mode cases, en conservant les anciens coûts. Devis, promesse
autonome, acceptation, planification et échéance passent ainsi par la même
précondition de présence, sans branche par tâche ou scénario.

**Preuves.** 42 tests existants ciblés et quatre nouveaux tests, repris après correction :
capture réelle et garde-manger incorporé au décor, refus avant transfert ou
engagement, absence d'abandon consécutif ; sauvegarde réelle, état, mémoire,
rendu et chronique comparés après 12 s d'un bloc ou en 3/4/5 s ; projection des
contenants ouverts et des possessions sans lecture d'un lieu réel inconnu ;
absence de cases ; service possible accepté puis tenu. Le parcours existant
de deux services tenus compare aussi le même laps découpé après recharge.

**Banc final**, 4 h × quatre scénarios × quatre graines : référence calculée
une fois, puis réutilisée du cache après correction. **16/16 états finaux
complets identiques**, mêmes chroniques, récits, souvenirs, mesures métier,
boucles et alertes. Zéro plantage, violation ou usurpation ; aucune répétition
supplémentaire dans ces nuits. Seul écart de compteur : recherches neuves
**629 → 624** en crue 7. Totaux propositions/acceptées inchangés : Relais
**0/0**, mine **10/1**, auberge **3/1**, crue **5/0**. Tâches promises en
contrepartie offertes/acceptées/tenues/rompues : **0/0/0/0** dans les deux
versions ; la tenue est démontrée par les scènes ciblées, pas par ce banc.

**Suite complète unique : 2 077 tests, 228 fichiers, 11 échecs, zéro erreur,
1 276,59 s**, deux processus réduits. Elle a révélé un contrôle trop bas dans
`Vue.approche`, également appelée pour estimer une fourniture future ; déplacé
vers les gestes réellement proposés par `_mesurer_direct`. Les neuf fichiers
en échec et les promesses sont repris : **139 tests, deux échecs MiMo `6 != 5`,
zéro erreur, 74,00 s**, un processus. Ces deux échecs sont reproduits sur une
archive intacte de **3cdcab3** : **13 tests, les deux mêmes échecs, 10,30 s**.
Bilan consolidé : seulement les deux échecs historiques ; aucune seconde suite
complète. Le premier banc, affecté par ce contrôle prématuré, est conservé
dans les bruts ; les chiffres ci-dessus portent sur la version finale.

**Limites.** Ce lot rétablit la précondition commune de présence. Il ne prouve
pas l'équivalence de toutes les autres préconditions des gestes. En particulier,
il ne corrige pas la fermeture ou le verrouillage d'un objet brisé accessible,
ni le champ de localisation incohérent du scénario. Les trajets estimés peuvent
encore échouer lors de l'approche réelle. Une croyance fausse sur un bien mobile
reste possible et peut donner lieu à une découverte réelle. Les promesses de
condition ponctuelle ne deviennent pas des gardes durables. Aucun temps CPU
comparatif revendiqué sur le poste partagé. Aucune clé Git de signature
configurée : commit non signé. Bruts : `artifacts/promesse-133/`.
