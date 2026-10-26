# Lot 144 — A4a partiel : activation et informer

Branche `codex-agendas-a4a`, non fusionnée ; base voulue `8ec3ace` du lot 140.
Code `36d2b82`. Intégration et fichiers MJ réservés intacts ; aucun Luna.

## Invariant et réalisation

Un projet persiste ; état, origine et cause sont sauvegardés, jamais score ni plan.
`agendas.actualiser` active une fois et limite à trois actifs. Accès centralisés,
lectures copiées, garde AST verte ; `esprits` accepte le champ facultatif sans
migration des PNJ sans déclaration. `informer` transmet une affirmation déjà crue
ou un avis de menace existant. `planifier` choisit sur les routes crues, passe une
condition de salle à `chercher` avec `endurer` (`_endure`), puis emploie la parole
commune d’`echanges`/`social`, réception et dispute comprises. La fin exige une
`transmission_attestee` : un registre plein ne prouve pas une parole. Gorm reçoit
l’objectif d’informer Ilse et Brune, en données seulement.

`_candidats` compare poids courant (valeurs, situation, affection, échéance) et besoins ;
désespoir, alarme et eau précèdent. Continuité selon VOL, INERTIE pour le besoin poursuivi.
Une croyance nouvelle autorise un essai ; seul un plan admissible réveille l’agenda.
Une nouvelle date d’observation seule ne suffit pas.

## Vérifications et mesures

Deux calculs réduits au plus. Après refus d’accès aux temporaires dans le bac à sable,
les tests ont été autorisés hors bac à sable. Bruts : `artifacts/agendas-144/`.

- Suite complète unique : **2 105 tests, 231 fichiers, 1 169,75 s**, deux échecs MiMo
  historiques `6 != 5`, zéro erreur. **40 ciblés consolidés verts**, dont six d’activation :
  Gorm prévient deux personnes, autre parole, monde/ouïe/rendu rechargés, laps entier et
  découpé identiques, sommeil/réveil, désespoir, plafond et registre plein. Deux nouveaux
  tests sont repris hors du compte de la suite ; un placement de test hors sol corrigé.
- Empreintes 2 h Relais/mine/auberge × quatre graines : **12/12 identiques**, chronique,
  mesures et état complet. Douze références calculées une fois puis cachées.
- Le premier banc crue révélait neuf alertes de réveil répété. Cycle commun corrigé,
  gardes désespérées prioritaires ; **11 puis 10 ciblés verts** (oracle A0 compris),
  sans seconde suite. Branche seule rejouée, quatre références cachées : zéro répétition
  nouvelle, plantage/usurpation/violation ; mêmes constats `voir_alterne`, `eau_longue`.
- Crue 4 h × quatre graines : attente urgente **22,5 → 20 min**, eau **123,75 → 128,75 min**,
  maximum de passages horaires **17,5 → 13,25**, au sec final **3,5 → 4 PNJ** en moyenne.
  Ilse/Brune à la galerie à 4 h **1/8 → 3/8** ; arrivée avant l’eau non prouvée.
  Information atteinte sur 1985 à 144 min ; sommeil sans menace crue sur 7/42/2024.
- `mesure_cout.py`, crue 1985 fixe, 4 h, base puis branche : recherches **1 475 → 1 459**,
  neuves **1 195 → 1 089**, nœuds **101 145 → 89 838** ; CPU indicatif **23,05 → 20,08 s**.
  Nuits différentes, poste partagé : aucun surcoût isolé ni gain CPU garanti.

Les empreintes hors crue précèdent la reprise finale, limitée aux porteurs d’agendas.
Aucune référence rejouée.

## Limites et livraison

**A4 et l’évacuation générale non acquis.** Restent `amener`, nouvelles événementielles,
impossibilité crue, manières générales, portée vocale dans le graphe (revalidée à
l’exécution), réveil relationnel, borne d’une recherche supplémentaire par choix et
conversion des engagements. Puis `garder`/`protéger`, s’interposer et hystérésis générale
remplaçant `retenu`. Aucune clé de signature configurée : commits non signés, branche
poussée seulement, sans fusion ni changement de `main`.
