# Lot 335 — protéger à portée de voix

Branche `codex-suivi-vocal`, **non fusionnée**, base `origin/integration 9237e14`.
**Lot terminé**, code/tests `6eaf80b`, branche poussée vers origin.
Bruts : `C:/Users/msics/donjon/artifacts/vocal-335/verification/`.

**Invariant.** L'agenda `protéger` réutilise le séjour `rester` du lot 266,
avec une portée vocale typée. `planification.proximite` est commun aux deux
portées. `proximite_vocale.arrivees` calcule les arrivées par `ouie.propager`
et `parvenu` : voix ordinaire, atténuation par distance, ouvertures et portes
crues. Seule l'oreille propre intervient, sans lecture de l'oreille, du repos,
du trajet ou de la position privés du protégé. Le terminal vise les mots
audibles par le protecteur ; il ne garantit pas l'audition réciproque d'un
protégé dont l'état auditif est inconnu.

Le devis mesure l'approche aux mêmes arrivées dans `trajet_estime`, puis
`pnj._approcher` emprunte la marche commune, ses obstacles et ses tarifs.
La place déjà admissible est conservée ; les pas privés du protégé ne
déplacent pas sa position crue. L'écoute ne fait pas pivoter vers une cible
non perçue. Sans lieu connu, inspection/appel/question viennent de la recherche
commune ; une salle connue sans case exige une inspection. Leur coût n'est
pas gratuit. Les lectures acoustiques propres sont ajoutées à `_entrees` ;
lieux, cases, portes crues et géométrie étaient déjà couverts.

`agendas._prochain_sous_but` active le suivi lorsqu'aucun poste
d'interposition n'est proposé. Un recours impossible peut encore dormir pour
sa cause commune ; la raison « suivi vocal non pris en charge » disparaît.
Interposition, échelle des paliers, secours et fins sur mort/départ crus
gardent leurs contrats. Aucun agenda historique ajouté aux scénarios.
Le rendu dit « reste à l'écoute », sans affirmer une présence réelle ni
révéler une personne cachée ; le souvenir de veille est sauvegardé.

**Épreuves consolidées.** **131 tests verts / quinze fichiers, 161,514 s**,
zéro échec, erreur ou saut ; code final, retrait de rotation vocale compris.
Sept nouveaux tests : déplacements vers la crypte du Relais et le filon de
la mine, appel réel reconnu et intervention, recherche sans localisation,
désespoir prioritaire, limite de portée stable, portes réelles distinctes
des portes crues, coût et invalidation par l'oreille propre, inspection sans
case. Mondes entiers, rendu et scène rechargés ; mêmes laps entiers/découpés.
Les déplacements du protégé et sa nouvelle localisation sont des données
d'épreuve ; sa marche autonome de bout en bout n'est pas démontrée ici.

**Banc terminé.** **20/20 nuits de 4 h identiques**, cinq scénarios × quatre
graines (1985/7/42/2024), états complets, chroniques et mesures compris.
Les nuits historiques sans agenda `protéger` déclaré restent inchangées.
Suspects 219 **0 → 0 dans chaque nuit**, zéro plantage et usurpation.
Vingt références `f08ef58` relues du cache, moteur/outils identiques à la base
(diff git vide), aucune référence rejouée. Un travailleur à priorité réduite,
calcul détaché vérifié actif au départ ; **`fin.json ok=true`, code tests 0**,
826,612 s au total, écrit en dernier. Empreintes de tous les fichiers validés
inchangées à la clôture ; aucun calcul actif, aucune relance.
Ni Luna ni suite complète. Ces nuits sans agenda nouveau prouvent la
non-régression historique ; le suivi actif est éprouvé par les tests.

**Recouvrements.** Lot 330 : `planification.py`, `pnj.py`.
Lot 333 : `agendas.py`, `pnj.py`, `tests/test_agendas_proteger.py`.
Documentation de reprise commune aux deux. La stabilité prouvée par les
épreuves reste bornée à leurs géométries et croyances, sans garantie générale
de retrouvailles ni de correction de toute croyance périmée.
