# Lot 237 — diagnostic des alertes du lot 231

28 octobre 2026, PC fixe. **Branche `codex-alertes-231`, non fusionnée**,
base/intégration figée `e84d5a7` (218/229/230/232 inclus). Jeu inchangé,
aucun Luna ni suite complète. Replays séquentiels, priorité réduite,
`4306c14` détaché puis intégration ; mêmes joueur/départ qu'au lot 231.

**Mine : inactivité mal qualifiée.** Les
465 PNJ·min historiques (58,125 par nuit) viennent exclusivement d'Odon :
305 en graine 500, 160 en graine 7. En 500, après le renoncement de 103
devant les témoins, le choix de 105 conserve la faim « pressante » malgré
`renonce` pour manger le pain de Lucien et aucun recours d'enquête restant ;
première inactivité ainsi mal classée à **107**. Autre cas : **539**, graine 7,
vivres derrière le garde-manger, même obstacle de témoins retenu. `_classer`
ne conclut « attente » que pour des essais tous `rien` ; `renonce` laisse
l'ancien classement, que `inactivite` interprète comme `sans_recours`.
Le refus de voler reste justifié. Sur l'intégration : **275 et 145**, mêmes
premières inactivités à 107/539 ; défaut toujours présent. **Lot A** : faire porter
au choix et au
signalement la même absence de moyen admissible, renoncements compris
(`donjon/deliberation.py`, `tests/test_reessai_obstacle.py`,
`tests/test_signalements.py`).

**Appels : signal distinct, aucune faute établie sur l'épisode suivi.** Les
huit archives donnent 43 → 140 appels. Odon/mine 1985 en fournit 19 : début
de l'épisode à **616**, enquête de chaleur vers Bram, sept lieux prospectés,
puis douze
réouvertures effectives avant rappel (cinq localisations, sept bruits nouveaux).
Aucun rappel sans nouvel indice dans ce cas ; pas de lot correctif déduit
du seul volume. Sur l'intégration, Odon passe de **19 à zéro appel**, tous les
appels de cette nuit de **33 à 16** ; « sans recours » reste nul.

**Gorm, hameau 1985 : recours invalidé par son propre classement.** Les onze
suspects chaleur de 541–545 sont reproduits ; les premières délégations visent
des moyens différents. Premier abandon sans nouvel échec isolé : **544, instant 326556**,
but chaleur/brasero vide adopté à 326536, après l'accord d'Aubin pour rapporter
du bois. La revalidation le remplace par aucun but, puis la chaleur revient
et interrompt l'inspection. Contre-épreuve sur la capture 545 : seul
`urgences.chaleur.etat` change ; `attente` donne le recours vide, `presse`
donne `None`, sur les deux moteurs. `Vue.detresses` ouvre l'aide après une
attente ; sélectionner le recours efface cette condition d'ouverture.
Sur l'intégration, **aucun retour de chaleur de Gorm** : à 541, brasero allumé,
chaleur 43,1. Occurrence disparue, mécanisme latent toujours reproduit sur capture.
**Lot B** : rendre l'aide et l'attente de réalisation stables sous leur propre
adoption (`donjon/planification.py`, `donjon/deliberation.py`,
`tests/test_recours_prioritaire.py`, `tests/test_contrat_engagement.py`).

**Maël, hameau 42 : restitution incohérente avec son trajet.** Les quatre
suspects sont reproduits. **419, instant 251779** : restitution torche→Aubin
adoptée ; **251840**, au beffroi sombre, `necessaire=True` fait disparaître
ce même recours au profit de l'inspection de la crypte (palier 9 contre 5).
Même bascule antichambre/échoppe à 420 ; restitution effective seulement
à 451. `_rendre` consulte la nécessité immédiate du bien via
`echanges.necessaire` et `deliberation.lumiere_utile`, sans distinguer son emploi pendant le
transport de son abandon à la remise. Sur la capture 421, les deux moteurs
rejettent encore le retour en cours. **Lot C** : admission et revalidation
communes du transport et de l'état de remise, sans forcer une remise qui
laisserait un besoin sans moyen (`donjon/planification.py`, `donjon/echanges.py`,
`donjon/deliberation.py`, `tests/test_garde_pret.py`,
`tests/test_contrat_engagement.py`).

Sur l'intégration, **zéro suspect de Maël** : à 419, torche à Aubin, aucun prêt
à Maël. Occurrence disparue ; limite du juge toujours reproduite sur capture.

**Trois invariants distincts**, malgré des fonctions communes : qualification
d'un obstacle retenu (A), stabilité sous adoption (B), cohérence du transport
et de la remise (C). Aucun correctif proposé pour le seul volume d'appels.

**Preuves et limites.** Dix nuits × 12 h : mine 500/7/1985, hameau 1985/42,
deux versions. Les cinq replays historiques retrouvent chronique, récit,
souvenirs, empreintes et mesures communes des archives ; **228/228 captures**
avec monde et rendu identiques après recharge. Pas de nouvelle moyenne sur
huit graines ni de garantie générale des boucles ; les contre-épreuves
historiques ne remplacent pas les nouvelles trajectoires. Bruts, synthèse,
contacts et manifestes : `C:/Users/msics/donjon/artifacts/alertes-237/`.
