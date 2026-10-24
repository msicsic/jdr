# Tâche Codex 50 : le moteur et la contre-revue lisent la même demande de ressource

Branche `codex-ressource` (elle porte ce fichier, issue de l'intégration **d60b80a** : lots 38 à 49 compris),
worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un invariant,
vérification minimale, rapport d'une page. **Luna disponible sur ce poste** (`SEUIL_AUTH` vers le coffre du dépôt
principal ; copies seulement). `tools/banc_multi.py` joue par défaut avec la connexion anthropic : passe
`--connexion chatgpt`.

D'autres lots tournent sur l'autre poste (`planification.py`). Ne touche pas à ce fichier.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-audience` lots 47 et 47 b, `codex-luna-restes` : « sens des
contenus typés partagé entre interprétation et revue », `echanges-suite` : « As-tu du bois ? »), `docs/contrat-mj.md`,
puis `donjon/paroles.py` (`BESOINS_DEMANDES`, la validation du contenu `ressource` vers la ligne 1200),
`donjon/echanges.py` (`enqueter`), `donjon/mj.py` (la boucle de correction vers la ligne 772, la contre-revue de
fidélité), `donjon/couverture_action.py` (`contenu_conforme`, le sens des contenus). Bruts :
`C:\Users\msics\donjon\artifacts\luna-47b-final\relecture.txt` (`noms-dialogue`, `soir-appel`).

## Le constat (passe Luna sur le code final du lot 47 b)
« est-ce que quelqu'un a du bois ? », Aubin en face : l'adresse est juste (Aubin), mais le joueur lit « Précise ce
que tu veux dire : les mots ou le contenu proposés ne correspondent pas à ta demande. » et rien n'est dit, dans les
deux scripts. Luna type `ressource` sujet `chaleur` ; la contre-revue refuse (« la demande porte sur du bois, le
contenu demande une ressource pour se chauffer, notion plus large ») ; Luna repropose `sujet: "bois"` ; le moteur le
refuse sans revue (`BESOINS_DEMANDES` : `faim` ou `chaleur`, « Corvus ne dit pas ce qu'il cherche ») ; au deuxième
refus, la boucle affiche le message. **Le moteur exige ce que la revue refuse.**

## L'invariant
**Un contenu typé a un seul sens, que le moteur et la contre-revue partagent : la revue ne peut pas refuser la seule
forme que le moteur accepte pour ces mots, et le moteur accepte une forme qui dit ce que le joueur demande s'il sait
y répondre.** Choisis la voie commune et justifie-la : par exemple, que `ressource` porte ce que le joueur nomme
(un bien, une substance, une catégorie que `enqueter` sait chercher dans ce que l'autre croit avoir) en plus du besoin
qu'il sert, ou que le sens partagé de `ressource/chaleur` dise ce qu'il couvre et que la revue juge sur ce sens. Pas
de mot-clé « bois » ni de cas de cette question : un autre bien demandé (« as-tu une lampe ? », « as-tu de l'huile ? »,
« as-tu à manger ? ») doit suivre la même règle. Et jamais « Précise ce que tu veux dire » quand le moteur et la
revue ont une forme commune pour les mots du joueur.

Hors de ce lot, à signaler seulement : l'élision cassée dans la projection publique d'un nom (« Je me méfie d'Le vieil
homme voûté. », dossier du chuchotement, `echanges`).

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : le cas réel (Relais, Aubin en face, « est-ce que
  quelqu'un a du bois ? » : Aubin répond selon ce qu'il croit avoir, rien d'affiché comme refus) ; un autre bien
  demandé de même nature (auberge ou mine) ; un contenu vraiment contraire aux mots, toujours refusé.
- Luna, **une passe** : `noms-dialogue`, `soir-appel`, `ressources` (`tests/data/bancs/ressources.json`), `echanges`,
  référence `main` lue du cache ; appels par tour, texte affiché pour chaque question de ressource.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md` (le sens partagé de `ressource`),
`docs/etat-dev.md` (« Branche `codex-ressource`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-50-ressource.md` (cause, invariant, fonctions, mesures, limites).
