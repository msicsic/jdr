# Lot 90 — Le séjour terminal appartient au recours prioritaire

Branche `codex-recours-prioritaire`, **non fusionnée**, base `9810f4a` (lot 87
inclus). Code signé SSH, dernier correctif `8a6c1b6`, contrôle des ressources
`735165d`. Lot 88 `9193904` fusionné **localement** par `3665e94` pour les
vérifications. Aucun appel à Luna, changement de scénario ou de `main`.

**Invariant.** Le séjour tarifé dans l'état terminal d'un recours fait partie
de son exécution. `eclairer(tenir=True)` exportait seulement le trajet : arrivé
dans la lumière fixe, le PNJ perdait son recours prioritaire et repartait vers
le noir pour une ronde inférieure. L'export termine désormais par `abriter`
sans flamme allumée portée. `_plan_lumiere` revalide ce séjour ;
`_continuer_progres` et `_candidats` retrouvent le recours qui porte le progrès,
avec repli s'il devient impossible. Le geste durable existant va jusqu'à
`SECURITE_FIN` ; priorités, inertie, alarmes et périls gardent leurs règles.
Le terminal passe par `_couper` : aucun séjour anticipant une livraison ou un
geste incertain ; une attente vide reprend son séjour après constat du résultat.
Aucun délai, registre, coût, horizon ou plafond nouveau. Les lectures ajoutées
sont hors du graphe ; aucune extension de `_entrees` n'est nécessaire.

**Preuves.** Capture réelle crue 2024 à 645, sans retouche : **128 → 8 passages
d'Aubin / 30 min**, même monde complet et vue description/sons d'un bloc ou
par quinze secondes sauvegardées/rechargées. Aubin reste inquiet à 675 : aucune
inspection sans moyen n'est prétendue. Autre cas : gardien au puits noir de la
mine, séjour sans navette, mêmes monde et vues découpés, puis ronde après
apaisement ; avec lampe portée, ronde possible malgré la sécurité haute.
Recours portable ordinaire et fin de plan sauvegardée également vérifiés.
`VERIFIER`, capture **30 min** et mine **3 min** : **aucun écart ni borne**.

**Mesures.** Rapide final `735165d`, **4 h × quatre scénarios × quatre graines**,
contre `9810f4a` : seize références relues du cache, aucun plantage, violation
ou usurpation, mêmes constats d'audit. Pires heures par PNJ inchangées :
**8 / 10 / 15 / 24** (Relais/mine/auberge/crue). En crue, bascules **4 → 5**,
avis textuels redits **0 → 1**, sans alternance durable nouvelle signalée.
Relais/mine : chroniques et récits identiques. La branche inclut le lot 88 :
ces écarts ne sont pas attribués au seul lot 90. Références jamais relancées ;
mesures de branche reprises après les corrections, sans comparaison des CPU
mis en cache. Dernière reprise : mêmes chroniques/récits que la précédente.

Audits **12 h**, anciens bruts relus : crue 2024 **237 → 24 passages/h**,
**292 → 30 glissantes**, bascules **3 → 3** ; crue 500 **22 → 22 / 32 → 32**,
bascules **2 → 2**, chronique/récit identiques. Aucun plantage ; disparition
des alertes de rafale et de va-et-vient. La nuit native 2024 diverge avant 649 :
la preuve sur un même état demeure la capture à 645.

**Tests.** Suite complète unique : **1 946 tests, 16 ignorés, 1 286,32 s**,
202 fichiers, 15 échecs dans cinq fichiers. Erreur réelle d'export après coupure
corrigée ; oracle de rang adapté, poussée vérifiée à son instant, annonce isolée
du séjour prioritaire, bois contrôlé à chaque transfert réel plutôt que par une
vente imposée. **68 tests ciblés finaux verts** ; bilan consolidé **1 947 tests,
16 ignorés, aucun échec/erreur restant**, sans seconde suite complète.

**Limites.** Pas de comparateur universel des plans entre besoins : `INERTIE`
et les priorités restent l'autorité. En 2024 subsistent 45 min de faim sans
recours pour Brune puis attente, et **3 → 6 avis textuels redits**, espacés d'au
moins **96 min**. Causes hors de ce correctif, sans garantie d'absence de tout
autre défaut. Créneau de 45 min dépassé ; priorité réduite, bancs et suite
plafonnés à trois processus. Bruts et consolidation dans `artifacts/90/`.
