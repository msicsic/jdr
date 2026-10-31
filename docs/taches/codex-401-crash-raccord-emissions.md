# Tâche Codex 401 : le jeu plante dans `narration.raccorder_emissions` (KeyError '0')

**Plantage du jeu**, trouvé par la vérification Luna de l'intégration (`561c1d16`, 2026-10-31, orchestrateur). Le banc
`tests/data/bancs/echanges.json` (Relais, graine 1985) plante dans les deux passes, et de nouveau quand on le rejoue
seul, sur l'intégration actuelle :

```
jeu.py:591 main -> mj.echanger -> mj._echanger_prepare (mj.py:1009)
  narration = raccorder_emissions(narration, rapport)
narration.py:896 : nouvelles = [etablis[str(i)] for i in range(len(fixes))]
KeyError: '0'
```

`segments_etablis(" ".join(fixes), audit_["faits"])` ne rend pas d'entrée pour un segment fixé par le moteur.
`raccorder_emissions` vient de G15 (lot 320) ; les lots 376 (messages selon le découpage), 390 (`ouie._au_joueur`) et 391
(parité acoustique) ont changé depuis les émissions et les paroles entendues. Les tours du banc vont de la parole à la
cantonade (« bonsoir, vous tenez le coup ? ») au chuchotement, à « à tous », au passage, à la poussée et au don. Les
passes `relais`, `crypte` et `atelier` passent. Bruts : `C:\Users\msics\donjon\artifacts\crash-echanges\` et
`.worktrees\integration\artifacts\bancs-multi\20261031-055134-40384\` (laptop).

Lis `AGENTS.md`, `docs/etat-dev.md` (court), les rapports 320, 376, 390 et 391.

## Invariant (un seul)
**Le raccord entre les paroles fixées par le moteur et la narration ne plante jamais : chaque segment fixé par le
moteur reçoit son établissement d'audit, ou le raccord le traite comme un segment établi par le moteur, sans le perdre
ni le dupliquer.** Reproduis le cas réel hors ligne : capture l'état et la réponse simulée du tour fautif à partir du
banc (`tools/banc_parties.py --fil`, ou instrumente pour sauvegarder la réponse de Luna juste avant le raccord). Trouve
pourquoi `segments_etablis` n'établit pas un segment fixé : texte joint différent du découpage, parole entendue ajoutée
par 390/391, segment vide, etc. Corrige le contrat commun ; aucune exception propre à ce tour. Bissecte entre `0bad227`
(main) et `561c1d16` si la cause n'est pas évidente.

## Vérification
Le cas réel en test hors ligne (réponse de Luna simulée, recharge, texte affiché et paroles entendues), plus un autre cas
de même nature (un autre tour de parole avec une émission fixée par le moteur). Tests touchés : `test_emissions` (ou le
fichier du 320), `test_narration`, `test_messages_decoupage`, `test_ouie_commune`. Puis **une passe Luna** du banc
`echanges` et d'un autre banc de parole (`noms-dialogue` ou `soir-appel`), sur copies ; si la revue automatique la bloque,
laisse la commande exacte dans les bruts. Pas de suite complète.

## Contraintes
**Poste : le laptop.** Lots en cours : 381 (A2 passage), 399 (rembourser), 400 (S1g) ; pendant S1, n'ajoute aucun
registre d'esprit. Deux processus au plus, priorité réduite. La poussée de ta branche vers origin
(https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-crash-raccord`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-401-crash-raccord-emissions.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\crash-raccord-401\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
