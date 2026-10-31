# Lot 434 — K2, assistance de Luna à la négociation

Branche `codex-k2-assistance-luna`, base `integration` **`364e8722`**.
**Terminé, non fusionné** ; code `7f59f07d`, clôture après vérification et passe Luna.

**Invariant.** Une aide demandée produit au plus deux alternatives typées,
admises sur copie avant affichage, puis sélectionnées dans K1. Aucun paiement,
engagement ni jet social avant la soumission ; le PNJ garde son verdict.

**Réalisation.** `compilation.py` étend le mode `accord` avec la charge
`obstacle/alternatives`. `negociation.py` utilise le catalogue public K1,
transmis par `mj.py` avec sa provenance, sans dossier mental privé.
Chaque candidat passe par `parole_accord` puis `echanges.candidat_proposition`,
étendu aux deux termes : droits, fonds, disponibilité, doublons, livraison,
devis du PNJ et limites temporelles communes. La possession actuelle exige
un bien visible ; sinon seule sa preuve mémorisée est utilisée.
Une clause inconnue écarte le candidat entier ; un obstacle déclaré arrête
toutes les alternatives. Les durées typées passent par `compiler_limites`.
Les libellés viennent du moteur. Console, TUI et web réutilisent K1 ; le web
affiche aussi les suggestions d’un brouillon vide. Aucun routage lexical,
registre d’esprit ou mécanisme social ajouté ; aucun audit retiré.

**Tests.** **75 tests distincts : 74 réussis, 1 ignoré, zéro échec/erreur.**
Le test ignoré dépend de `jsonschema`, facultatif. K0/K1/E5/E6/propositions/
projection : 63 tests en 546,3 s, incluant 4 K2 intermédiaires ; reprise finale
K2 (5) et raccord libre (11) : 16 tests en 144,4 s. Le décompte distinct
remplace les 4 intermédiaires par les 5 finaux.
Aubin/planches contre tâche et Odile/huile contre lanterne : vrais callbacks
web, éditeur terminal prérempli, termes soumis, accords acceptés, état et vues
identiques après recharge. Autres preuves : candidats refusés jamais affichés,
fonds, références privées, possession sans preuve, clauses inconnues, obstacle,
déduplication, plafond de deux, limite relative puis instant exact et contexte
inchangé quand un besoin privé varie. `compileall`, `--help` du banc et
`git diff --check` réussis. Deux travailleurs au plus, priorité réduite ;
ni suite complète ni banc PNJ.

**Luna : une passe sur copies, référence K0 sur les mêmes scènes.**

| Scène | Alternatives hors K0 admises | Acceptées, première soumise |
|---|---:|---:|
| Aubin : planches contre déplacement de cloche ou torche | 2 | 1, cloche |
| Odile : huile contre lanterne ou déplacement de lanterne | 2 | 1, lanterne |
| Brune avant la crue, payé seulement en cas de succès | 0 | refus `reglement_conditionnel` |

**Deux alternatives utiles hors K0 confirmées**, deux autres non soumises.
Monde inchangé avant sélection ; état et vues identiques après les deux
soumissions et recharges. Compilation : 8,954 / 6,723 / 4,432 s, sans comparaison
de vitesse. **Un appel jusqu’à chaque première offre utile, reconstitué** :
le compteur initial affichait zéro car `journal_complet` était désactivé.
Chaque fil contient une seule interprétation en mode accord, sans prose,
correction ni reprise ; ce chemin ne fait aucune revue supplémentaire.
L’analyse séparée conserve cette limite ; journal complet désormais activé.
Le premier lancement avait échoué avant appel (`tools/tests.py` masquait
`tests/`) ; import corrigé. Aucun rejeu de la passe.

**Limites.** Détecter une clause inexprimable dans tout français libre reste
sémantique ; la validité typée ne prouve pas la fidélité. Le joueur contrôle
les deux termes dans K1. Une tâche de Corvus reste une promesse, sans plan
autonome ni garantie de réussite. Admission et utilité privée sont distinctes.

**Bruts.** `C:/Users/msics/donjon/artifacts/k2-assistance-434/` :
`verification.json`, `final-cibles.json`, `luna/bilan.json`, `luna/analyse.json`,
trois fils, copies avant/après, commandes et `fin.json` de clôture.
Branche poussée ; aucun calcul en cours. Fusion et suite complète au superviseur.
