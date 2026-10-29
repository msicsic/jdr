# Tâche Codex 273 : un échec ancien ne clôt pas une demande adoptée dont la raison tient

Le diagnostic 272 (`docs/taches/rapport-codex-272-retour-aubin.md`, fusionné ; bruts
`C:\Users\msics\donjon\artifacts\retour-272\`, dont la capture rechargeable à **117503**) établit un défaut réel :
Relais 2024, Aubin a adopté la demande `pulsion {objet: vivres, servir: ilse}` (motif `empathie`, palier 12). À 117503,
`deliberation.choisir` (vers la l. 2103) trouve dans `e["manque"]` le geste de tête du plan (demander une part à Gorm,
déjà refusé `necessaire` à 117170), met l'intention à `None` et inscrit une sortie **`dementie`**, alors que la raison
tient (Ilse crue affamée, `_fin_demande` renvoie `None`) et qu'aucun palier ne gagne. Ilse vient de sortir du champ de
vision : rien ne reprend la demande. À 117518, Ilse revue, le même plan renaît. Preuve : sur la capture rechargée,
retirer seulement `manque` conserve la demande.

## L'invariant
**Le démenti d'un moyen ne clôt pas une demande adoptée dont la raison tient encore : ses moyens sont revalidés
(`_reprendre_demande`, refus retenus selon leur cause, lot 225), et elle ne prend fin que sur une fin attestée
(`_fin_demande`) ou une préemption par un palier supérieur (lot 213).** Le geste manqué n'est pas réinstallé
aveuglément : si aucun autre moyen n'est admissible, la demande passe en attente ou en sommeil selon les règles
existantes, sans délai ajouté. Aucune exception par personnage, objet, scénario ou but.

Lot de 30 à 45 minutes. Pas de Luna, pas de suite complète (le superviseur la lance).

**Fichiers attendus** : `donjon/deliberation.py` (le traitement de `manque` dans `choisir`, la reprise de la demande) ;
`donjon/planification.py` seulement si la revalidation des moyens l'exige. Ne touche pas `agendas.py`, `echanges.py`,
`signes.py` (lots en cours).

## Vérification
- La capture réelle 117503 rechargée : la demande d'Aubin ne sort plus en `dementie` ; elle est revalidée (autre moyen
  ou attente), sans renaître sur la seule perception d'Ilse. Un autre cas de même nature (autre PNJ ou autre scénario,
  demande adoptée hors perception, obstacle maintenu puis levé). Une vraie fin (raison démentie) et une vraie préemption
  restent des sorties. Monde, rendu et scène identiques après recharge et laps entier/découpé.
- Tests ciblés des fichiers concernés (`test_echelle_choix`, `test_dynamique_besoins`, `test_reessai*`, `test_contrat*`,
  `test_aide*`, `test_empathie*`) ; **pas de suite complète**.
- Banc rapide 4 h, cinq scénarios × quatre graines, référence `0e3e626` (en cache si présente, sinon calculée une fois),
  sonde actuelle de l'intégration (lots 265/271) : suspects 219 par nuit sans hausse, le suspect Aubin Relais 2024
  disparu ou expliqué. Calcul long détaché à priorité réduite.

## Livraison
- Branche indiquée au lancement, poussée (sinon commit local, et dis-le). Rapport d'une page
  `docs/taches/rapport-codex-273-demande-adoptee.md` ; entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans le
  dossier d'artefacts indiqué au lancement. Termine par `LOT TERMINÉ` (résumé d'une ligne),
  `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
