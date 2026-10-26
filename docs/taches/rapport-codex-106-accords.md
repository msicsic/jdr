# Lot 106 — Accord en nombre des textes composés

Branche `codex-accords`, non fusionnée ; base `dcd7b31`. Aucun Luna.

**Contrat.** `francais.pluriel` centralise le nombre déclaré, prioritaire, sinon
la déduction par la tête du nom ; noms propres et références sans nom restent
singuliers. `designer`, les accords et les formulations sociales l'emploient.
`quantite` compose les noms comptés et leurs déterminants : 0/1 au singulier,
2 au pluriel, flexion irrégulière explicitable. Les pièces des propositions,
échanges, missions, chroniques, fiches, TUI et navigateur passent par ce
contrat ; les descriptions physiques et utilisations aussi. Le navigateur
reçoit `or_texte` calculé en Python. Aucun scénario, planificateur, délibération,
prompt ou format de sauvegarde modifié.

**Preuves.** Odon, mine 7, minutes 0/13, est reproduit au banc ; l'échange
Lucien–Anselme à une pièce contre le ballot est reconstitué en test. Échanges,
propriété, paiements ou refus, phrases entendues, chronique, récit et rendu
sont vérifiés après recharge, avec noms déclarés, noms en -x et quantités
0/1/2 de pièces, parts et objets (formateur), puis fiches et compteur web.

**Mesures.** Empreintes 2 h, Relais/mine × 1985/7/42/2024, référence `dcd7b31`
calculée une fois puis cachée (localisation automatique du premier écart).
Huit mesures et empreintes de jeu identiques. Les deux seules substitutions
observées sont « l'outils de serrurier » → « les outils de serrurier » et
« contre 1 pièces. » → « contre 1 pièce. ». Dans l'état final : **28 chaînes**
(19 désignations, 9 contre-offres sonores), réparties Relais **1/0/0/1**, mine
**4/11/0/11**. Après restauration de ces seules chaînes dans les captures,
les **huit SHA-256 complets** égalent la référence ; huit sauvegardes/recharges
et rendus du joueur identiques. Aucun autre écart d'état.
Suite complète unique : **1 995 tests, 16 ignorés, 212 fichiers, 1 822,58 s**,
deux processus réduits ; cinq échecs et deux erreurs corrigés (références
sans nom et anciennes attentes). Reprises finales : **158 tests, un ignoré,
aucun défaut restant**, onze fichiers ; une erreur de localisation de la
nouvelle scène de test corrigée, puis ses cinq tests verts. Aucune seconde
suite complète. Bruts : `artifacts/accords-106/`, notamment
`preuve-etats.json`, `bilan-reprises.json` et les résultats originaux conservés.

**Limites.** La graphie seule ne désambiguïse pas tous les nombres : les formes
invariantes ambiguës exigent `pluriel` explicite. Le formateur reçoit un
singulier et sa flexion irrégulière si nécessaire ; aucune garantie de grammaire
universelle. Les anciennes phrases déjà sauvegardées ne sont pas réécrites.
