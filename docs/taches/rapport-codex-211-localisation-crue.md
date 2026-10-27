# Lot 211 — Localisation crue des entités mobiles

27 octobre 2026, branche `codex-localisation-crue`, **non fusionnée**, base
`0b95f3373df898f73f443104015e976271808114`, commit requis présent.

**Invariant.** Une position cachée de personnage ne complète jamais une croyance
absente. `monde.mobile_par_nature` reconnaît les personnages indépendamment du
drapeau `mobile`, et les objets transportables par ce drapeau. `_lieu_cru`
réserve désormais son repli structurel aux objets fixes. Les croyances existantes
restent prioritaires, y compris une absence explicite ; `salle_crue` suit les
contenants et porteurs par leurs localisations crues. Aucun scénario, savoir
initial implicite, prompt ou fichier interdit modifié.

**Appelants.** Sites exhaustifs : `appelants.txt`. Source commune :
`croyances[sujet].lieu` (vue, ouïe, parole, savoir déclaré), inventaire propre
effectivement porté. Aucun savoir fabriqué pour préserver l'ancien comportement.

| Usage | Source et conduite sans localisation |
|---|---|
| Recherche/avertissement/demande (`Vue`, `_chercher`, `_plan_prevenir`) | Dernier lieu cru ; sinon lieux accessibles non cherchés en vain, inspection/appel ; indices 37/69 conservés. |
| Appels/rendez-vous (`appel`) | Contact entendu, réponse saisie, lieu/échéance mémorisés dans `rejoindre`/`rejoint`. |
| Abri/compagnie (`_plan_abri`, `_rejoindre_un_proche`) | Présence fiable et case crues ; inconnue ne crée plus d'abri. |
| Protégé/danger/garde (`defense`, `de_garde`, `biens`, `signes`) | Localisation crue ou souvenir localisé de secours existant. |
| Agendas/propositions/échanges/avis | Destinataire cru joignable, lieu entendu, condition explicite ; sommeil/sans recours sinon. |
| Moyens/clés/lumière/refus/contenants | Croyance à chaque maillon mobile ; structure fixe, inventaire propre. |

**Preuves.** Les captures du lot 209 sont lues sans modification. Rejeu des trois
graines 2024/42/7 jusqu'aux instants **753 et 1034** : six états, douze variantes
rechargeables, même esprit ; l'ancien repli suit Aubin, le correctif rend toujours
la position inconnue. Les trois retours précoces disparaissent du banc. Tests du cas
réel Ilse/Aubin et d'Hugues/Anselme dans l'auberge : déplacer seulement la cible
cachée conserve l'esprit et le plan ; savoir déclaré, vue, ouïe, absence,
installation fixe, objet mobile et porteur inconnu couverts. Monde, `regarder`
et `scene_percue` identiques après sauvegarde ; deux minutes d'un bloc ou en
deux tranches identiques dans les deux scènes. **16 tests ciblés verts**.

**Banc 4 h, vingt nuits.** Zéro plantage/usurpation. Moyennes par nuit sauf les
retours (somme des quatre graines) ; richesse S/F/D du lot 183, inactifs compris.

| Scénario | Retours | S/F/D avant → après | Appels / retrouvailles avant → après |
|---|---:|---|---|
| Relais | 0 → 4 | 11,25/4,5/1,813 → 11,25/3,75/1,5 | 0,75/0,5 → 0,5/0,5 |
| Mine | 1 → 1 | 21,5/4,25/1,643 → identique | 0,25/0,25 → identique |
| Auberge | 5 → 2 | 11,25/4/0,906 → 12/4,25/1,063 | 1,5/1 → 2/1,25 |
| Crue | 27 → 22 | 23,75/6,75/2,813 → 16,5/7/2,5 | 2,25/1,5 → 1,25/0,5 |
| Hameau | 24 → 19 | 27,25/6,75/2,333 → 32,75/7,75/2,542 | 1/0,5 → 2,25/1,75 |

Total **57 → 48**. Attentes de rendez-vous : crue 1,25 → 1,25 min,
hameau 1,25 → 0, autres zéro ; aucune attente vaine ni parole rompue.
Recherches du planificateur Relais/mine/auberge/crue/hameau :
406,5/571,25/353/1 654,5/1 159 → 409,75/571,25/372/1 008,75/1 760
(ce compteur ne distingue pas la recherche d'une personne).
**Aucune boucle nouvelle : critère non validé.** Relais 1985 : deux interruptions
de secours ; Relais 2024 : ronde/secours d'Aubin à 194 min, deux retours.
Crue 7 : Brune active/endort son agenda huit fois (deux alertes de répétition
nouvelles) ; les retours d'abri tardifs remplacent le retour précoce d'Ilse.
Hameau 42 : 1 → 7 retours. Relais 7 : marchand sans but 150 min, devoir confié
(observation `fige_presse`, pas preuve d'une boucle). Aucune alerte masquée,
attribution causale détaillée de ces nouveaux parcours non établie.

**Suite complète unique : en cours.**

Référence : vingt nuits archivées du lot 209 (`78ba505`), code du jeu identique
à `0b95f33` (différence limitée à quatre documents). Un lancement initial du
comparateur sur `0b95f33`, sans référence déjà cachée pour ce commit, a été
arrêté ; seules les archives existantes servent à la comparaison finale.

**Limites, réserve avant intégration.** Engagements (196 c), périls/abris (205)
et restauration des charges restent ouverts ; les retours sont des alertes,
pas autant de défauts certifiés. Aucun Luna. Aucune clé de signature configurée :
commit non signé.
Au plus deux travailleurs de calcul à priorité réduite. Bruts exclusivement
`C:/Users/msics/donjon/artifacts/localisation-211/`.
