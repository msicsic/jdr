# Lot 342 — terminé avec huit réserves d'intégration

30 octobre 2026. Branche `codex-attribution-groupe1`, base `16b18a7`.
[Matrice des 33 incidents et des huit réserves finales](attribution-codex-342-groupe1.md).

**Attribution.** Référence exacte `e37d9ee`, chaque lot seul et retraits d'un
seul lot : **17 incidents de défaut corrigés**, dont treize issus du même
contrat, **neuf attentes ou scènes périmées**, **sept incidents préexistants**.
Rejeux initiaux : 27/22/23/22/22 tests sur référence/313/315/332/333,
2 177,100 s. Une méthode absente n'est jamais comptée verte.

**Contrats et branches poussées.** 313 `cddc76e` : `esprits._percus` traite
une position absente comme inconnue, sans fournir le joueur réel au devis
fermé. 332 `c3db8e2` : `signes.lire` n'interprète pas une relation privée de
sa référence requise ; une direction prépare un geste, sans rouvrir le but
avant sa perception. `pnj._avancer` exécute le regard disponible avant le
bavardage facultatif, en respectant les gestes engagés. 315 `beaecc7` conserve
ordre et borne des remboursements ; 333 `40bd537` isole le secours concurrent
dans la scène de prêt. Aucun cas de PNJ ou de scénario dans les règles.

**Oracles.** Quatre captures retrouvent leur hash historique exact après
retrait strict du seul registre vide ; deux changent les registres/provenances
des regards, huit autres oracles identiques. La scène de lampe fournit son
second stimulus explicite, une source connue de niveau 2, sans forcer
l'extinction ; toutes assertions finales sont conservées. L'oracle d'abri
initial est intégralement restauré. Régressions sur deux scénarios,
monde/rendu/scène rechargés et temps découpé ; **12/12 ciblés verts**.

**Validation finale.** Essai poussé **`93d5a25`**, base `da5f795`, quatre
branches corrigées. **279 tests / 27 fichiers : sept échecs, une erreur,
zéro saut, 755,310 s.** Ces huit rouges ont aussi un témoin rouge sur la
base, à la même assertion ou au même accès : deux boucles, deux dynamiques,
deux captures chaînées, lampe vide, aide 541. Les trajectoires ne sont pas
certifiées identiques ; aucun oracle n'est recalé pour les masquer. Les six
incidents initiaux du 339 et celui de la mine passent désormais, sans crédit
aux correctifs du 342. `jeu.py` inchangé ; ni Luna ni suite complète.

**Banc.** **20/20 nuits de 4 h**, cinq scénarios × quatre graines : zéro
plantage, usurpation ou suspect certifié 219 dans chaque nuit. **366 suivis,
247 s de rotation**. Vingt références historiques `c870c8b` relues du cache
sans réexécution dans cette reprise ; instrumentation distincte, aucune
comparaison de vitesse ni attribution des écarts à un seul lot. Deux
travailleurs réduits au plus. Première tentative de banc invalide dans
l'observateur de référence (`agendas.enfants`), conservée ; branche jouée
seulement lors de la reprise. Calcul final : 1 368,014 s.

**Limites.** **200 alertes à expliquer**, dont 153 répétitions, restent ouvertes.
La variante sans 332 sur la base récente garde 33 passages d'Aubin, celle
sans 313 dix : interaction 313/base non déclarée corrigée en général par le
succès de l'assemblage. Aucune absence universelle de boucle revendiquée.
Bruts `C:/Users/msics/donjon/artifacts/groupe1-342/`,
`analyse-cloture.json`, **`fin-cloture.json`**, aucun calcul actif.
