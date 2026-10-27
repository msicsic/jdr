# Lot 190 — Mesurer la réflexion limitée avant de décider

2026-10-27, PC fixe, branche `codex-mesure-reflexion`, base `e62c5bf`.
**Mesure partielle**, aucun `donjon/`, Luna ou sauvegarde utilisateur touché.
Deux calculs réduits au plus. Bruts exclusivement
`C:/Users/msics/donjon/artifacts/reflexion-190/`.

**Variantes.** C = recherche courante. I = profondeur
`min(profondeur demandée, max(2, min(8, 2 + INT modulée // 3)))` : les malus
corporels réduisent déjà l'INT. E = I, sauf sécurité/devoir ou besoin servi à
`DESESPOIR` : profondeur demandée conservée (proxy large de l'enjeu).
Aucun budget expérimental en nœuds ou cas de scénario. **Saillance non modifiée** :
`emplois`, pertinence, lumière et gestes communs. Aucune règle livrée au jeu.

**Neuf nuits libres**, mine/auberge/`crue_hameau`, 12 h, graine 1985, départ
fixe ; C/I/E séquentiels. CPU instrumenté indicatif, poste partagé : aucun gain causal
prouvé. N = nœuds de toutes les passes, certificats séparés dans les bruts.
S = signatures famille × auteur × texte, F = familles, D = diversité moyenne
par PNJ, inactifs compris (lot 183).

| Nuit / variante | Recherches / neuves | N | CPU s | Sans recours / attente, min·PNJ | S / F / D | Alertes audit |
|---|---:|---:|---:|---:|---:|---|
| Mine C | 4 383 / 1 127 | 213 793 | 66,55 | 65 / 1 525 | 50 / 6 / 2,29 | 6 figés, 6 noirs |
| Mine I | 4 383 / 1 127 | 97 691 | 48,86 | 65 / 1 525 | 50 / 6 / 2,29 | idem |
| Mine E | 4 383 / 1 128 | 120 310 | 54,75 | 65 / 1 525 | 50 / 6 / 2,29 | idem |
| Auberge C | 9 036 / 2 850 | 526 512 | 201,09 | 70 / 435 | 75 / 5 / 2,75 | 3 figés, 1 noir, 4 alternances de visite |
| Auberge I | 9 065 / 2 854 | 293 320 | 154,28 | 70 / 440 | 75 / 5 / 2,75 | idem |
| Auberge E | 9 036 / 2 850 | 302 253 | 146,08 | 70 / 435 | 75 / 5 / 2,75 | idem |
| Hameau C | 2 277 / 1 110 | 296 886 | 65,94 | 165 / 440 | 50 / 7 / 3,17 | 2 figés |
| Hameau I | 574 / 505 | 32 349 | 16,61 | 60 / 10 | 40 / 6 / 2,33 | aucune, mais tous partis |
| Hameau E | 574 / 505 | 32 349 | 16,81 | 60 / 10 | 40 / 6 / 2,33 | idem |

Mine : mêmes monde, chronique, récit et souvenirs pour I/E ; E change seulement
le compteur de recherches neuves. Auberge E identique au témoin ; I diverge
dans la chronique à **658 min**, Lucien vers la cuisine. Hameau : premier
écart à **40 min**, approche du pied-de-biche d'Aubin. Le témoin perd quatre
PNJ à 150–151 min ; I/E perdent les six à 150–154 min. **Le défaut des sorties
internes, en cours de correction au lot 189, invalide toute lecture favorable
de cette économie CPU/attente et de l'absence d'alertes.** Zéro usurpation dans
les neuf nuits ; aucun plantage.

Odon/argent : C/I/E = **742 recherches, 102 neuves** ;
**11 043 / 10 637 / 10 637 nœuds**, **2,88 / 2,58 / 2,66 s CPU** inclusives
de recherche. Baisse faible sur ce but ; les 68 % du lot 187 portaient sur une
autre graine et 4 h, pas sur ce dénominateur.

**Myopie appariée.** `mesure_reflexion_190.py --apparier` observe la première
exploration neuve par heure × PNJ × but, copie la Vue **avant** les découvertes,
et rejoue I/E sans graphe repris ; C continue seul la nuit. Il compare les
plans avant `endurer`/export, **pas les choix de but**. Oracle C courant,
**pas `REFERENCE` sans emplois**. Exemples détaillés dans `bilan.json` ;
l'échantillon n'est pas un taux exact de décisions changées.

Mine : **0/242**, hameau **0/102** plans changés pour I/E, surcoût nul.
Auberge : **2/357 (0,56 %)** pour I,
**1/357 (0,28 %)** pour E ; aucun plan perdu. Surcoût cumulé/maximal des plans
communs : I **10,252/8,085**, E **2,167/2,167** minutes de coût modèle.
Lucien 519 : sept étapes remplacées par une demande à Odile ; Lucien 658,
I : huit étapes lumière/retour remplacées par rester (108,915 → 117).
Tous scénarios : aucun plan perdu/nouveau ni oracle plafonné dans l'échantillon.
Le hameau diverge pourtant en nuit libre : cet échantillonnage ne suffit pas.

**Trouvailles.** La scène de `test_planification` (position explicitée pour
sauvegarder) trouve en C huit étapes, dont allumer avant crochetage ; I/E
perdent ce plan, trop long. Le choix social nourrit toutefois Brune dans les
trois variantes : **plan perdu ≠ décision ou repas perdu**. La capture
`tests/data/taches_relais42_avant_part.json.gz`, Relais 42/151, choisit désormais
les fagots propres de Gorm dans les trois recherches : demande des planches
d'Aubin non redémontrée. Les intentions sauvegardées ne sont pas réécrites.

**`VERIFIER` et caches.** Séparer recalcul identique à moyens/horizon égaux,
déterminisme avec recharge/laps découpé, myopie face à la complète mesurée.
L'optimum limité reste à prouver : le meilleur coût par état peut masquer une
arrivée plus courte en étapes ; devis estimés et plafonds restent des limites.
`_entrees` contient la profondeur : mémoire, graphes et certificats restent
utilisables **au même horizon**, sans preuve d'absence globale. Reprises de
graphes C/I/E : mine 26/26/26, auberge 264/264/264, hameau 66/30/30.
La saillance demanderait sa règle et son ensemble effectif dans la clé, récence
comprise, avec les lectures des gestes/devis/routes. Gain de cache non mesuré.

**Recommandation : ne pas avancer l'implémentation avant A5 sur ces seules
mesures.** Préparatif émergent perdu, hameau confondu par les départs.
Reprendre la saillance liée au but après 189 et comparer les choix entiers à
entrées égales et à `REFERENCE`. Filtre de saillance, oracle élargi, ensemble
des choix et campagne multigraines restent non mesurés.

**Contrôles/reproduction.** Les trois témoins appariés sont strictement identiques
aux témoins simples (monde, chronique, récit, souvenirs, mesures, empreintes).
Douze états finaux et leurs rendus passent le cycle
JSON ; six scènes passent sauvegarde disque/rendu et 10 min contre 5 + recharge
+ 5. Syntaxe et `git diff --check` verts ; aucune suite complète pour ce diagnostic.
Python principal, `tools/mesure_reflexion_190.py --scenario <scénario>
--variante <complete|int|enjeu> --sortie <bruts>/<nom>.json.gz` ; témoin apparié :
`--apparier`. Puis `tools/scenes_reflexion_190.py <bruts>` et
`tools/bilan_reflexion_190.py <bruts>`, deux calculs au plus.
