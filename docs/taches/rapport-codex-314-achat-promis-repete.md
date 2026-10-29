# Lot 314 — achat promis après annulation

Branche `codex-achat-promis`, base `integration c4f6d46`.
**Correction et épreuves nouvelles terminées ; vérification élargie en attente.**

**Cause et invariant.** Une livraison annulée reste dans `agendas.en_cours`
jusqu'à l'annonce de son abandon. `_remettre_part` prenait cette inscription
pour une livraison encore due et retournait `promis`. `echanges.executer`
publiait alors un accord et effaçait les refus du demandeur ; celui-ci
rechoisissait le même achat, sans paiement ni progrès. La voie commune de
livraison de parts transmet désormais la cause d'annulation enregistrée.
L'exécution mémorise ce refus selon ses moyens ou son échéance habituels.
Pas de délai ajouté, de nouvelle mémoire, de règle de scénario ni de
modification des données du hameau ; réclamations du lot 315 inchangées.

**Preuve réelle.** Capture 306/reprise-309 `0038-23110-aubin`, rechargée à
38 min, avant t=36582, conservée sans retouche dans les tests. Rejeu de
30 min avec la fonction de base chargée en mémoire : **28 achats promis**
entre t=36582 et 39282, aucun paiement. Même capture corrigée : **un refus
à t=36477, zéro achat**, aucun nouveau prélèvement ou paiement ; annulation
ensuite annoncée et retirée. Le monde entier est identique entre un laps
de 30 min et trente laps de 1 min, recharges intermédiaires comprises.
Les observations visibles ont la même multiplicité ; leur ordre varie avec
le regroupement du bilan des présences à la fin de chaque action joueur.
Monde, rendu et scène identiques avant/après sauvegarde et recharge.

**Autre scénario.** Auberge : Odile promet une part d'huile à Joss,
constate la perte de la part réservée, puis annule par le cycle commun.
Un achat préparé reçoit `impossible`, retenu et non répété durant cinq
minutes ; ni argent, ni charge supplémentaire consommée, ni source allumée.
Laps entier/découpé, monde/rendu/scène rechargés contrôlés aussi. Les deux
causes d'annulation, demande gratuite/achat, livraison active puis soldée
sont couvertes. **Quatre nouveaux tests verts, 24,699 s**, un travailleur
réduit. La sonde de reproduction utilise les instants, car la chronique
est bornée ; ses premiers résultats vides ne sont pas une preuve retenue.

**À terminer avant clôture.** Fichiers voisins des échanges et agendas,
empreintes 2 h Relais/mine/auberge/crue × quatre graines contre `c4f6d46`,
puis banc hameau 4 h × quatre graines dans un worktree temporaire fusionnant
le 306. Référence hameau : quatre nuits déjà archivées du 306, sans relance.
Deux travailleurs au plus, priorité réduite, séquences successives.
Ni Luna ni suite complète. Les résultats détaillés et le fichier de fin
seront dans `C:/Users/msics/donjon/artifacts/achat-314/fin.json`.

**Limites.** Ce lot corrige la confirmation abusive d'une livraison de
part annulée ; il ne certifie pas l'absence universelle de répétition de
toute parole ni les autres avis du 306. Un refus connu suit le mécanisme
commun existant de réévaluation ; une nouvelle demande explicite après
clôture de l'ancien engagement peut établir un nouvel accord.
