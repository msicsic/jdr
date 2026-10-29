# Lot 335 — protéger à portée de voix

Branche `codex-suivi-vocal`, **non fusionnée**, base `origin/integration 9237e14`.
Implémentation livrée ; **validation élargie en cours**, aucun verdict final de banc.
Bruts attendus : `C:/Users/msics/donjon/artifacts/vocal-335/verification/`.

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

**Épreuves courtes.** **13 tests verts / deux fichiers, 12,011 s** avant
le dernier retrait de rotation vocale, repris dans la consolidation prévue.
Sept nouveaux tests : déplacements vers la crypte du Relais et le filon de
la mine, appel réel reconnu et intervention, recherche sans localisation,
désespoir prioritaire, limite de portée stable, portes réelles distinctes
des portes crues, coût et invalidation par l'oreille propre, inspection sans
case. Mondes entiers, rendu et scène rechargés ; mêmes laps entiers/découpés.
Les déplacements du protégé et sa nouvelle localisation sont des données
d'épreuve ; sa marche autonome de bout en bout n'est pas démontrée ici.

**Validation à terminer.** `tools/valider_vocal_335.py` consolide quinze
fichiers ciblés, puis vingt nuits de 4 h, cinq scénarios × quatre graines,
un travailleur réduit. Vingt références `f08ef58` présentes en cache,
moteur/outils identiques à la base (diff git vide), jamais rejouées.
Critères : aucune hausse des suspects 219 par nuit, zéro plantage/usurpation,
identité des états complets, chroniques et mesures sans agenda déclaré.
`verification/fin.json` est écrit en dernier, même en échec.
Ni Luna ni suite complète. Aucun résultat de banc revendiqué avant lecture.

**Recouvrements.** Lot 330 : `planification.py`, `pnj.py`.
Lot 333 : `agendas.py`, `pnj.py`, `tests/test_agendas_proteger.py`.
Documentation de reprise commune aux deux. La stabilité prouvée par les
épreuves reste bornée à leurs géométries et croyances, sans garantie générale
de retrouvailles ni de correction de toute croyance périmée.
