# Lot 338 — Deviser et conserver le recours jusqu'au constat

30 octobre 2026 — `codex-recours-sans-cout`, **terminée, non fusionnée**.
Fusion sans rebase **`20e1f41`**, parents `38bc65d` et `fff9aab` : code de
l'intégration `c9b972b`, seul ajout suivant documentaire (brief 341).
Aucun conflit de code ; deux côtés de `etat-dev.md` conservés. Branche poussée.
Bruts : `C:/Users/msics/donjon/artifacts/recours-338/`.

**Invariant.** Toute proposition admissible d'agenda porte un coût fini.
`agendas.planifier` conserve le coût complet des recherches (récupération,
pièces, garde) ; `planification.mesure_recours` compose approches, gestes et
pression des suites directes, inspection et attente comprises. L'attente sans
geste coûte zéro ; l'impossible n'a pas de mesure. `duree_devis` partage la
composition physique ; `choisir_mandataire` réserve l'infini au recours absent.

Le contrat sauvegardé d'intention retient les entrées du moyen.
`deliberation.choisir` garde son suffixe admissible jusqu'au terme ou son attente
adoptée jusqu'à une entrée nouvelle. Déplacement propre et dates de regard ne
rouvrent pas les moyens ; états crus, ressources, accords, refus, relations et
échéances le peuvent. Démenti, fin du projet et urgences gardent leurs contrôles.
Ni changement d'`INERTIE`, délai ajouté, lieu interdit ou exception de scénario.
Après fusion, contrôle AST : `_entrees_communes` et six fonctions communes
(croyances, naissances, fin de garde, contrat, conditions et satisfaction)
identiques à l'intégration. Entrées des contrats du 336 et preuves de fin du
337 conservées ; aucun nouveau lecteur de recherche hors de `_entrees`.

**Validation après fusion : 518 tests / 52 fichiers**, union des ciblés 338,
336 et 337, **513 succès, quatre échecs préexistants, un saut facultatif,
zéro erreur**, 2 130,177 s. Tous les incidents rejoués isolément sur
**l'intégration exacte `fff9aab`**, 11,552 s : mêmes quatre assertions,
hors chemins de worktree. Appel de protection : Gorm en `beffroi`, attendu
`echoppe` ; réaction au feu : 600 au lieu de 205 ; geste illicite sans
`vu_agir` ; audit : `_retentir` refuse l'argument `emission`. Aucune correction
ni adaptation d'oracle. Saut : validation JSON Schema, `jsonschema` absent.
Les fichiers de régression **338 5/5, 336 8/8, 337 14/14** sont verts.

La capture réelle 317 crue 3 à 160 min conserve son inspection à 170 et
l'arrêt des navettes jusqu'à 175 ; monde, rendu et scène après recharge,
15 min entières ou découpées, identiques. Autre scénario : attente de garde à
l'auberge, 3 min entières/découpées. Devis inspection/attente, continuité
d'`informer` après déplacement et réouverture sur localisation nouvelle testés.

**Crue 3, 12 h après fusion : maximum Gorm 26 passages/h**, zéro usurpation,
282,450 s. Par heure : **5, 10, 22, 0, 0, 4, 4, 26, 12, 4, 0, 26**.
Tests puis nuit détachés, deux travailleurs réduits au plus : 2 416,177 s.
`fusion-validation/fin.json` brut rouge conservé ; quatre défauts attribués
dans `attribution-echecs.json`, clôture qualifiée `fin-cloture.json`.
Code et tests inchangés depuis `20e1f41` ; aucun calcul actif.

**Mesures initiales conservées, non rejouées après fusion.** Avant
synchronisation : 206 tests, 205 succès/un échec antérieur ; vingt nuits 4 h,
suspects 219 **0 → 0 par nuit**, zéro plantage/usurpation. Vingt références
absentes calculées/rangées une fois, aucune disponible relancée. Avis à expliquer
43 → 38, dérives ouvertes 436 → 422 ; maximum crue 3 à 30 passages/h.
Repère du diagnostic 317 : 298 sur `75b6dfb`, sans nouvelle référence 12 h.

**Limites.** D'autres allers-retours subsistent ; aucune absence générale de
boucle ni réussite de tout l'agenda (qui vise aussi Brune) revendiquée.
Devis du prochain sous-but, sans garantie d'accord ; empreinte conservatrice,
sans preuve de dépendance causale minimale. Ni Luna, suite complète, banc
4 h après fusion ou correctif du contact Aubin/Sève.
