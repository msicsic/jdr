# Tâche Codex 295 : la suite complète après G2, G4 et U-D

Petit lot de correction. La suite complète lancée par le superviseur sur l'intégration `8acbbd9` (G2 et G4 fusionnés,
avant U-D) donne **2 759 tests, 15 échecs et 9 erreurs**. Le journal complet est sur ce poste :
`C:\Users\msics\donjon\artifacts\suite-g2g4-8acbbd9\suite.log`. Lis `AGENTS.md` (« Contrat du MJ »),
`docs/plan-refonte-mj.md` et les rapports `docs/taches/rapport-codex-291-g2-refus-moteur.md` et
`rapport-codex-292-g4-resultat-public.md`.

## Les échecs
Ils sont tous dans des parcours qui simulent la suite des appels au modèle :
- `test_websocket_jeu` (reconnexion aux quatre étapes, coupure sans fragment, deux scènes) ;
- `test_fournisseurs_jeu` (OpenAI HTTP, Anthropic, MiMo : erreurs) ;
- `test_restes_fusions` (MiMo après reprise) ;
- `test_cache_kv_local` (parcours local) ;
- `test_parole_corrections` (refus de forme non montré) ;
- `test_sans_message_technique` (description mal formée, corrigée ou repliée) ;
- `test_luna_noms` (approche structurée).

Plusieurs attendent encore les étapes `repondre_au_joueur` / `auditer_narration` après une exécution, retirées par G4,
ou l'explication libre d'un refus, retirée par G2. Au moins un pourrait être une vraie régression :
`test_sans_message_technique` attendait un repli de perception (« mur », « bobine »). Il reçoit maintenant « Précise la
manœuvre que tu veux tenter. Corvus n'a rien tenté. »

## Ce qu'il faut faire
Pour chaque test en échec, sur la base actuelle de l'intégration (elle contient aussi U-D) :
1. Attribue-le au lot qui l'a cassé (G2, G4 ou U-D), en le rejouant sur le commit de fusion précédent si nécessaire.
2. Classe-le :
   - **attente périmée par le nouveau contrat** : l'étape de récit après exécution, ou l'explication libre d'un refus
     (contrat du MJ, « Mécanique », et clause de transition). Adapte le test pour vérifier la nouvelle garantie (rendu
     moteur exact, zéro récit ou audit après exécution, refus public exact), sans affaiblir le reste : reconnexion,
     exécution unique, absence de fragment, sauvegarde avant affichage, reprise ;
   - **régression** : le test protège une garantie que le contrat garde. Exemple : une demande de description dont
     la forme reste invalide doit donner au joueur ce qu'il perçoit, pas un « précise » (lot 100). Corrige le code
     commun, sans cas propre à l'exemple, et vérifie le cas réel et un autre de même nature après recharge.

   En cas de doute entre ces deux classes, pose la question au lieu de trancher.
3. Rejoue seulement les fichiers concernés, plus ceux que tes corrections de code touchent.

Pas de Luna (ces tests sont simulés), pas de banc, pas de suite complète : le superviseur la relancera.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-suite-g2-g4` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) ; si la
  poussée échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-295-suite-g2-g4.md` : un tableau des échecs (test, lot, classe,
  correction).
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\suite-295\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.
