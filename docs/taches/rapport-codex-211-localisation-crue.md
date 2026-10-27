# Lot 211 — Localisation crue des entités mobiles

27 octobre 2026, `codex-localisation-crue`, **non fusionnée**. Départ `0b95f33`
vérifié ; reprise demandée sur **`aadab7c`**, fusion `5a97ab3`, seul conflit
documentaire. Les fichiers des autres lots sont conservés intégralement.

**Invariant.** `monde.mobile_par_nature` reconnaît personnages et objets
transportables ; `_lieu_cru` réserve le repli structurel aux installations fixes.
Une croyance reste prioritaire, absence explicite comprise. `salle_crue` suit les
porteurs/contenants par leurs croyances. Aucun savoir implicite ajouté au jeu,
aucun scénario/MJ changé. Le diff de production contre `aadab7c` ne touche que
cette fonction et la lecture commune de `monde.py` (`moteur.patch`).

**Appelants** (`aadab7c/appelants.txt`). Source commune : croyance de lieu issue
de vue, ouïe, parole ou savoir déclaré ; inventaire propre effectivement porté.

| Usage | Sans localisation |
|---|---|
| Recherche/demande/avertissement (`Vue`, `_chercher`, `_plan_prevenir`) | Parcours des lieux accessibles non cherchés en vain, inspection/appel ; indices 37/69 conservés. |
| Appels/rendez-vous (`appel`) | Contact entendu, réponse saisie, lieu/échéance mémorisés. |
| Abri/compagnie (`_plan_abri`, `_rejoindre_un_proche`) | Présence fiable et case crues requises. |
| Protégé/danger/garde (`defense`, `de_garde`, `biens`, `signes`) | Localisation crue ou souvenir localisé de secours. |
| Agendas/réclamations/propositions/échanges/avis | Destinataire/porteur cru joignable ; sommeil ou sans recours sinon. |
| Moyens/clés/lumière/refus/contenants | Croyance à chaque maillon mobile ; structure fixe, inventaire propre. |

**Preuves.** Captures 209 lues sans modification ; trois graines 2024/42/7,
instants 753/1034, six états et douze variantes rechargeables : même esprit,
l'ancien repli suit Aubin, le correctif conserve l'inconnu. Cas réel Ilse/Aubin
et Hugues/Anselme dans l'auberge ; savoir déclaré, vue/ouïe, absence, fixe/mobile,
porteur inconnu, même laps entier/découpé. Tests du monde, de `regarder` et de
`scene_percue` après recharge ; cible non perçue et intention persistée comparées.

**Banc final : 20 paires × 4 h**, référence exacte `aadab7c` calculée une fois et
cachée : **24 → 16 retours**, zéro plantage/usurpation. Moyennes sauf les retours
(sommes) ; S/F/D du lot 183, inactifs compris.

| Scénario | Retours | S/F/D avant → après | Appels/retrouvailles avant → après |
|---|---:|---|---|
| Relais | 0 → 4 | 10/4/1,563 → 11,25/3,75/1,5 | 0,75/0,25 → 0,5/0,5 |
| Mine | 1 → 1 | 22/4,25/1,607 → identique | 0,25/0,25 → identique |
| Auberge | 5 → 2 | 11,25/4/0,906 → 12/4,25/1,063 | 1,5/1 → 2/1,25 |
| Crue | 9 → 2 | 23/6,75/2,625 → 14/6,75/2 | 0,5/0,25 → 0,25/0 |
| Hameau | 9 → 7 | 29,5/7,5/2,292 → 31/8/2,542 | 1/0,5 → 2/1,25 |

Attentes de rendez-vous : zéro avant/après. Recherches du planificateur
Relais/mine/auberge/crue/hameau : 373,75/547/353/1 763,5/1 602,25 →
399,75/547/372/1 098,25/1 812 (compteur non spécifique aux personnes).
Attente urgente crue **102,5 → 178,75**, hameau **111,25 → 128,75 PNJ·min** ;
sans recours crue **27,5 → 0**.

**Validation.** Quinze ciblés verts sur la fusion ; suite finale unique :
**2 425 tests / 281 fichiers, 2 128 s, quatre échecs et une erreur bruts**.
Six reprises finales vertes corrigent l'oracle du rejeu, la contre-épreuve hors
sol et l'observation manquante du test d'abri. **Bilan consolidé : deux MiMo
préexistants, zéro erreur restante**, sans seconde suite sur cette base.
Relectures ancien/corrigé : eau verte des deux côtés après 205 ; Aubin
nourri à 4 min, formulation de vente différente ; deux rotations vers une
personne reconnue omises par l'ancien oracle du rejeu. Ces tests contrôlent
maintenant l'événement `nourri`, repas/faim et toutes les rotations d'ouïe.
Sources de scènes explicitées dans les tests ; oracle de seules
visites/diagnostics adapté, plans/monde/rendu inchangés ; borne sans surcoût,
demande pendant la ronde maintenue dans le récit.

**Réserve avant intégration.** Absence de boucle nouvelle **non validée** :
Relais 1985, deux secours interrompus ; 2024, ronde/secours d'Aubin à 194 min,
deux retours ; causalité détaillée non établie. Aucune nouvelle alerte de
répétition/alternance ; deux observations `fige_presse` (Gorm : devoir confié,
Brune : froid en attente). Engagements 196 c distincts ; aucun gain uniforme promis.

Première base archivée : banc 57 → 48, suite 2 404/13 échecs, puis 15 reprises
vertes ; seconde suite demandée après fusion. Créneau 30–45 min dépassé.
Aucun Luna, deux travailleurs
réduits au plus. Pas de clé de signature, commits non signés. Bruts :
`C:/Users/msics/donjon/artifacts/localisation-211/`, résultats finaux `aadab7c/`.
