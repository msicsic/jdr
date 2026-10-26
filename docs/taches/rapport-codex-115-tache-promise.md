# Lot 115 — Une tâche promise en contrepartie de recours

Branche `codex-tache-promise`, **non fusionnée**, base **6910d8e**. Code signé
SSH **d3567d8**, **ee0ab0c**, signatures vérifiées. Aucun Luna, scénario,
choix des besoins ou recherche modifiés.

**Invariant et fonctions.** Après les moyens ordinaires, `pnj_propositions.recours`
peut offrir une tâche typée. `propositions.taches_crues` utilise une condition
entendue ou un état connu à réparer sur un bien du destinataire ou commun dans
sa salle crue, sans lire ses buts privés. Un seul candidat est devisé par recours,
même avec deux déclencheurs ; le devis est partagé avec les contrôles de coût
et de refus. Demande, achat, délégation futurs et faute interdisent la promesse.
Même jugement inversé et classement coût/chance que les biens. Un refus ancien
ne remplace plus un nouveau plan ordinaire ni une demande dans son préfixe.

`echanges.proposer` revalide l'autonomie avant transfert ; l'accord remet la part
et inscrit une parole datée dans `agendas`. Planification, tenue, empêchement,
annonce et relations suivent le cycle existant. Refus de tâche et anciens plans
rechargés sont contrôlés avant parole. Aucun nom de scénario dans le moteur.

**Preuves.** Brune/Gorm : part contre recharge effective avec son propre bois,
vue datée de Gorm et engagement tenu appris. Joss/Odile : verrouillage du
garde-manger contre un repas. Monde, journal moteur et esprits rechargés ;
même laps continu/découpé. Rupture annoncée et confiance diminuée, impossibilité,
fourniture d'un tiers, refus persistant et devis unique vérifiés.

**Tests.** Suite complète unique : **2 033 tests, 16 ignorés, 219 fichiers,
2 266,85 s**, trois échecs et deux erreurs dans quatre fichiers. Rejeux : la
promesse d'allumer la torche obtient un repas sans chercher les crochets,
révèle l'embuscade, ou permet de rendre l'outil après la stratégie réussie.
Ces tests isolent maintenant leur sujet avec la torche déjà allumée. Mine :
Bram conscient, seul, sécurité 60,293 < seuil d'appel 95 ; le test n'exige plus
l'arrivée contingente d'un compagnon avant ce seuil. Reprises : **101 tests,
152,26 s**, une dernière attente de première offre corrigée en borne de
non-répétition, puis **13 tests verts en 20,04 s**. **Bilan consolidé vert**,
un ignoré dans les reprises, aucune seconde suite. Neuf tests nouveaux.

**Banc final : 4 h × quatre scénarios × quatre graines**, 16 références relues,
16 nuits de branche. Aucun plantage, violation, usurpation ou nouveau code
d'audit ; **10/16 états identiques**. Propositions écartées au profit des moyens
ordinaires. Aucune tâche naturelle offerte/acceptée/tenue/rompue : **0/0/0/0**,
comme la référence ; exécution démontrée par les parcours ciblés et les rejeux.

| Scénario | Propositions/acceptées, base → branche | CPU branche/nuit |
| --- | --- | --- |
| Relais | 0/0 → 0/0 | 6,60 s |
| Mine | 13/1 → 10/1 | 20,35 s |
| Auberge | 3/1 → 3/1 | 16,45 s |
| Crue | 9/0 → 5/0 | 22,69 s |

Mine 2024 : répétition et avertissement redit disparaissent ; observation
`fige_presse` supplémentaire pour Rémy, **230 min de devoir déjà satisfait**.
Le devoir satisfait n'engendre pas de boucle active. Autres codes inchangés ;
aucune offre identique à moins de 60 min, base comme branche.

**Limites.** **Critère CPU au bruit près non démontré** : références cachées
mesurées sous une autre charge. Avant le renforcement de priorité, le premier
banc montrait +15,5 % auberge et +38,9 % crue ; profil crue 2024 : recours
8,92 s sur 70,64 s instrumentées, devis dominants. Aucun gain causal revendiqué.
Un candidat impossible peut masquer un autre service réalisable. Dépôt et repas
peuvent reprendre une condition entendue ; aucun lieu souhaité n'est deviné.
Verrouillage ponctuel, aucune garde permanente ni tarif en pièces nouveau.
Le devis reste cru, les moyens réels sont revalidés. Créneau dépassé par les
vérifications et reprises. Bruts : `artifacts/tache-115/` ; lourd à l'intégration.
