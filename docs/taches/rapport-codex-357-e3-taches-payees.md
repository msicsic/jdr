# Lot 357 — E3 et les tâches payées sans limite

Branche `codex-e3-taches-payees`, base `origin/integration 9ea8523`, PC fixe
(`msi-desktop`).

**Invariant et cause.** E3 doit porter le jugement temporel, sans modifier le
contrat des obligations ordinaires. Ses quatre régressions sont reproduites
dans `test_taches_payees` : Tilo accepte sans flamme, Aubin encaisse malgré un
refus connu, la part n'aboutit plus au refus attendu et le prêt du briquet
disparaît du devis. E3 avait remplacé, dans `_pulsion`, l'état annoncé par
l'offre historique par un ancien état cru du prestataire. Celui-ci pouvait
alors ne prévoir qu'une recharge, sans moyen autonome de rallumer.

**Correction.** `_pulsion` choisit désormais ce contrat par la présence d'une
référence temporelle canonique sur l'engagement actif correspondant. Sans
référence, l'offre garde exactement son hypothèse historique. Avec référence,
le devis reste fondé sur les seules croyances du contractant, y compris dans
le plan d'exécution et le jugement d'abandon. `juger_delai` inscrit déjà une
obligation datée sur sa copie : aucun indicateur supplémentaire ni changement
d'interface n'est nécessaire. Le paramètre de mesure `duree` ne sélectionne
jamais un comportement. Acceptation, exécution et abandon passent toujours
par la même recherche autonome ; aucune exception d'objet ou de scénario.

**Épreuves.** 169 tests distincts dans 16 fichiers ciblés/voisins : 164 verts,
dont les 57 tests des tâches payées et d'E1 à E4 ; cinq tests voisins gardent
onze assertions rouges, reproduites à l'identique sur la base intacte
(`test_echanges_argent` : prêt de lampe ; `test_part_proposee` : quatre tests
du terminal). La passe groupée dure 235,569 s ; le fichier E3 final, 8,713 s
(une fixture ajoutée corrigée, aucun changement moteur supplémentaire).
Les deux tests de régression ajoutés contrôlent, avec `planification.VERIFIER`, le
même devis impossible avant/après mesure (Tilo et capture du Relais), puis le
même devis et plan datés après changement des croyances privées du bénéficiaire
(huile à l'auberge, huile à la mine, feu au Relais). Les parcours existants
contrôlent réalisation, refus, prix, remboursement, paroles et promesses après
rechargement ; les ajouts comparent aussi monde, scène perçue et rendu.

**Neutralité.** Empreintes demandées : 2 h, graines 1985/7/42/2024, Relais,
auberge et mine, référence `dbb122b0`. Calcul détaché en cours ; références
relues du cache commun ou calculées uniquement si absentes. En cas de divergence,
le lanceur mesure la base intacte `9ea8523` avec la même référence en cache.
Fin attendue : `C:\Users\msics\donjon\artifacts\e3-taches-357\fin-empreintes.json`.

**Limites.** La voie sans limite conserve sa lecture historique du payeur,
conformément au périmètre et à la transition ; ce lot ne prétend pas la porter
sur le contrat des accords datés. Aucun changement de schéma, rendu, sauvegarde
ou MJ. Ni suite complète, ni Luna, ni banc long. Calculs à priorité réduite,
deux processus au plus. Bruts : `C:\Users\msics\donjon\artifacts\e3-taches-357\`.
