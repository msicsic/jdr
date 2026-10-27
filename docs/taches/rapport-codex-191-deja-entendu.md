# Lot 191 — Ce qui a été entendu ensemble

Branche `codex-deja-entendu`, non fusionnée ; base `integration 8a10a16`.
**Livraison partielle : l'invariant subjectif complet reste ouvert.** Aucun Luna,
deux travailleurs réduits au maximum. Bruts et sondes exclusivement dans
`C:/Users/msics/donjon/artifacts/deja-entendu-191/`.

**Correction retenue.** `social._audience_connue` photographie les auditeurs qui
saisissent les mots et ceux dont chacun connaît la présence. `faire_entendre`
et `retenir_parole` enregistrent ces audiences dans le même registre que les
confidences directes. `entendu_a` conserve plusieurs positions entendues sans
écraser la dernière position personnellement dite, ni établir leur vérité.
`deja_dit`, `_a_dire`, les nouvelles et les preuves de transmission le consultent.
`reviser_dits` rouvre les anciennes valeurs lorsqu'un changement est appris ;
une entrée créée par la seule écoute ne vaut pas conclusion personnelle.
`esprits.py` change uniquement la validation du registre, compatible avec les
anciennes sauvegardes. Aucun fichier interdit modifié.

**Cas réel.** Mine 1, départ tiré, 4 h : quinze annonces du guet sur la base,
**trois sur la branche** (227/227/229). L'ancienne capture avant 40 garde les
annonces 40/41 : elle ne possède pas les audiences enregistrées dès le début
d'une nuit neuve. Dix minutes d'un bloc ou 5 + 5 sauvegardées : monde, chronique
et mots entendus identiques ; monde/rendu final de la nuit rechargés identiques.
Les scènes du Relais contrôlent aussi constat matériel, témoin, absent arrivant
ensuite, refus d'adoption, changement de valeur, positions contraires, canal
acoustique direct et laps découpés. Les disputes restent exercées en ciblés.

**Banc retenu.** Seize nuits de branche, quatre scénarios × quatre graines,
4 h. Les seize références `4c57020` sont relues du cache, jamais recalculées.
Elles sont antérieures à la base : écarts non attribuables au seul lot, temps
non comparables. Totaux sur quatre graines, référence → branche :

| Scénario | Confidences | Constats | Avis | Avertissements redits |
|---|---:|---:|---:|---:|
| Relais | 9 → 9 | 9 → 9 | 0 → 0 | 0 → 0 |
| Mine | 127 → 81 | 80 → 56 | 0 → 0 | 4 → 2 |
| Auberge | 37 → 30 | 37 → 30 | 0 → 0 | 0 → 0 |
| Crue | 48 → 37 | 25 → 24 | 15 → 5 | 0 → 0 |

Zéro plantage/usurpation, aucune nouvelle alerte de boucle. Même `fige_presse`
au Relais/mine et `noir_long` à l'auberge ; disparition de `voir_alterne` et
`eau_longue` en crue. Aucune dispute naturelle ; deux avis adoptés contre zéro.

**Tests.** Suite unique intermédiaire : **2 299 tests, 265 fichiers, 1 572,001 s,
15 échecs, une erreur, aucun saut**. Elle ne valide pas à elle seule l'état final.
**135 ciblés finaux verts, 17 fichiers** (107 sociaux, 25 régressions, trois
empreintes) : tous les échecs intermédiaires hors les deux MiMo historiques
sont repris verts. Deux empreintes réancrées pour registre/paroles/recherches ;
plans et vues historiques conservés. Aucune seconde suite complète.

**Limite déterminante.** Le contrôle historique `_sait` de `bavarder` lit encore
le savoir de l'auditeur : « ce que le locuteur croit, jamais le savoir privé »
**n'est pas garanti**. Sa suppression et un essai de vue commune ont provoqué
des régressions de défense/trajets, puis ont été retirés, sans élargir les bornes
des tests. La suite du contrat des observations communes doit dépasser les
seules fonctions de registre autorisées dans `esprits.py` (perception et témoins
de `pnj`). Les audiences oubliées restent irrécupérables ; registre borné à
512 identités. Pertinence et constats triviaux après son propre geste restent
hors lot ; aucune garantie générale sur toute répétition ou justesse des avis.

Commit non signé : aucune clé configurée. Branche seule destinée à la revue ;
`main` et `integration` intactes.
