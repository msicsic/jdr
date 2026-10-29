# Lot 313 — contact sans position connue

29 octobre 2026. Branche `codex-contact-inconnu`, **non fusionnée** ; base
`integration d76f272`. Validation longue en cours ; aucun résultat du banc
n'est encore déclaré acquis. Ni Luna, ni suite complète.

**Invariant.** Une portée insuffisante ou une case inconnue ne prouve pas
l'absence. `positions_crues.case_contact` est l'accès commun de
`pnj._case_crue` et `Vue.case_objet` : il suit les seuls liens crus de
contenant, support ou porteur, avec arrêt sur cycle. La chaîne prime sur
l'ancienne case du contenu. Les effets projetés du plan restent privés ;
aucune position réelle de mobile n'est utilisée pour résoudre ce contact.
Les objets fixes conservent leur position de lieu connue.

`pnj._approcher` juge désormais la distance au point cru et prépare une
observation dans le lieu cru si la case manque : marche vers la salle,
puis son centre et tour d'horizon. Le geste physique contrôle ensuite sa
portée réelle. `trajet_estime.approche` mesure le même préparatif, tour
compris, au lieu d'une approche gratuite. `_mesurer_direct` conserve son
contrôle des présences projetées. `_hors_d_atteinte` ne dément plus une
présence à distance ou sans case : il faut un emplacement cru touché ; un
objet vu ou caché dans un contenant fermé reste présent. Aucun changement
de `planifier_tache` ni d'`echanges.empeche` (lot 312).

**Cas réel.** Les archives `services-308` sont absentes de ce poste. Le
rejeu déterministe de la base reproduit Relais 7 à **856 dixièmes** : Gorm
sert les vivres à Brune, croyance `vivres → reserve`, salle/case nulles ;
ancienne approche **0**. Capture reconstruite et versionnée
`tests/captures/contact-313-relais-7.json.gz`, générateur
`tools/capturer_contact_313.py`. La correction déclenche une marche de
**30 dixièmes**, conserve la charge, puis Gorm sert Brune.

**Épreuves ciblées.** Sept régressions dans
`tests/test_contact_position_inconnue.py`. Cas réel et mine : source dans
un contenant d'une autre salle, service réussi, aucun service exécuté en
échec, monde complet et textes identiques après six minutes d'un bloc ou
minute par minute. Monde, rendu et scène identiques après sauvegarde et
rechargement. Contre-épreuve : source réellement déplacée hors du
contenant attendu, un seul démenti au contact pendant six minutes, aucune
portion servie, absence crue enregistrée puis rechargée. Autres contrôles :
case inconnue, observation, lien au porteur, cycle, devis pur et déplacement
réel caché sans changement du premier pas.

**Mesures.** Contact/marche/trajets : **35 tests verts**, quatre fichiers,
13,079 s, deux travailleurs à priorité réduite. Comparateur : six tests
verts (passe précédente). Validation élargie détachée : onze fichiers
ciblés, puis **4 h × quatre graines × Relais/auberge/mine**, référence
figée `d76f272`, cache commun, référence puis branche, deux travailleurs
réduits au plus. Le comparateur expose `gestes_refuses_contact` (appels au
refus matériel `_hors_d_atteinte`) et `approches_impossibles` (approche
renvoyant `None`), avec leurs occurrences ; sa clé d'instrumentation
invalide automatiquement les anciennes archives dépourvues des compteurs.
Les références absentes sont calculées une fois et rangées, jamais
relancées pour comparer des temps.

Bruts : `C:/Users/msics/donjon/artifacts/contact-313/` ; `tests.json`,
`comparaison.json`, `mesures.json` (services, refus, suspects 219 et boucles
par nuit), journaux et **`fin.json` écrit en dernier** par
`tools/verifier_contact_313.py`. Les résultats de cette passe restent à
lire avant clôture du lot.

Le premier lancement a échoué avant les tests : `priorite.ceder` ne trouvait
pas `donjon`. Le lanceur ajoute maintenant la racine du worktree aux imports,
fixe le cwd des sous-processus et protège aussi l'import et l'initialisation
de priorité par le bilan final. Deux épreuves couvrent ces échecs de démarrage.
La relance sur `5660366` conserve les anciens journaux : PID **45596**
constaté vivant en `BelowNormal`, `relance.log` annonce la racine et le
démarrage des tests ; `tests.log` confirme « 11 fichiers, 2 processus,
priorité réduite ». Deux tests du lanceur verts. Aucune surveillance répétée.

**Limites.** Une observation sans preuve suffisante, notamment dans le
noir, ne devient pas une absence : ce lot ne garantit ni recherche
exhaustive ni absence universelle de boucle. L'admissibilité d'un plan
reste une projection conditionnelle, jamais une preuve de présence réelle.
Les statistiques du banc et les éventuels nouveaux avis restent à examiner.
