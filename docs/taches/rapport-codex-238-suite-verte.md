# Lot 238 — suite verte : arrêt sur divergence du cas réel

Branche `codex-suite-verte`, non fusionnée ; base `e84d5a7`.
Tests seulement, aucun moteur, adaptateur ou Luna modifié.

## MiMo : faux audit périmé, correction vérifiée

Les deux échecs `6 != 5` sont reproduits sur l'atelier. Le générateur commun
`tests/test_fournisseurs_jeu.py::arguments` renvoyait `verdict` et `comptes`,
alors que `narration.schema_audit` exige `nature` et interdit les propriétés
supplémentaires. La validation de transport provoquait ainsi une relance
supplémentaire. La simulation emploie désormais `nature=mecanique`,
`portee_mecanique=etablie`, la source `resultat_resolu`, et les extractions
`eclairages`/`rappels` selon les faits fournis. Aucun compte d'appels ni
assertion de sauvegarde, reprise ou exécution unique n'a changé.

Les deux fichiers entiers passent : **13 tests, zéro échec, 7,627 s**,
avec les deux scènes et les rejets archivés. Verdict : oracle de transport périmé.

## Torche : prémisse du brief non reproduite, analyse moteur nécessaire

La passe initiale des trois fichiers : **36 tests, trois échecs, 27,855 s**.
Contrairement au brief, le test actuel attend déjà une liste vide et ses
deux `all(...)` sont alors vacuement vrais. Sur cette base, une perte réelle
est pourtant relevée : paiement Ilse → Brune à la minute 0, réussite à
`3188`, perte à `3615` (600 unités/minute), classe
`prestataire_beneficiaire_present`, `violation=True`.

Un rejeu instrumentant uniquement `_executer` confirme le geste
`eteindre/torche` de Brune à `3615`, combustible avant **59**, et
`biens.services_proteges(monde, 'brune') == []` avant ce geste. La sonde
retient les lieux crus de la torche et d'Ilse à `echoppe`, porteur Brune.
Ce n'est donc pas une cessation physique par épuisement. Il reste à établir
si une clôture antérieure de protection légitime le geste ou si le moteur
perd cette protection ; la justesse de la classe de la sonde reste à examiner.
Le verdict « oracle périmé » n'est pas établi pour ce test. Aucun réancrage,
aucune assertion affaiblie, aucune capture modifiée.

Le brief impose de s'arrêter et poser une question si le jeu ou l'adaptateur
est en cause : arrêt sur cette divergence, sans toucher au moteur ni au test
de la torche. **Suite complète non lancée**, le lot étant suspendu avant la
validation finale ; suite verte non revendiquée. Pas de banc ni appel modèle.
Deux processus au plus, priorité réduite, Python du dépôt principal sur PC fixe.

Bruts : `C:/Users/msics/donjon/artifacts/suite-238/avant.{json,log}` et
`mimo-apres.{json,log}` ; diagnostic de rejeu dans `diagnostic-torche.log`.
