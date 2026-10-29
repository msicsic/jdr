# Lot 330 — Demander à un proche ce qui l'inquiète

29 octobre 2026 — `codex-demander-cause`, **terminée, non fusionnée**, base
fournie `f08ef58`, descendante de l'intégration. PC fixe `msi-desktop`.
Code/tests validés : `3ab6aa5`, inchangés depuis le calcul, empreintes vérifiées.

**Invariant et fonctions.** `planification._pulsion` peut faire commencer le
secours de proximité par une question, puis replanifie sur la réponse effective.
`echanges.executer` conserve l'approche et le contact communs ; `causes.connues`
répond depuis les seuls savoirs datés du proche : violence encore active contre
lui, menace d'eau, bruit sans auteur identifié. Un cri attribué au proche est
un signe de détresse, pas une explication. Aucun lieu caché du danger n'est lu
ni ajouté. `social.faire_entendre` et `social.recevoir` diffusent le même contenu
`cause_detresse` au demandeur et aux témoins ; les émissions sont enregistrées.
Le ouï-dire conserve date, source et confiance ; les avis d'eau passent par
`recevoir_prevision`. Une preuve plus récente ou plus solide prime ; une réponse
fausse peut être transmise. Méfiance, ignorance et inconscience ne donnent rien
d'utile. `refus` retient la réponse hors des quarante souvenirs ; `deliberation.tient`
ignore délai, perte du signe, estompement relationnel et date rafraîchie du même
signe. Une nouvelle entrée perceptive peut réarmer la question.

**Preuves.** **192 tests ciblés distincts / quatorze fichiers consolidés verts**,
zéro échec, erreur ou saut : 126 tests repris en 220,043 s, 66 précédemment verts
conservés sans relance. Dix nouveaux tests : agressions réellement exécutées au
Relais et à la mine, question autonome, ouï-dire puis fuite/riposte ; capture
réelle de crue du 266 ; refus, inconscience physique, croyances fausses de
violence et d'eau, bruit, tiers, absence de position transmise, preuve plus forte,
nouveau signe et date seule. État complet, émissions, scène et rendu final
comparés après recharge et laps entier/découpé. Les aperçus intermédiaires du
joueur dépendent des points d'affichage. Deux tests du 266 adaptés conservent
leurs assertions de préfixe certain, maintien, apaisement et recharge.

**Banc 4 h × cinq scénarios × quatre graines**, référence exacte `f08ef58` puis
branche, deux travailleurs réduits au plus. Vingt références absentes calculées
et rangées une fois dans le cache commun, aucune référence disponible relancée.
**20/20 critères tenus : suspects 219 0 → 0 dans chaque nuit ; zéro plantage,
zéro usurpation.** Reprise détachée : **fin.json ok=true, code 0, 1 018,634 s**,
tests compris. Ni Luna ni suite complète ; aucun calcul encore actif.

| Scénario | Questions | Causes dites | Réponses crues | Premiers choix suivants |
|---|---:|---:|---:|---:|
| Relais | 10 | 9 | 4 | 4 |
| Mine | 22 | 3 | 2 | 2 |
| Auberge | 6 | 5 | 2 | 2 |
| Crue | 29 | 22 | 12 | 12 |
| Hameau | 45 | 32 | 8 | 8 |
| Total | **112** | **71** | **28** | **28** |

Les 71 causes dites sont des **bruits** ; eau et violence sont exercées par les
tests, pas par ces nuits. Autres issues : 38 ignorances, trois méfiances.
Après réception crue : 23 choix de compagnie de secours, trois inspections,
une interposition et un engagement. Les trois inspections ont une exécution
ultérieure dans la chronique ; succession observée, sans preuve causale.
Les entrées **à expliquer 32 → 43** et les **dérives ouvertes 387 → 436** ne
sont pas certifiées bénignes ; tentatives de vol **2 → 3**. Aucune amélioration
uniforme des réactions ni absence universelle de boucle n'est revendiquée.

**Limites et livraison.** PNJ seulement ; schéma MJ, voie joueur et Luna inchangés.
Question comme moyen du secours, sans nouvelle priorité ni recherche distante ;
au plus une cause par réponse, ordre violence/eau/bruit, sans exhaustivité.
Recouvrement G17/326 : `docs/etat-dev.md` seulement, aucun fichier de code commun.
Bruts `C:/Users/msics/donjon/artifacts/cause-330/` : échec initial conservé
(24 erreurs d'import masquant l'échange d'objets, corrigé), puis `reprise-1/`
verte ; doublon sur date rafraîchie corrigé avant ce banc. `analyse-cloture.json`
et `tests-consolides.json` explicitent les mesures et leurs preuves. Branche
poussée vers origin ; clôture `fin-cloture.json` écrite en dernier.
