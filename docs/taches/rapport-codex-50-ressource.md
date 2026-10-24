# Lot 50 — même demande de ressource

Branche `codex-ressource`, non fusionnée ; base `d60b80a`, brief `d24e7d5`.

**Cause, invariant et fonctions.** Le moteur exigeait `faim`/`chaleur` ; la revue
refusait l'élargissement de « bois », puis le moteur refusait la correction littérale.
`ressource.sujet` conserve désormais le bien nommé, même inconnu de Corvus ; les
besoins généraux gardent leurs codes. `paroles.verifier_contenus`, `_typer`, le schéma,
`SENS_CONTENU` et `sens_contenu` partagent ce contrat. `echanges.enqueter` utilise
`correspond_ressource` : suites de mots entières dans identifiant, nom, alias,
matière, type ou catégorie explicite, parmi les possessions connues du PNJ,
avec lieu et disponibilité crus. Aucun transfert ni capacité déduite.
`couverture_action.entree` préserve les sujets littéraux : « bois » ne devient pas
le nom d'un objet caché dont ce serait l'identifiant. Aucun changement propre à
une question, du modèle, des scénarios ou de `planification.py`.

**Tests et banc.** Six nouveaux tests `test_ressource_nommee`, avec console/MJ simulé
et recharge : Relais/Aubin/bois, auberge/Lucien/lampe portée (alias) et huile absente,
correction `chaleur` → `bois`, contenu contraire refusé, possession ignorée non
révélée et sujet vide avec `attendu`. Biens inchangés, dossier de revue et texte
sauvegardé contrôlés. L'ancien refus de `bois` devient une réponse de Joss.
Suite complète unique (`tools/tests.py --processus 3`) : **1 760 tests, 16 ignorés, 170 fichiers verts**, 1 929,2 s, priorité réduite. Le lot dépasse 45 minutes à cause de cette suite de 32 minutes ; aucun banc lourd supplémentaire. Brut : `artifacts/tests-ressource.json`.

Banc rapide, référence puis branche, deux processus à priorité réduite : Relais et
auberge, 4 h × graines 1985/7/42/2024. Huit paires de chroniques, empreintes aux relevés,
récits et souvenirs identiques ; mêmes mesures, zéro usurpation/violation, mêmes
audits (un `noir_long` dans l'auberge). Base calculée une fois puis mise en cache.
Brut : `artifacts/banc-ressource.json`.

**Luna : une passe effective par script**, ChatGPT, copies et coffre principal.
`main` `42bb9c0` lu du cache (première passe, empreintes des trois scripts identiques).

| Script | Appels/tour MJ main → branche | Questions de ressource affichées |
|---|---:|---|
| noms-dialogue | 3,00 → 3,00 | Bois, 4 appels : question dite à Aubin ; il dit avoir ses planches. |
| soir-appel | 3,60 → 4,25 | Bois, 4 appels : même réponse ; nourriture à Ilse, 3 appels : « Non, je n'ai rien à manger. » |
| echanges | 2,75 → 3,67 | Aucune question de ressource. |
| ressources | absente → 3,00 | Bois à Aubin et nourriture à Brune, 3 appels chacun : planches disponibles / « Non, je n'en ai pas. » |

Périmètre comparable : **41 → 40 appels, 13 → 11 tours MJ, 3,15 → 3,64 appels/tour**.
Avec `ressources` : **49 appels / 14 tours MJ**. Aucun faux refus sur ces demandes,
repli, erreur technique ou recharge invalide. `ressources`, absent du cache, avait
d'abord fait zéro appel (noms inconnus) : préparation corrigée, puis une passe effective.
Le premier script précède la correction finale de projection, vérifiée par simulation,
sans deuxième passe Luna. Bruts/relecture : `artifacts/bancs-multi/20261024-212809-31572/`,
`artifacts/luna-50-ressources/`, `artifacts/luna50-relecture.txt`.

**Limites.** Correspondance lexicale, sans synonymes ni inflexion grammaticale générale ;
aucune garantie d'usage du bien. Fidélité toujours sémantique, sans garantie générale
contre les faux refus. Hors lot : question sur le gardien encore refusée dans `echanges`,
réponse de dette inversée dans `ressources`, élision d'un nom public à corriger séparément.
Aucune conclusion causale sur les temps du cache. `main` non modifiée.
