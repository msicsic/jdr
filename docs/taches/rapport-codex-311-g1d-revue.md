# Lot 311 — G1 d : terminé, non fusionnable

29 octobre 2026 — code `4c9120f`, intégration `d58b343` fusionnée sans rebase
(`1b16cdd`). Une passe, six scripts, référence `230e7b3` exclusivement en cache,
copies vérifiées par SHA-256. Aucun incident réseau, arrêt, échec de recharge
ou calcul actif. **Dernière reprise : pas de G1 e. Aucun correctif après mesure.**

| Critère | Atteint ? Référence → lot |
|---|---|
| Admission au premier coup | **Non**, 22 → 21/30. |
| Fidélité, refus publics fidèles compris | **Non**, 23 → 20 au premier coup ; 27 → 23 après corrections. Familles perdues ci-dessous. |
| Abandons au plus égaux | **Non**, 1 → 3 : écoute de référence ; levier, passage et coup du lot. |
| Aucune famille de refus nouvelle | **Non**, 8 → 9 refus ; avis sur lieu inconnu absent de la référence. |
| Revue distincte de l'admission | **Partiellement, invariant complet non atteint.** Protocole acquis : une compilation et une revue pour chacun des deux refus publics, sans relance. Mais faux refus de style et attente omise demeurent. |
| Appels/tour ≤ 3,30 | **Non**, 104/30 = **3,47**, contre 99/30 = 3,30. |
| Prix demandé fidèle | **Oui**, 20 pièces, or 24 inchangé et engagements vides après recharge. Voie parole/propos ; opération `prix` toujours non jouée par Luna. |
| Taille et préfixe mesurés | **Oui**, 22 572 → 13 858 jetons/compilation ; cache 11 812 → 5 113, soit 52,3 → 36,9 %. |
| Aucun texte interne affiché | **Non**, justification technique d'`impossible` publiée en crypte/10. |

La fidélité crédite les **intentions entières** conservées par un refus moteur,
y compris après correction. Comme au 304, recherche de traces non certifiée et
mission en `propos` restent exclues du score de contrat des deux côtés ; montant
du prix évalué séparément. Un refus de proximité exact ne couvre pas une attente
omise : `voler/simple` compile seulement `deplacer`, `finesse` ajoute `patienter`.

| Famille (indices zéro) | Fidèles finales réf. → lot | Résultat |
|---|---:|---|
| Sensoriel, relais/1 et crypte/1 | 2 → 2 | Odeur récupérée, enregistrée et relue ; lumière conservée. |
| Son, relais/2 | 1 → 0 | Son omis puis corrigé ; approche **effort/CHA 10**, confirmation, aucune émission au tour. |
| Mémoire/description, quatre tours | 4 → 4 | Conservées ; conduite et échoppe nécessitent une reprise. |
| Recherche, relais/5 | 0 → 0 | Examen du sol, traces non certifiées des deux côtés. |
| Écoute, crypte/9 | 0 → 1 | Exécutée dès le premier candidat, deux appels, aucun faux refus. |
| Levier, crypte/10 | 1 → 0 | **Nouvelle perte** : le modèle nie l'opération disponible, répète `impossible`. |
| Passage, relais/20 | 1 → 0 | Deux `faufiler/sud` étrangers, refus de sens justifiés, puis précision moteur. |
| Coup, relais/21 | 1 → 0 | Poussée étrangère, puis improvisation refusée pour manière absente du dossier ; abandon. |
| Bien absent, relais/22 | 1 → 1 | Prendre le bien demandé ; refus de visibilité fidèle, sans substitution. |
| Attente/vol, crypte/26 | 1 → 0 | Refus de proximité exact, mais `voler/simple` perd l'attente ; revue trop permissive. |
| Prix mission, crypte/24 | 0 → 0 | Montant correct, typage de consultation non exercé. |
| Question MJ, crypte/41 | 1 → 1 | Encore parole/avis au départ ; lieu refusé, puis dialogue, **aucune parole prononcée**. |
| Questions PNJ, trois tours | 3 → 3 | Gardien conservé comme sujet libre. |
| Avis, quatre tours | 4 → 4 | Clauses et destinataires conservés. |
| Ressources/comptes/marché, sept tours | 7 → 7 | Part contre trois pièces fidèle ; refus commercial, pas abandon. |

| Famille de refus, même classement qu'au 304 | Référence → lot |
|---|---:|
| Fidélité de l'action | 1 → 5 |
| Portée | 3 → 1 |
| Visibilité/référence | 1 → 1 |
| Réexamen d'impossible | 1 → 1 |
| **Avis sur lieu inconnu** | **0 → 1** |
| Arguments d'écoute | 1 → 0 |
| Personne inconnue | 1 → 0 |

Les cinq refus de fidélité : son omis (contrôle déterministe), deux passages
étrangers, poussée étrangère, puis **faux refus de manière**. Les anciens motifs
« non admis = absent » disparaissent, sans rendre la revue juste. Paramètres
sonores, catégorie acoustique, opération incompatible et parole omise du 304
n'apparaissent plus ; une famille nouvelle suffit à faire échouer le critère.

En crypte/10, le faux manque d'opération vient d'abord de Luna ; sa justification
reste dans `retour_moteur.proposition_refusee`, puis l'audit la traite comme source
mécanique. Le joueur lit cette explication technique. Le moteur n'avait pas
établi l'absence d'opération : c'est une perte de contrat, pas un incident réseau.

**Coût** : 91 saisies, 30 tours MJ, 61 sans modèle. Appels de réponse 57 → 55,
revues d'action 15 → 21, audits narratifs 27 → 28 : total 99 → 104.
Secondes modèle/tour 9,82 → 7,71 (référence historique, aucun gain causal établi).
Compilations 36 → 37, tours repris 5 → 7 ; obstacles narratifs 9 → 6,
relances 8 → 5, replis détectés 0 → 2. Entrée JSON 21 609 → 18 786 caractères ;
requêtes complètes hors ligne à 88,7 / 87,8 % de la référence.

**Preuves** : 207 tests réussis / 211 distincts, quatre ignorés, 21 fichiers ;
aucune suite ni Luna relancée. Rejeu de sept tours archivés : charges exactes,
annotations de périmètre séparées des verdicts Luna, pas de sauvegarde intégrale
par tour. Schémas avant/après et mutualisés contrôlés sur six charges.
Ancien interprète non réintroduit ; narration, PNJ, qualifications/faits et prix
via parole gardent leurs voies et contrôles transitoires.

Bruts : `C:/Users/msics/donjon/artifacts/g1d-311/`, passe
`20261029-184942-30520/` ; `analyse-passe.json`, `familles.json`,
`familles-refus.json`, `revue-admission.json`, `preuves-pertes.json`,
`mission-jouee.json`, `manifest-bruts.json`, `tableau-tours.md` (30 tours,
cause → correction → résultat et coût). **Critères de fusion non atteints.**
