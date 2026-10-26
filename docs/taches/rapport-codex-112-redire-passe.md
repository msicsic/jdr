# Lot 112 — passé des échanges

Branche `codex-redire-passe`, non fusionnée ; base `8613fc9`.

Le dernier audit du tour 5 de la partie archivée `n3-soir-noir-lot102`
a été relu avant modification : **zéro obstacle**, malgré le faux refus
antérieur attribué à Ilse. Une fixture conserve ce segment et son rapport exact.
`mj._echanger` fournit maintenant `narration.echanges_passes` : toutes les paroles
entendues de chaque interlocuteur, sous sa référence publique actuelle, sans
fenêtre globale ni auditeurs privés. Le schéma demande l'extraction `rappels`
dans tous les verdicts. `controler` refuse les rappels jugés sans fondement ou
contraires, cite les mots enregistrés dans l'`attendu` et conserve l'extraction
pour la relecture à l'enregistrement. Aucun mot-clé ni cas propre à un scénario.

La vraie boucle console avec MJ simulé reproduit présentation, question de
nourriture, imposture puis tour 5 : faux rappel refusé, refus compatible affiché.
Un vrai service de Gorm diminue les vivres et la faim ; son faux rappel d'un
refus est rejeté, son rappel conforme admis. Paroles, conversation et état sont
vérifiés après recharge. L'historique ne perd pas Ilse après douze paroles d'un
autre locuteur et exclut une parole non entendue.

Luna, une passe `soir-noir` / `soir-voix`, `gpt-6-luna`, ChatGPT medium :
**39 appels**, **14,4 s/tour MJ**, aucun repli, obstacle narratif ni erreur de
rechargement. `soir-noir`, tours 1–5 : appels **5/4/4/4/6**, secondes
**18,95/12,62/13,56/12,53/19,41**. Au tour 5 : « Je ne te dirai pas qui je suis. »
après s'être nommée au tour 2, sans prétendre avoir déjà refusé.
`soir-voix`, tours 1–4 : appels **4/4/4/4**, secondes
**14,25/12,58/12,27/13,03**. Deux refus de validation dans `soir-noir` ; aucune
contradiction du passé observée. Une passe ne démontre pas une détection exhaustive.

Suite complète unique, deux processus réduits : **2 021 tests, 16 ignorés,
aucun échec ni erreur, 1 932,23 s**, 217 fichiers. Reprise ciblée finale
avec la fixture archivée : **6 tests verts, 4,37 s** ; aucune seconde suite.

Limites : la reconnaissance et la compatibilité des rappels restent sémantiques.
Le moteur impose le traitement du rappel extrait, sans garantir que l'auditeur
les extrait tous ou les juge tous correctement. Les anciens rapports restent
lisibles ; les gestes anciens reposent sur les résultats publics disponibles,
sans nouveau registre universel des actes. Le texte historique ne prouve pas
la vérité de son contenu. Aucun moteur de simulation ni scénario modifié.
Bruts : `artifacts/redire-112/` et
`artifacts/bancs-multi/20261026-054955-38148/`.
