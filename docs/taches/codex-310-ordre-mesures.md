# Tâche Codex 310 : l'ordre des mesures du banc ne dépend pas du processus

Petit correctif révélé par le lot 309. Lis son rapport, `docs/taches/rapport-codex-309-recit-buts-agenda.md`, section
« Échec préexistant ».

## Le constat
`tests/test_banc_sans_joueur` (ou le fichier qui le porte), `test_des_nuits_en_parallele_comme_une_a_une`, échoue
depuis le lot 302. La ligne « Mesures » diffère entre une nuit jouée seule et la même nuit jouée en parallèle : l'union
des clés dans `banc_pnj.executer` range les nouveaux compteurs de mandat (`banc_pnj.mesures_mandats`) dans un ordre qui
dépend du hachage du processus. Les valeurs sont égales.

## L'invariant
**Les mesures et tout texte ou empreinte qu'on en tire ont un ordre de clés déterministe, indépendant du processus et
du parallélisme.** Corrige la construction commune des mesures, pas le test. Ne change aucune valeur. Vérifie qu'aucun
autre ensemble ne sert à ordonner des sorties du banc.

## Vérification
- Le test d'origine, inchangé, vert, plusieurs fois et sous des `PYTHONHASHSEED` différents.
- Tests du banc et de l'audit des nuits.
- Empreintes 2 h, Relais et hameau, 4 graines : chronique et état identiques. Seul l'ordre des mesures peut changer ;
  dis-le si c'est le cas.
- Pas de Luna ni de suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-ordre-mesures`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur : la poussée est autorisée).
- Rapport court `docs/taches/rapport-codex-310-ordre-mesures.md`.
- Entrée dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\ordre-310\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
