# Lot 397 — S1f, localisation crue et preuves de possession

31 octobre 2026 · `codex-s1f-localisation` · base exacte `integration 3d59310c`.
Code mesuré : **`13ec9204`**. Intégrations `a6f0f00b`, puis **`561c1d16`** fusionnées
(`f36bea90`, `6c2a6fee`) ; seul conflit documentaire. **Lot clos, non fusionné.**

**Invariant et fonctions.** Les localisations sauvegardées, y compris leurs droits
photographiés, passent par `memoire.localisation`, `fait_brut` et `faits_connus` :
lectures pures, copies profondes, ordre historique, confiance initiale conservée.
`esprits.croyance` garde sa confiance vieillie ; les autres familles gardent leurs
politiques et leurs identités historiques. L'admission commune `admettre_fait`
reprend la séquence de `croire`, qui reste une façade compatible. Mobilité crue,
vieillissement depuis l'origine, consommation et vérification du 374, confirmation
ou retrait d'une piste vocale et validation de la preuve composée sont dans la porte.
Les opérations explicites de projection reprennent les copies des devis, les moyens
réservés et l'annulation d'un bien provisoire, sans ajouter de crochet d'admission.

Lecteurs portés : perception, recherches/contact, routes et devis observateurs,
gardes/transferts, négociation, transmission sociale, connaissance des noms, rendu
du rejeu et diagnostics. Aucun droit n'est relu depuis le réel à la réception.
Clés, dates, ordre des dictionnaires et sérialisation restent historiques ; aucun
registre ajouté. Les fonctions de passage du 381, d'avis du 395 et d'interface de
comptes du 396 ne sont pas réécrites. Recouvrement de fichiers : `planification`,
`esprits`, `agendas`, `social`, `paroles` ; seules leurs lectures communes sont portées.

**Inventaire AST.** Le contrôle supplémentaire de `test_memoire_localisation`
suit stocks, clés indirectes, alias, cellules, boucles, sélections et méthodes
détachées. Il gèle aussi les expressions dérivées : une nouvelle lecture de lieu
sous un ancien accès d'une autre famille est détectée. Inventaire syntaxique des
croyances et expressions dérivées : **1 619 → 398** ; aucune lecture directe de
localisation restante dans le moteur. Les autres familles de S1g–i, les empreintes
homonymes et les variantes de données de `tension_relais` restent gelées dans
`tests/fixtures/acces_memoire_s1a.json`. Ce comptage n'est pas celui des seuls
épisodes de S1a. Le contrôle reste local et syntaxique, sans preuve exhaustive
des flux interprocéduraux de Python.

**Vérifications acquises.** **39/39** tests de `memoire_socle`, de la nouvelle
porte et du comparateur passent (`tests-porte.json`, 100,5 s). Copies imbriquées,
confiance initiale/courante, consommation, voix et absence de création d'esprit
sont contrôlées. Aubin crue 42, minute 18, et la capture mine 7, minute 470 : même
laps entier/découpé avec recharges, état complet et ordre JSON identiques, puis
rendu, scène et registre des paroles identiques après sauvegarde/rechargement.
L'observateur courant lit aussi une référence dépourvue de la nouvelle API ;
sa vue des croyances entre dans la clé du cache des empreintes.

**Bilan consolidé : 448/451 verts**, 35 fichiers distincts, aucune erreur ni saut,
en retenant la dernière passe de chaque fichier. Les 235 tests complémentaires
corrigent tous les premiers défauts d'import et la scène Relais corrigée par le 392.
Les trois rouges sont reproduits à l'identique sur **`3d59310c`**, oracles intacts :

- `planification.MemoireTests.test_une_croyance_une_limite_ou_l_horloge_relancent_la_recherche` :
  la position expirée de Gorm conduit à inspecter plutôt qu'à demander directement ;
- `agendas_socle.ChaineTests.test_tache_payee_acceptee_puis_abandonnee` :
  soldes `(80, 20)` au lieu de `(100, 0)` ;
- `agendas_socle.ChaineTests.test_achat_apres_abandon_conserve_la_piece_due_puis_la_solde` :
  soldes `(99, 1)` au lieu de `(100, 0)`.

**Empreintes : 16/16 identiques.** Deux heures × graines 1985/7/42/2024 ×
Relais/mine/auberge/crue, contre `3d59310c`. Chronique, mesures, récit, souvenirs,
empreintes du banc, constats et état final complet concordent ; aucun plantage.
Les 16 références manquantes puis les 16 nuits de branche sont rangées dans le
cache. Avis auxiliaires identiques : zéro non justifié, vingt à expliquer.
Deux travailleurs réduits au plus, calcul détaché ; aucun temps comparé.

**Intégration et limites.** La dernière fusion apporte les terminaux du 396 et de
la documentation/scènes de tests ; aucun fichier du moteur PNJ mesuré ne change.
Les sept contrôles d'inventaire repassent après fusion. Garantie mesurée sur deux
heures ; autres familles et oubli restent hors lot. Aucun calcul restant, aucune
suite complète ni Luna.

**Bruts.** `C:/Users/msics/donjon/artifacts/s1f-397/` : `tests-premiere.json`,
`tests-porte.json`, `tests-final.json`, `empreintes-base.json`, inventaires et
attributions sur base. `fin.json` rouge reste intact ; **`fin-cloture.json`** et
`conclusion.json` consolident les preuves et les trois échecs hérités attribués.
