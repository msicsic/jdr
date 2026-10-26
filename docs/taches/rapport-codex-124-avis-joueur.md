# Lot 124 — Avis typé du joueur

Base `85b9204`, branche `codex-avis-joueur`, **non fusionnée**. Aucun changement
de `main`, d'`integration`, des scénarios, du modèle, de `pnj_propositions.py`,
d'`echanges.py` ou de `planification.py`. Aucune clé de signature Git configurée
sur ce poste (`user.signingkey`, `commit.gpgsign` et `gpg.format` absents).

**Contrat réalisé côté moteur.** `paroles` ajoute `avis` dans l'union du schéma,
le sens partagé et la carte des opérations : salle publique connue, prédicat
`menace`, valeur `oui|non`. Trois refus séparés avec `attendu`, avant effets.
`social.avis_exprime` distingue la position exprimée de ses preuves ; la conviction
vient de `prevision_propre`, minimum deviné 0,4 sans estimation. Les observations
d'eau de Corvus sont mémorisées par `spatial.memoriser`, dans
`connaissances_joueur`, et utilisent les mêmes repères et estimation que les PNJ.
Les prévisions qualitatives reçues ne fabriquent aucune mesure : menace minimale
positive dans `eau.attendue`, sans inventer de noyade ni effacer une profondeur vue.

L'émission photographie les preuves avant réception, puis auditeurs et témoins
passent par `recevoir_prevision`, confiance et affection envers Corvus comprises.
La dispute du lot 121 utilise l'ouïe commune (`saisit`, joueur compris), les prises
de parti et le désaveu public ; le moteur ne prononce aucune réplique supplémentaire
pour Corvus et ne choisit pas son parti. Le registre conserve aussi les partis pris
qu'il a entendus, pour ne pas rouvrir le même épisode après recharge.

**Preuves.** 37 tests ciblés verts (quatre fichiers), dont sept nouveaux : conduite
basse/Gorm et galerie/Ilse, avis positif/négatif, conviction minimale/étayée,
observations réelles, absence de lecture du pic caché, refus atomiques, témoins,
partis pris et dispute perdue, non-répétition, cantonade, chuchotement, console/MJ
simulé. Monde, paroles et rendu rechargés contrôlés. Un huitième test exerce ensuite
Gorm observant réellement la décrue, puis contredisant la menace de la galerie.
Suite complète unique à deux processus réduits : **2 064 tests, 223 fichiers,
1 009,24 s, cinq échecs, zéro erreur ou ignoré**. Trois échecs du fil historique N3
résolus en ajoutant uniquement `avis:false` à ses cartes d'opérations ; mots,
verdicts et effets historiques conservés. Reprise ciblée : **24 tests, 16,04 s,
deux échecs MiMo restants** (22 verts, dont les huit nouveaux). Ces deux échecs de
comptage d'appels (6 au lieu de 5, atelier) sont reproduits identiquement sur
l'archive isolée de `85b9204` : 13 tests, deux échecs, 10,61 s. Ils préexistent au lot ;
aucune seconde suite ni modification du fournisseur. Bilan non entièrement vert.
Banc rapide de branche : **4 h × crue/Relais × quatre graines**, un processus réduit,
huit nuits terminées. Aucun rejeu de référence ni comparaison de temps sous charge.
Analyse des seules chroniques : aucun signalement, 36 avis de PNJ en crue, zéro
adoption ; aucun avis au Relais ; au plus 28 passages/h et une bascule matérielle.
Ce banc ne comporte pas les relevés d'un audit long et ne prouve pas l'absence de tout défaut.
Bruts : `artifacts/avis-joueur-124/`.

**Luna : échec du critère de typage.** Une seule passe, copie de scène d'auteur
`tests/data/avis-joueur-124.json.gz`, trois saisies dans `bancs/avis-joueur.json`.
**9 appels, 3 par tour, 13,5 s/tour**, zéro refus affiché, repli, erreur, mention
sans fondement ou erreur de recharge. Mais **0/3 `avis`, 3/3 `propos`**, du premier
coup sans correction ; aucun avis reçu ni dispute par ce parcours. Les instructions
et schémas comportaient bien `avis`. `MJOpenAI._verifier_fidelite_parole` dispense
de revue les mots exacts déclarés sans opération : l'omission sémantique passe ce
raccourci commun. Aucun mot-clé, exception d'eau ou instruction supplémentaire à Luna
n'a été ajouté pour masquer cet échec. Pas de seconde passe ni élargissement du lot.

**Limites et décision.** Le contrat typé est livré et vérifié ; l'invariant depuis
la saisie libre **n'est pas garanti**. Cette branche n'est donc **pas fusionnable
comme réalisation achevée de 3f**. La suite doit traiter le contrat commun de couverture
des paroles et son raccourci, avec mesure de son coût ; les autres prédicats restent
hors périmètre. Les souvenirs antérieurs d'eau du joueur ne sont pas reconstruits.
