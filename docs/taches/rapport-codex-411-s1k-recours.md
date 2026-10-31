# Lot 411 — S1k, recours historiques par la porte commune

31 octobre 2026 · `codex-s1k-recours` · base exacte `integration 8cb825aa`.
**Lot non fusionné ; vérification en cours.** Le commit mesuré et le résultat final
des empreintes sont consignés dans les bruts `debut.json` et `fin.json`.

**Invariant et code.** Les cinq registres `demande_refusee`, `recours_propositions`,
`recours_services`, `recours_intermediaires` et `service_en_cours` passent par
`donjon/memoire.py`. Cinq vues rendent des copies profondes pour un observateur
explicite, sans création d'esprit, apprentissage, expiration ni acquittement.
Les opérations nommées retiennent l'essai de service, son commencement et sa
clôture, restaurent le devis supplanté, publient la commission choisie, puis
enregistrent son issue, la part affectée et la livraison accomplie. La proposition
exécutée remplace l'essai du même tiers/besoin et acquitte son déclencheur au
même instant qu'avant. Les admissions sont copiées ; les validations sont portées.

`pnj_propositions` garde les prédicats `_tient`, `refus_tient`, l'identité historique
du refus, les devis et leur classement. Un service impossible reste tenté ; une
commission moins chère restaure exactement le service non choisi. Perte de moyens,
regard rafraîchi et temps seul ne rouvrent pas un recours. Les délais historiques
distincts des refus d'humeur et d'aide attendue restent inchangés. Aucun nouveau
registre, choix, parole, délai, tirage, schéma de sauvegarde ou appel modèle.
`agendas`, `echanges`, `deliberation`, `esprits` et les métriques de `banc_pnj`
consomment la porte ; leurs autres responsabilités restent locales.

**Contrôle et tests.** Inventaire AST des recours **84 → 1 expression**, la seule
déclaration exacte du schéma : **zéro accès au stockage hors porte**. Le contrôle
fermé et ses contre-épreuves de clés indirectes, alias, boucles, méthodes détachées,
retours et mutations sont conservés ; l'inventaire des refus du 409 ne croît pas.
Première passe : **70 tests**, dont socle et porte verts ; deux sous-échecs
`offre_sensee` (marchand/Aubin) et une erreur de placement Hugues/Mathurine déjà
signalés par le 409. Leur attribution à la base exacte est vérifiée séparément.
Les tests complémentaires portent sur les copies imbriquées, les admissions,
les écritures ciblées, les corruptions, les prédicats et la survie après 45 épisodes.
La capture réelle crue 7, minute 353, puis deux services et deux commissions
contrôlent état complet, ordre JSON, lignes, rendu, scène et paroles après recharge,
pour deux minutes entières ou quatre tranches. Résultats détaillés dans les bruts.

**Empreintes en cours.** 2 h × graines 1985/7/42/2024 × Relais/mine/auberge/crue,
comparées à la base exacte `8cb825aa`, sans exclusion. Référence et branche
successives, cache partagé par commit, deux travailleurs réduits au plus ;
`fin.json` est écrit en dernier. Aucune identité n'est annoncée avant ce résultat.

**Limites et voisinage.** Contrôle AST syntaxique et local, sans preuve de tous les
flux interprocéduraux Python ; politiques historiques conservées. Pas de suite
complète ni Luna. Aucun fichier de `fournisseurs/` du 410 n'est touché ; le 402
reste un calcul indépendant. Dernière actualisation : `origin/integration 8cb825aa`,
sans avance à fusionner. Bruts : `C:/Users/msics/donjon/artifacts/s1k-411/`.
