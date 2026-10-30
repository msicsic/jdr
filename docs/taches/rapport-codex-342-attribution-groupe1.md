# Lot 342 — corrections poussées, reprise de validation en cours

30 octobre 2026. Branche documentaire `codex-attribution-groupe1`, base
`16b18a7`. [Matrice des 33 incidents](attribution-codex-342-groupe1.md).
La fin des nouveaux calculs reste à analyser avant clôture.

**Attribution.** Référence exacte `e37d9ee`, puis chacun des lots 313/315/332/333
seul : 27/22/23/22/22 tests, 8/14/2/11/1 incidents ; 2 177,100 s. Les deux
interactions sont prouvées par retrait d'un seul lot. Six incidents initiaux
restent attribués au 339 et celui de la mine à l'intégration antérieure ; ils
passent dans l'assemblage récent sans être crédités aux correctifs du 342.
Une méthode absente n'est jamais comptée comme une preuve verte.

**Contrats corrigés.** Le 313 (`cddc76e`, correctif `de03f87`) traite une position
absente comme inconnue dans la perception commune, sans fournir le joueur réel
au devis fermé : neuf tests de devis verts. Le 332 (`4da7dc4`, `3acd5c7`)
distingue direction, interprétation et geste : une référence requise absente
n'admet aucun savoir relationnel ; le signal prépare la rotation, sans rouvrir
le but avant la perception. À la disponibilité du PNJ, ce geste préparé passe
avant le bavardage facultatif. Aucun PNJ ni scénario particulier dans ces règles.
Les premiers prototypes de priorité/rétention de direction sont écartés.

**Attentes contrôlées.** Quatre captures retrouvent exactement leur ancien hash
après retrait strict du seul registre vide ; deux autres changent seulement les
registres/provenances des regards, huit autres oracles identiques. Le 315
(`beaecc7`) conserve deux remboursements uniques ordonnés et la borne 84, le
contact pouvant conclure plus tôt. Le 333 (`40bd537`) isole le secours concurrent
d'Odile dans la scène de prêt, toutes assertions conservées. La scène de lampe
(`c3db8e2`) fournit explicitement son second stimulus, une source connue de
niveau 2 : la vraie chandelle vaut 1 et Rémy peut rester au baraquement obscur.
Toutes assertions finales sont gardées. L'oracle d'abri initial est restauré
intégralement ; le KO observé dans un témoin antérieur ne sert plus d'oracle.

**Mesures acquises.** Assemblage `94329d3`, base `da5f795` : **279 tests /
27 fichiers, 11 incidents**. Les témoins sur cette base reproduisent huit
réserves restantes après correction des trois points propres à l'assemblage :
deux boucles, deux dynamiques, deux captures chaînées, lampe vide, aide 541.
Même assertion rouge ne signifie pas trajectoires identiques. Reprise ciblée :
**12/12 verts**, attention conjointe dans deux scénarios, lampe réelle, abri,
monde/rendu/scène rechargés et temps découpé. `jeu.py` inchangé par rapport
à la base ; ni Luna ni suite complète.

**Calcul restant.** Essai corrigé `93d5a25`. Les 27 fichiers sont repris après
le changement de l'ordonnanceur, puis vingt nuits de branche (4 h, cinq scénarios,
quatre graines). Deux travailleurs réduits au plus, phases séquentielles. La
première tentative de banc a échoué dans l'observateur récent de la référence
ancienne (`agendas.enfants`), avant toute nuit de branche ; sortie invalide
conservée. La reprise relit vingt références historiques `c870c8b` du cache,
instrumentation `1f6b05da83`, et joue uniquement la branche. Observations de
versions distinctes, aucune attribution causale à un seul lot ni comparaison
de vitesse. Aucun résultat de banc n'est encore annoncé.

**Limite.** La variante sans 332 sur la base récente garde 33 passages d'Aubin,
celle sans 313 en garde dix. Cette interaction 313/base récente n'est pas
déclarée corrigée en général par le succès de l'assemblage avec le réflexe.
Bruts `C:/Users/msics/donjon/artifacts/groupe1-342/`, fin attendue
**`cloture-1/fin.json`** : fin du calcul, pas attestation de réussite du lot.
