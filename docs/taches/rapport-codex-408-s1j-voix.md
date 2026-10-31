# Lot 408 — S1j, identité vocale et noms retenus

31 octobre 2026 · `codex-s1j-voix` · base exacte `integration 44745a89`.
Code soumis aux empreintes : **`bea3d8ec`**. **Vérification des empreintes en cours ; lot non clos.**

**Invariant et code.** Les voix connues et entendues, leurs signatures, prétentions,
appellations et méfiances, les noms appris et les échanges retenus passent par
`donjon/memoire.py`. Les vues `voix_connues`, `voix_entendues`, `noms_retenus` et
`echange_retenu` rendent des copies pour un observateur explicite, sans création
d'esprit ni apprentissage. Les écritures nommées retiennent l'audition, la prétention,
l'appellation, la méfiance et le nom ; `reconnaitre_voix` conserve l'ordre des liens,
du démasquage différé, des épisodes et de la révision de localisation vocale.
`voix` et `noms` gardent leurs façades et leurs décisions d'identification/exposition.

Installation, migration et validation sont également portées. `esprits`, `ecoute`,
`relations`, le contexte de `Monde`, `perception` et les métriques de `banc_pnj`
consomment la porte. L'outil `comparer_noms` et trois fixtures de tests sont adaptés
au retrait des retours mutables ; aucune assertion de sécurité n'est retirée.
Les clés et l'ordre historiques restent conservés : 24 voix, éviction par date/rang,
8 paroles par échange de 600 dixièmes, reconnaissance distincte du nom appris,
prétention distincte de l'identité, désignation `voix_<n>` et genre public inchangés.
Aucun nouveau registre, oubli, jugement social ou appel au modèle.

**Contrôle et tests.** Inventaire vocal AST **98 → 17 expressions** : une déclaration
exacte de schéma et seize homonymes (acoustique, propositions de paroles, diagnostics
et données d'auteur) gelés dans `voix_homonymes_s1j`. **Zéro accès aux registres vocaux
restant hors porte.** Le contrôle S1j paramétré couvre clés indirectes, alias, méthodes
détachées, boucles, créations, retours et mutations ; les inventaires antérieurs passent.
**217/217 tests distincts verts, seize fichiers**, dont sept nouveaux tests.
Copies imbriquées et admissions protégées, saturation/date/rang, migration depuis
une voix absente et corruptions sont contrôlées. Chaînes : les deux régressions
historiques de présentation de Corvus (vu, puis voix nommée dans le noir et reconnue),
imposture de Brune démasquée par la voix d'Ilse et capture de la mine à 470 minutes.
Deux minutes entières ou quatre tranches avec recharges donnent le même état complet,
ordre JSON, lignes, rendu, scène et paroles. Les premiers essais ont révélé une fixture
écrivant dans un retour désormais copié, une migration testée avant son installation,
puis un compteur local masquant l'import de mémoire dans le banc ; tous sont corrigés.

**Empreintes et reprise.** Calcul détaché contre la base exacte : 2 h × quatre graines
1985/7/42/2024 × Relais/mine/auberge/crue, deux travailleurs réduits, référence puis
branche, cache partagé sans relance des nuits disponibles. Résultat attendu dans
`C:/Users/msics/donjon/artifacts/s1j-408/fin.json` ; lire aussi `empreintes-base.json`
avant de clore le lot. Aucun résultat d'identité n'est encore revendiqué.

**Limites et voisinage.** Contrôle AST syntaxique/local, sans preuve de tous les flux
interprocéduraux Python ; politiques et limites historiques conservées. Pas de suite
complète ni Luna. Aucun fichier attendu du 407 n'est modifié ; le 402 reste un calcul
d'intégration indépendant. `origin/integration` est resté à `44745a89` à la dernière
actualisation ; aucune fusion supplémentaire nécessaire. Bruts :
`C:/Users/msics/donjon/artifacts/s1j-408/`, avec
`bilan-tests.json`, tests détaillés, inventaire et lanceur `run408.py`.
