# Lot 171 — Diagnostic des refus de mesures résolues

27 octobre 2026 — Branche `codex-mesures-resolues`, **diagnostic, non fusionnée**,
base `06cfe9e`. Périmètre réduit sur instruction de l’orchestrateur : aucun code,
appel Luna, rejeu ou suite de tests ; aucune correction ni garantie nouvelle.

**Conclusion : trois faux refus, aucune source nécessaire absente du dossier.**
Les rapports bruts contredisent l’hypothèse initiale selon laquelle une autre
affirmation non établie expliquerait le rejet. Cette hypothèse est retirée.
Les tours ci-dessous suivent les indices zéro du brief et des fils.

| Audit | Motif exact et confrontation aux sources | Diagnostic |
|---|---|---|
| `force-4c-fuir` p1 t1, segment 0 | « Tu avances de deux pas, tandis que des pas résonnent à l’ouest. » Rejet : « Le résultat établit deux pas, pas deux pas supplémentaires/en total de deux pas. » `resultat_resolu.faits` contient deux occurrences de « Tu avances d’un pas. », chacune suivie de « Tu entends des pas à l’ouest. ». | **Faux refus** : la phrase résume les deux pas du résultat courant, sans dire « supplémentaires ». Le son à l’ouest est également fourni. Aucune autre affirmation rejetée ni source manquante ; confusion sémantique sur le cumul. |
| `force-4c-fuir` p2 t1, segment 0 | « Tu fuis Brune en avançant de deux pas vers la sortie connue la plus proche. » Rejet : « Le résultat établit deux pas vers l’ouest, non deux pas vers la sortie la plus proche; cette reformulation contredit les gestes et faits résolus. » Les mêmes deux pas figurent dans les faits ; `resultat_resolu.gestes` fournit « Fuir Brune, batelière évacuée, qui t’a agressé, par la sortie connue accessible la plus proche. ». | **Faux refus** : l’autre affirmation effectivement contestée est la destination de la fuite ; sa source est présente dans le geste résolu. L’ouest apparaît dans les sons entendus, pas comme direction de ces pas dans les faits. Le motif ne démontre aucune contradiction. |
| `atelier` p2 t8, segment 0 | « Tu vois le mur de l’atelier à environ deux mètres au nord et trois mètres à l’ouest. » L’audit cite lui-même 2 m nord et 3 m ouest, puis les déclare différents ; sa citation finale se termine par « à l’ouï », absent du texte contrôlé. `objet:mur_atelier.localisation` donne `direction=nord-ouest`, `position_relative=2 mètres vers nord et 3 mètres vers ouest` ; `visible=true` et `perception.objets_visibles` contient le mur. | **Faux refus** : nombres, axes et visibilité concordent. Aucune autre affirmation rejetée ni source manquante ; l’équivalence chiffres/mots et prépositions échoue dans le jugement, avec une citation altérée. Le segment 1 est admis. |

**Correction générale à concevoir.** Le lot 95 (`textes_etablis`,
`segments_etablis`) ne prouve que des segments entiers exacts ; aucun de ces
trois segments n’est une reprise exacte. Une égalité numérique seule ne peut
donc pas exempter une phrase qui comporte d’autres assertions. Une décomposition
typée pourrait lier chaque assertion à son acteur ou repère, sa temporalité,
son unité, sa quantité et ses axes, puis comparer ces valeurs au moteur tout
en contrôlant les autres assertions. La fidélité et l’exhaustivité de l’extraction
resteraient à traiter ; ce n’est pas une correction livrée ici.

Piste plus petite à évaluer : fournir des attestations canoniques de positions
visibles et des totaux de déplacements issus d’un résultat structuré, réutilisables
par la preuve exacte. Cela facilite une narration prouvable, mais ne garantit
pas l’acceptation des trois reformulations libres archivées. Ajouter des exemples
au prompt ou exempter une phrase par ses seuls nombres ne répondrait pas au contrat.

**Preuves et limites.** Lecture des trois premiers appels `auditer_narration`
concernés, de leurs entrées, réponses brutes et obstacles, rapprochés de
`relances-168/attribution.json`. Extraits complets et SHA-256 des fils dans
`C:/Users/msics/donjon/artifacts/mesures-171/diagnostic-audits.json` ; originaux
dans `verif-luna-227c496/{force-p1,force-p2,reference-p2}/`. Pas de causalité
plus fine démontrée sur le fonctionnement interne de Luna ; pas de mesure de
variance, de validation après recharge ou de critère 95 revendiqués.
Aucune clé Git de signature configurée ; livraison non signée, `main` intacte.
