# Lot 244 — réserve faible et capacité de lumière

28 octobre 2026, PC fixe. Branche `codex-lumiere-faible`, non fusionnée,
base `integration` **707e7ac**. Aucun Luna ; deux calculs simultanés au
plus pour ce lot, priorité réduite. Bruts :
`C:/Users/msics/donjon/artifacts/lumiere-244/`.
Créneau dépassé par le contrôle systématique 8 h et l'attente de validation.

**Cause.** La source faible conserve déjà le rang 3 de `Vue.capacite`,
sa lumière et sa flamme ; `couvre`/`doublon` ne les perdent pas. Lucien
ne porte pas la lanterne d’Hugues et emploie déjà la lumière (`peur=0,5`).
En revanche, `Vue.feu` lit sa réserve faible comme une charge insuffisante,
rendant l’huile pertinente et multipliant possessions, lieux, ouvertures
et droits sans capacité nouvelle. Le témoin complet optimisé génère
729 acquisitions d’huile (382 burettes, 347 pots), 1 052 devis et
6 528 nœuds ; aucun de ces gestes/devis après correction, 336 nœuds.

`Vue.recharge_utile` exprime le contrat commun : une recharge permet
d’allumer une source éteinte sans charge, ou restaure une réserve visée
explicitement par un entretien. Ce critère sert aux acquisitions de combustibles seuls, aux
parts à demander (`sources_a_charger`) et au geste `alimenter`. Les buts
qui visent un combustible restent autorisés ; l’entretien d’une source
faible reste exécuté et sauvegardé. Code du jeu : `planification.py` seul ;
aucun plafond, devis, autre mécanisme ni MJ modifié.

**Preuves ciblées.** Les captures réelles 435:0 (grenier et chambre chaude)
et 435:292 (chambre chaude) sont rechargées et comparées à l’ancienne
recherche uniforme complète avec l’ancien critère de recharge.
Même résultat, sous les 4 000 nœuds ; au grenier,
**7 091 → 336**, coût **125,64**, rester ; à la chambre, **11 139 →
656** et **11 898 → 663**, coûts **108,316985 / 106,56**. Le monde, `regarder` et
`scene_percue` sont identiques avant/après sauvegarde. Mêmes objets et
esprit après le laps en bloc ou découpé, rechargé, caches initialement vides.
Rejeu ciblé de 435 à 480 :
**zéro seconde sans intention**, garde du grenier maintenue, contre les
44 min 17,8 s du lot 243 : la garde de la complète remplace l’abandon
du recours borné. Autre cas à la mine : lampe faible de Rémy,
même réponse que la complète, laps découpé et rechargé identique ; entretien
joué, réserve augmentée et combustible consommé, persistés.

**Mesures.** **12/12 paires d’empreintes 2 h identiques**, auberge/mine/Relais
× quatre graines : chronique, mesures et état final complet. Mine 1985
4 h fixe : **10 119 → 10 100 nœuds (−0,19 %)**, 310 recherches neuves
inchangées ; six empreintes identiques, dont l’état complet et le récit.
CPU indicatif **18,39 → 18,89 s**, aucune conclusion temporelle.
Références 707e7ac calculées une fois et rangées, aucune rejouée.
**20/20 paires 4 h identiques** sur état final, chronique, récit,
souvenirs, mesures, repères, boucles et audits, cinq scénarios × quatre
graines ; zéro plantage. Deux suspects inchangés (auberge et crue). Aucune décision
changée dans ces vingt nuits. Contrôle **8 h auberge 42 vert, 2 528,217 s**
(`VERIFIER`, `spatial.VERIFICATION=0,2`) : aucune assertion, une seule
`ancienne_borne` à 312 (lumière de Lucien), même coût complet **73,498790** ;
plus d'absence à 435. Les 143 choix observés entre 435 et 480 gardent une
intention ; état final et rendu rechargés vérifiés.
**Suite complète laissée au superviseur**, conformément à la règle reçue
pendant le lot (`integration` 4422f13) : passe en cours arrêtée, sans bilan
global. **21 ciblés verts**, puis les **5 tests finaux verts, 18,244 s**.
Reprise hors confinement après refus Windows des dossiers temporaires.

**Limites.** L’invariant prouvé porte sur les capacités de la projection
actuelle : celle-ci ne décompte pas l’autonomie pendant chaque trajet et
séjour. Ce lot ne garantit donc pas qu’une source faible couvre la durée
physique d’un long plan, ni qu’aucune autre recherche n’atteindra son plafond.
Les perceptions et replanifications réelles restent responsables de la
suite. Aucun oracle existant n’est modifié.
