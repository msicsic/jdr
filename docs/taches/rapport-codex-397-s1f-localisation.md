# Lot 397 — S1f, localisation crue et preuves de possession

31 octobre 2026 · `codex-s1f-localisation` · base exacte `integration 3d59310c`.
Code figé pour les mesures : **`13ec9204`**. Intégration `a6f0f00b` fusionnée
(`f36bea90`) : documentation et scènes de tests du 392, aucun code moteur.
**Portage réalisé ; vérifications complémentaires et empreintes en cours.**

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

Première passe : 219 tests, 208 verts, deux échecs et neuf erreurs. Les erreurs
proviennent des imports de `memoire` manquants pendant cette passe, corrigés avant
le gel du code ; leurs fichiers sont repris. L'échec de scène Relais est corrigé
par le 392 intégré. L'autre, `planification.MemoireTests.
test_une_croyance_une_limite_ou_l_horloge_relancent_la_recherche`, se reproduit à
l'identique sur **`3d59310c`** : inspection de la position expirée de Gorm, au lieu
de la demande attendue par l'ancien oracle. Aucun changement de cet oracle.

**Calcul détaché.** `run-final.ps1` reprend les trois fichiers corrigés et quatorze
fichiers directement concernés, puis lance les empreintes **2 h × quatre graines
1985/7/42/2024 × Relais/mine/auberge/crue**, contre `3d59310c`, avec cache, référence
puis branche, deux travailleurs au plus et priorité réduite. Aucun temps CPU
comparé, aucune suite complète ni Luna. Ne pas déclarer les empreintes identiques
avant lecture de `empreintes-base.json`. Résultats et fin écrite en dernier :
`C:/Users/msics/donjon/artifacts/s1f-397/fin.json`.

**Reprise.** Lire `fin.json`, `tests-final.json` et `empreintes-base.json`, attribuer
tout rouge nouveau, puis consolider ce rapport et l'entrée d'état. Bruts, premiers
résultats, inventaires et attribution de la base sont dans le même dossier.
Les contrôles d'identité sur les seize nuits restent une condition de clôture.
