# Lot 266 — rester près d'un proche effrayé

Branche `codex-rester-pres`, **non fusionnée**, base `7404d2d`, 28 octobre 2026.
Ni Luna, scénario, comparaison de modèles ni suite complète. Poste fixe,
deux processus réduits au plus. `echanges.py` intact ; dans `agendas.py`,
seule la validation des raisons accepte désormais `peur`, avec autorisation
explicite de l'utilisateur pendant le lot. Aucun mécanisme du lot 260 modifié.

**Invariant et code.** `deliberation.detresses_percues` extrait exactement la
lecture commune du lot 53, désormais partagée avec `autour` : tremblement,
fuite, impression encore appuyée par son signe, appel identifié de la minute.
`secours` ouvre la condition durable `pres` au palier SECOURS, avec le seuil
et le poids du 197, rancune exclue. Le contrat commun conserve sa raison ;
`_raison_tient` et `_fin_demande` relisent la peur perçue et le calme propre.
Absence du signe, détresse propre ou disposition retirée donnent une sortie
explicite ; les paliers supérieurs et le péril gardent l'arbitrage commun.
La disparition du signe dément la raison perçue, sans certifier une émotion
privée disparue. Un bénéficiaire cru mort ou inconscient est exclu.

`planification.gestes` offre le terminal de proximité ; `_pulsion` emploie
les routes, présences, approches et tarifs communs, puis un séjour `tenir`.
La cible est dans `vises` et la clé de mémoire ; lieux/cases crus, métrique,
obstacles et tarifs sont déjà dans `_entrees`. Mémoire, graphes et contrôle
VERIFIER restent communs. Sans localisation crue, le préfixe `rejoindre` du
226 cherche le contact, sans terminal sur une présence supposée. `pnj`
exécute `rester` par l'approche physique commune, sans case choisie par le
planificateur ; au contact, le placement accessoire ne le fait pas repartir.
La compagnie n'injecte aucun point de sécurité : `autour` et `vecu` restent
seuls responsables de l'apaisement. Proximité revalidée, souvenir enregistré,
puis phrase visible seulement si les deux personnes sont perçues du joueur.

**Vérification ciblée : 76 tests distincts verts, huit fichiers.** Fichiers
du brief, plus planification et trajet estimé. Six nouveaux tests : Aubin/Ilse
et Mathe/Lucien, arrivée, maintien, compagnon déjà au contact immobile,
sécurité décroissante, peur d'Ilse réellement accrue dans le noir puis fin
naturelle, souci faible/rancune/dos/noir/détresse et faim propres, appel
identifié sans localisation, positions/besoins privés sans effet et
localisation crue qui change le devis. Monde entier, rendu/carte et scène
identiques après recharge ; même laps entier/découpé. Deux anciens oracles
de dynamique étaient modifiés par les nouveaux secours (ils passent sur la
base : deux méthodes, 61,907 s). Leurs seules scènes sont explicitement sans
souci spontané ; assertions de garde/recherche inchangées, autres scènes
de ce fichier conservées. Dernière reprise : 23 tests / trois fichiers,
85,450 s ; dernier fichier de proximité : six tests, 4,546 s.

**Banc détaché en cours**, `tools/banc_rester_pres.py` : 4 h, cinq scénarios
× 1985/7/42/2024, référence exacte `7404d2d` (commit de départ ; `main` local
reste à `c870c8b`). Références exactes réemployées, seules les absentes sont
calculées/rangées ; branche jouée une fois avec compteurs. Sonde pure sur
état final complet et chronique en nuit courte ; seule la durée de calcul
diffère. Scène active : état entier identique, un secours et **2,0 minutes**
de sécurité urgente en baisse avec sa compagnie. Ce compteur mesure le temps
vécu sous secours, **pas un gain causal contre une autre trajectoire**.
`bilan.json` conserve les suspects/cycles 219 et boucles **par nuit**, les
épisodes de peur et les minutes apaisées. Résultats et absence de nouvelle
alternance **non certifiés avant lecture du banc** ; lot non déclaré validé.

Bruts : `C:/Users/msics/donjon/artifacts/rester-266/`.
Fin attendue, écrite en dernier : `banc/fin.json` (vérifier `code`, puis
`bilan.json` et les nuits). Les signes restent faillibles et relus aux
événements/minutes existants, sans délai de maintien ajouté. Aucune garantie
nouvelle sur la justesse sémantique des impressions ou toutes les boucles.
