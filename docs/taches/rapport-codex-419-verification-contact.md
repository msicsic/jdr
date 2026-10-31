# Lot 419 — le contact prépare le moyen et son but

31 octobre 2026, laptop · `codex-verification-contact` · base **`8c5eaaa7`**.
Moteur `b51cf8f8`, livraison mesurée **`4fc57520`**. **Lot clos, non validé pour
fusion : une régression de service et une hausse d'appels. Aucun calcul restant.**
Bruts : `C:/Users/msics/donjon/artifacts/verification-contact-419/`.

**Contrat et code.** `planification.preparer_contact` conserve le geste derrière
sa vérification ; seul le préfixe s'exécute, puis le constat impose de recompiler.
Les propositions lisent cette provenance pour préserver le recours licite.
`_appeler` éprouve le dernier repère inaccessible sans en faire une présence ;
consommation du 374 inchangée. La parole d'agenda utilise le terminal du graphe.
Une localisation manquante n'efface plus l'aide attendue ; servir exige d'abord
un moyen matériel admissible. `echanges.executer` sépare provenance et termes
prononcés, sans polluer l'accord sauvegardé. Aucun registre ou prompt ajouté ;
`memoire.py`, `deliberation.py`, méthodes des familles R et E inchangés.

**Treize méthodes du brief : douze vertes, une ouverte.** Attribution antérieure :
[414](rapport-codex-414-suite-4539dd68.md) ; captures et preuves : `diagnostic/`.

| Méthodes (fichiers sans `test_`) | Classement et preuve |
|---|---|
| `recours_prioritaire` (deux aides) | Défaut corrigé : source portée non localisée ; attente adoptée et monde/rendu entier ou découpé rétablis. |
| `contre_offre`, `offre_sensee` | Défauts corrigés : faux préfixe malgré repas épuisé ; offre admissible perdue avec le contact. |
| `agendas_activation`, `propositions_redites` | Défauts corrigés : parole derrière contact, appel du repère inaccessible ; oracles de perception et durée adaptés au 374. |
| `achat_promis_annule` | Date fausse : enquête sur Gorm à 60, réponse démentie à 67, refus à 40267 ; aucun paiement ni nouvel accord. |
| `gardien_detresse` | Compteur faux : cri 277200 évincé des 300 entrées ; souvenir 462 conservé, aucun cri nouveau. |
| `empathie_peur` : Gorm | Attente fausse : vérification de Mael puis attente d'aide ; ronde encore exécutée à 208. |
| `signalements` : Hugues, Anselme | Prémisses fausses : nouveau secours d'empathie isolé du devoir ; question positive à 571 remplaçant l'appel, but du poêle conservé. |
| `eau` | Vitesse attendue fausse : abri atteint dès 31 après un seul relevé ; refuge sec et absence de pente inventée vérifiés. |
| `dynamique_besoins` : ballot | **Ouvert, oracle intact** : à 120, Lucien garde la chambre, ballot toujours au coffre, piste consommée à 93. Quelle preuve autoriserait le vol attendu à 107–110 avant d'exiger la recherche du porteur ? Ne pas contourner le 417. |

**Tests : 22 fichiers, 203 méthodes, 197 vertes, six rouges** (sept entrées
d'échec/erreur, dont deux sous-cas d'une même méthode). Quatre nouveaux tests
verts : Rémy/Bram, deux contacts présents/absents rechargés, recours conditionnel,
termes d'aide. Consolidation dans `fin.json`, frontière et fichiers finaux.

Cinq méthodes rouges préexistent : deux de `dynamique_besoins` (lanterne,
ballot), `empathie_peur` (démenti, suffixe supposé), `gardien_detresse`
(`demander_un_moyen_pour_un_autre_besoin`). Les deux égalités de contenu refusent
la provenance descriptive du 417 ; oracles laissés intacts. Preuves :
`reconnaissance/`, 414, et `attribution-base.stdout.json` sur la base exacte.

**Régression nouvelle :** `service_rejoindre...capture_reelle_289_tilo_mathurine`
est verte sur `8c5eaaa7`, rouge ici. Tilo porte `marmite_1_1`, disponible ;
planifier ce service retrouve Mathurine, mais reprendre le but adopté
`marmite_1` laisse un plan vide. Le retrait de l'anticipation du contact dans
`_pulsion` perd donc le raccord entre lot et part déjà reçue. À corriger par le
contrat commun de reprise des moyens, sans exception Tilo ou marmite.

**Banc achevé : 24 nuits jouées, 4 h × quatre graines × trois scénarios** ;
référence puis branche, cache alimenté, zéro plantage. Deux travailleurs réduits
après le calcul 416 ; aucun temps CPU comparé, aucune nuit relancée.

| Scénario | Appels base → branche | Retours suspects certifiés |
|---|---:|---:|
| Auberge | 13 → 13 | 0 → 0 |
| Mine | 5 → 4 | 1 → 0 |
| Crue | **42 → 47** | 0 → 0 |

**Critère de non-hausse non atteint.** Crue, graines 1985/7/42/2024 : appels
5→6, 10→7, 18→16, **9→18**. Le dernier cas concentre la hausse : Brune appelle
Ilse à 2172/2558/2783/3246, puis plusieurs contacts d'Aubin et Gorm suivent.
La chronique seule ne prouve pas une nouvelle hypothèse avant chaque appel ;
aucune répétition n'est reclassée comme légitime. `analyse-finale.json` conserve
les appels par nuit/acteur et l'attribution des tests ; `fin.json` reste
**`termine: true, succes: false`**. Pas de garantie générale de l'invariant ni de
non-régression. Pas de suite complète ni Luna ; fusion déconseillée en l'état.
