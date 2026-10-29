# Lot 272 — retour d’Aubin au Relais

28 octobre 2026, laptop. **Branche `codex-retour-aubin`, non fusionnée**,
base `aaaf4cf` (intégration du 271 : `c293d3f`). Diagnostic seul ; aucun code
du jeu modifié, ni Luna, suite complète ou banc comparatif.

**Verdict : défaut de continuité confirmé.** Le retour possède un déclencheur
réel ignoré par la sonde, la perception renouvelée d’Ilse ; l’engagement aurait
cependant dû survivre à sa disparition momentanée du champ de vision. Il ne
s’agit pas d’un réessai déclenché par le seul délai.

**Reproduction.** Une nuit actuelle, Relais 2024, départ tiré, joueur passif
en `chambre_cloche`, 4 h, un processus à priorité réduite : **15,999 s**.
Les classements et tous les allers-retours sont identiques à l’archive 271.
Le suspect revient exactement à **117518**, après naissance à **117488**
et sortie à **117503**, soit **1,5 seconde** d’interruption. Huit captures
avant/après les choix, dont avant abandon et avant retour : **24 égalités**
monde/rendu/scène après sauvegarde et recharge. Les deux appels à 117518
produisent deux contrôles mais réécrivent les mêmes fichiers horodatés.

**Abandon.** But `pulsion {objet: vivres, servir: ilse}`, motif `empathie`,
palier **12**, valeur **18** ; plan : demander une part à `marchand`.
À **117170**, ce même geste avait réellement échoué (`necessaire`). Le refus
conserve `cause = [[moyen, vivres, reserve, null]]`, mais il **ne tient déjà
plus** aux trois relevés : `moyens_crus` comporte aussi
`[ouvert, reserve, null, null]`. Cela décrit les croyances, pas une ouverture
réelle nouvelle entre 117503 et 117518. Aucun `renoncement` du lot 225
n’est enregistré ; le marqueur `manque` conserve seulement le geste et la
minute **195**.

À 117503, `choisir` reconnaît ce geste dans `manque`, met `courant` et
`e[intention]` à `None`, et inscrit une sortie **`dementie`**, issue de cet
échec ancien. Ilse reste crue affamée et consciente ; `_fin_demande` renvoie
`None`. Aucun palier ne gagne : le candidat devoir **5** échoue, puis seuls
les candidats argent **14** sont essayés, sans plan. Ilse, passée de la case
`[5,1]` à `[6,1]`, n’est plus perçue par Aubin : aucun candidat de naissance
`secours`. L’effacement préalable empêche la reprise de la demande adoptée
par `_reprendre_demande`, qui aurait autrement gardé son identité.

**Retour et sonde.** À 117518, Ilse revient en `[5,1]`, redevient perçue,
et `secours` recrée le même candidat et le même plan. Ni ressource, ni refus,
ni valeur de croyance ne change dans les catégories comparées par la sonde.
`relever_entrees` ignore les perçus effectifs, les cases et la provenance des
croyances : `ilse.lieu.valeur` reste `antichambre`, alors que la source passe
de `entendu` à `vu`. Son « strict complet » n’est donc pas une identité de
toutes les entrées du choix. Cette perception explique la renaissance ; elle
ne prouve pas que l’obstacle du geste a changé depuis l’abandon.

**Preuve causale et suite.** Sur la capture 117503 rechargée, le choix intact
reproduit la sortie ; retirer uniquement `manque`, changer uniquement sa cible,
ou dater uniquement ce marqueur de la minute précédente conserve la demande,
avec Ilse toujours hors de vue. Les quatre états résultants passent chacun
les trois contrôles de recharge (**12 égalités** supplémentaires).
Invariant proposé pour un petit lot : **le démenti d’un moyen ne clôt pas une
demande adoptée dont la raison tient encore ; ses moyens sont revalidés, sa
fin ou sa préemption doit être attestée.** Corriger le contrat commun entre
`choisir`, la replanification et l’exécution, sans supprimer les refus ni
réinstaller aveuglément le geste manqué. Vérifier cette scène et une autre
demande adoptée hors perception, avec obstacle maintenu puis levé et recharge.
La sonde devra distinguer les entrées perceptives sans les transformer en
justification automatique. **Aucune correction ni garantie générale livrée.**

Bruts : `C:/Users/msics/donjon/artifacts/retour-272/` : `diagnostic.py`,
`relecture.py`, `trace.json`, `episodes.json.gz`, `avis.json`, `nuit.json`,
captures et vues, `recharges.json`, `relecture.json`, `fin.json` (`ok=true`).
**Aucun calcul actif.**
