# Lot 325 — U-C, consentement du texte libre

29 octobre 2026. Branche `codex-uc-consentement`, **non fusionnée**, base
`origin/codex-up-recapitulatif`, commit `865aff3`. Aucune fusion d'integration.

`donjon/consentement.py` prépare une réponse entière sur copie : transactions
ordonnées, admissions et plan moteur. La classification commune porte sur les
effets typés de réussite, d'échec et d'échec critique, et descend dans les
sous-plans. Les effets usuels légers sont explicités ; un nouvel effet reste
lourd par défaut. Les contenus de parole et accords sont soumis à la même
décision ; ils ne passent plus avant l'aperçu. Une seule étape lourde retient
toute la composition, y compris une transaction accompagnée d'une action.

`jeu.py` montre la fiche U-P avant tout effet retenu. `annuler` sauvegarde son
historique sans publier la copie. `tenter` reprépare sur l'état courant sans
modèle : différence d'état, de plan, de destinataires ou de rapport impose
un nouvel aperçu ; une proposition devenue impossible reste visible comme
indisponible et ne s'exécute pas. Le contrôle détecte aussi une mutation sans
incrément de révision. Les rendus et paroles admises sont sauvegardés avant
affichage. Après changement du monde, une ancienne narration n'est pas
réutilisée : les faits publics recalculés sont rendus par le moteur. Les actes
légers gardent l'exécution immédiate et leur récapitulatif après résultat ;
clics, menus et commandes structurées gardent leurs contrôles existants.

## Vérification

MJ simulé sans réseau : paiement direct, offre réelle du corpus G1/U-P, avis,
enfermement de Rémy à la mine, fermeture puis verrouillage (une seule étape
lourde), et offre suivie d'un dépôt léger. Console, pont web et vraie TUI :
aperçu, annulation, nouvelle saisie, confirmation, ressources/portes/objets,
paroles entendues et monde complet, sauvegarde et rendu après recharge.
Prix changé et destinataire parti sans changement de révision demandent un
nouvel aperçu ; contre-épreuves acte léger et consommation par clic/menu.
Les oracles de texte U-P restent inchangés ; ses parcours offre/avis envoient
désormais `tenter`. Sa sonde de péremption vise le monde vivant puisque la
préparation travaille désormais sur copie.

**28 tests TUI préexistants inchangés verts, 306,864 s**, première passe.
La première passe des nouveaux tests conserve ses **13 échecs de sous-cas** :
attente après fermeture de leur TUI et fixtures invalides (clé hors de
portée, geste direct inexistant, nom inconnu d'Aubin), corrigés sans toucher
les gardes du jeu. La seconde passe valide les **18 parcours lourds**, mais
garde deux échecs de synchronisation TUI et trois erreurs de compteur de
fixture (`portions`, pas `charges`). **Les trois méthodes corrigées repassent
vertes, 20,223 s** ; le rejet d'une ancienne réplique après revalidation est
également vert, **3,565 s**. Aucun oracle existant n'est affaibli.
**Vérification finale des huit méthodes U-C et de la régression ciblée en cours** :
`C:/Users/msics/donjon/artifacts/uc-325/fin.json` fera foi, y compris en échec.
Mesures saisie→aperçu et confirmation→effet dans `mesures-finales.jsonl` ;
temps humain simulé séparé (zéro), compteur d'appels après confirmation.
Aucune mesure ne prétend représenter la latence de Luna réelle.

## Limites et intégration

La revalidation est conservatrice : tout changement d'état hors historique
d'affichage peut redemander un aperçu, même sans conséquence sur l'acte.
Une fiche enregistrée se relit après recharge ; elle n'est pas réactivée
comme consentement en attente. Aucune garantie de fidélité parfaite au
français, aucune revue ni contre-revue retirée, aucun schéma ou prompt Luna
modifié. Pas de Luna, banc ou suite complète. Deux processus Python au plus,
priorité réduite. Recouvrement avec **321 et 323 : `jeu.py`** ; ni `tui.py`,
ni `rendu.py`, ni le pont web n'ont été modifiés.
