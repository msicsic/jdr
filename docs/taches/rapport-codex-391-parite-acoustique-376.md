# Lot 391 — Parité acoustique après 376

Branche `codex-parite-acoustique`, base `integration 55c3a456`, laptop.
Bruts : `C:/Users/msics/donjon/artifacts/parite-acoustique-391/`.

**Invariant corrigé.** Les perceptions suivent chaque événement du monde,
indépendamment des frontières d'attente et des copies de transaction.
À **143408** dans la capture d'Ilse, `Monde.adopter` remplace les éléments de
la liste des bruits : le rendu du 376, fondé sur leur identité Python,
rejouait les paroles de **141120 à 143408**. `pnj._avancer` et
`Moteur._terminer_etape` reconnaissent désormais le contenu sauvegardé de
l'événement, y compris son instant et son identifiant d'émission.
Les paroles réellement distinctes restent distinctes ; aucun registre ajouté.

Dans l'autre salle, la conversation de Mathe à **1200** ne passait pas par le
relevé immédiat des perceptions. Au prochain événement (**1300**), son ton
bref avait expiré ; une coupure à 1200 le montrait. Le relevé est déplacé à
la sortie commune des branches PNJ (geste, conversation, secours), avant
l'avancée de l'horloge. Aucun cas lié au personnage, lieu ou texte.

**Empreintes historiques attribuées intégralement.** Rejeu des deux captures
480–485 sur le parent du 376 (`d1c3d1f9`), sa fusion (`69ae6101`), la base
du lot et la correction. Dans chaque monde complet, le **seul champ changé
par 376 est `/journal/96/faits`** : sons rendus successivement au lieu du
regroupement final. Mine : 8 → 14 lignes ; auberge : 2 → 7 lignes.
Visites, plans, diagnostics et les deux vues conservent leurs empreintes.
Aucun changement ultérieur de ces mondes, correction comprise.
`tests/data/parite-391-etapes.json` conserve anciens/nouveaux faits et hashes.
Le test restaure les anciens faits et exige l'ancienne empreinte exacte :
le réancrage ne masque aucun autre champ. Diff exhaustif :
`differences-captures.json`, mondes complets dans `captures-*/`.

**Vérification : 75 tests verts, huit fichiers**, zéro saut. Six fichiers
verts réutilisés ; les deux fichiers de tests ajustés ont été repris
(`tests-consolides.json`, sources et traces conservées). Les trois méthodes
du brief passent ; aucune assertion de parité ou de sécurité retirée.
Les cas source distante et capture d'Ilse comparent état complet, texte,
`regarder` et `scene_percue` après sauvegarde/rechargement ; coupures
1199/1200/1201 et 143399/143400/143407/143408/143409.
La transaction moteur unique et son journal sont également comparés aux
événements PNJ découpés/rechargés. Les seuls champs neutralisés sont ceux
du journal et des numéros d'action, comme au 376 ; `entendus` reste comparé.

**Mesure en cours.** Empreintes 2 h × Relais/mine/auberge/crue × quatre graines,
contre la base figée `55c3a456`, cache commun ; référence puis branche,
un travailleur réduit (deux avec le dernier fichier de tests). Calcul détaché,
processus confirmé actif ; fin écrite en dernier :
`C:/Users/msics/donjon/artifacts/parite-acoustique-391/fin-empreintes.json`.
Ni suite complète ni Luna. Fusion laissée au superviseur.

**Limite de contrat existante.** `entendus` décrit le dernier geste du joueur
(`docs/plan-temps.md`, « Entendu vaut pour le dernier geste »). Plusieurs
commandes distinctes le réinitialisent et ne donnent donc pas nécessairement
la même audience finale qu'une seule commande ; ce contrat reste inchangé.
La parité des perceptions est vérifiée sans exclure ce champ, à commande
unique et entre événements PNJ, pas affirmée pour cette différence de commandes.
