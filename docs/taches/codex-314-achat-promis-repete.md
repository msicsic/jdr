# Tâche Codex 314 : une promesse d'achat annulée ne se ré-annonce pas sans entrée nouvelle

Défaut révélé par le lot 306 (`codex-a5-agenda-hameau`, non fusionné : agenda d'évacuation de Gorm dans le hameau).
Lis son rapport `docs/taches/rapport-codex-306-a5-agenda-hameau.md` sur sa branche (section « Achat promis, 7 »), et ses
bruts sur le PC fixe : `C:\Users\msics\donjon\artifacts\agenda-hameau-306\reprise-309\` (`diagnostic-7/`,
`diagnostic-7-choix.json`, `hameau-7-*`).

## Le constat
Hameau, graine 7, avec l'agenda du 306 : Aubin fait **28 annonces** d'un achat promis entre t=36582 et 39282.
La sonde relève **26 comparaisons successives sans entrée nouvelle**, au même lieu, pour la même promesse de la
minute 0, alors que l'engagement est annulé. Il n'y a aucun nouveau paiement. La sonde 219 ne le classe pas en retour
A→B→A, mais c'est bien une intention qui se répète sans cause, invisible à la seule classification des retours.

## L'invariant
**Une promesse ou un engagement annulé ou soldé ne produit plus d'annonce ni de geste. Une même parole ne se répète
qu'après une entrée nouvelle (croyance, moyen, réponse, échéance réelle), jamais par le seul choix renouvelé.** Établis
d'abord la cause. Est-ce l'annulation de l'engagement que le choix ne lit pas ? Ou une annonce rejouée à chaque
délibération ? Ou un plan qui recommence sur un état qu'il n'a pas changé ? Corrige le contrat commun
(`agendas`, `echanges`, `deliberation`), sans cas propre à Aubin ni au hameau, ni délai.

## Base et reproduction
Base `integration`. Reproduis sur une capture rechargée du 306 : fusionne localement la branche
`origin/codex-a5-agenda-hameau` dans un worktree temporaire, ou recharge directement ses captures. **Ne modifie pas
les données du hameau.** Ta branche part d'`integration`, sans les données du 306.

## Vérification
- La capture de la graine 7 avant t=36582 rechargée : une annonce au plus, puis plus rien sans entrée nouvelle.
  Vérifie aussi que monde, rendu et scène sont identiques après recharge, et que le résultat est le même avec un laps
  d'un bloc ou découpé.
- Un autre cas de même nature, dans un autre scénario.
- Empreintes 2 h, Relais, mine, auberge et crue, 4 graines.
- Banc rapide : le hameau avec les données du 306, 4 h × 4 graines, sur un worktree temporaire. Les annonces répétées
  disparaissent, sans hausse des suspects. Calcul détaché.
- Pas de Luna ni de suite complète.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite. Un autre lot (315) traite les réclamations répétées
de Sève : ne le chevauche pas.

## Livraison
- Branche `codex-achat-promis`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur : la
  poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-314-achat-promis-repete.md`.
- Entrée dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\achat-314\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
