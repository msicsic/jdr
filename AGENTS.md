# Instructions de développement — Le Seuil

## Règle de conception prioritaire

Ne corrige pas un comportement du jeu en ajoutant un cas particulier pour l'exemple qui l'a révélé. Cela inclut les branches liées à un objet, un lieu, un personnage, une formulation du joueur, un type de fait narratif ou une consigne supplémentaire au prompt de Luna.

Pour chaque bug, identifie l'invariant général en cause et corrige le contrat commun entre la saisie, le MJ, le moteur, le rendu et la sauvegarde. Une règle propre au scénario peut exister comme donnée ou mécanique explicite du scénario ; elle ne doit pas masquer une lacune du moteur général.

Avant de déclarer la correction terminée, vérifie la chaîne complète avec le cas réel qui a révélé le problème et au moins un autre cas de même nature. Les tests doivent contrôler l'état du monde et ce que le joueur voit après rechargement, pas seulement la réponse d'une fonction isolée.

Si l'invariant ne peut pas encore être garanti, indique clairement cette limite. Ne présente pas un traitement partiel ou une liste élargie de cas comme une solution générale.

## Contrat du MJ

Décidé le 2026-10-29 avec l'utilisateur. C'est la cible de la refonte du MJ (`docs/conception-refonte-mj.md`,
`docs/conception-valeur-llm.md`) : le gameplay d'abord, la narration est secondaire. **Transition** : une voie qui n'est
pas encore portée garde ses contrôles actuels ; un audit ne se retire que dans le lot de portage qui fournit la garantie
qui le remplace.

Luna reste le MJ du jeu avec le modèle `gpt-6-luna`. Le moteur garde l'autorité sur les positions, la perception, les
ressources, les actes de parole, les actions et les sauvegardes. La comparaison entre modèles reste désactivée.

**Ce que fait Luna.** Les gestes usuels passent par des actions directes (clic, menu, touche, commande) que le moteur
exécute sans modèle. Luna sert à ce qu'un moteur déterministe ne fait pas à coût raisonnable : comprendre une saisie
libre et la composer en plan, comprendre une négociation, suggérer des termes, admettre un détail ou un contenu de
dialogue inédit, produire l'ambiance. Elle propose ; le moteur décide de l'accord, du prix, de la croyance et de la
réalisation.

**Mécanique.** Toute information mécanique affichée (entités identifiées, positions, sorties et passages, distances,
possession, ressources, lumière, présence des PNJ, signes perçus, comptes, missions, résultats d'action, refus) provient
d'un rendu déterministe du moteur, sur les seules données perceptibles ou connues de Corvus, ou d'une proposition typée
admise par le moteur. Ses conséquences, et les paroles effectivement entendues, sont enregistrées et sauvegardées avant
l'affichage. Une parole établit qu'elle a été prononcée et entendue, sans établir que son contenu est vrai. Une
réplique de PNJ dont le moteur fixe le contenu est formulée par le moteur. Un contenu de dialogue inédit proposé par
Luna est admis comme parole enregistrée, sans effet mécanique non typé.

**Fidélité de la saisie.** Une intention compilée reste une proposition : sa validité ne prouve pas sa fidélité à la
saisie. Le joueur en est le contrôleur : le moteur affiche ce qu'il a compris (« Compris : … »), avant l'exécution pour
un acte lourd ou irréversible selon ses effets typés, après pour les autres. Une action choisie par clic ou menu n'est
pas réinterprétée. Pendant la transition, les revues de fidélité restent pour les seuls actes à effets issus d'une
saisie libre ; leur retrait se décide sur mesure.

**Interactif.** Un objet ou un détail que le joueur peut cibler existe dans l'état avant d'être manipulé. Un élément
d'ambiance ciblé est matérialisé par le contrat commun des faits interactifs ou déclaré non manipulable ; aucun texte
cosmétique n'applique un effet, une capacité, un indice ou un engagement. Une propriété inventée que le moteur ne sait
pas calculer passe une revue ciblée à son admission, pas au récit.

**Ambiance.** Aspect, odeur, son de fond, impression : une prose cosmétique distincte, produite en fond, qui ne bloque
jamais le jeu (un indicateur visible signale qu'elle est en préparation). Elle ne doit pas contenir d'erreur flagrante
qui casse l'immersion. Elle n'est jamais une source de vérité mécanique et ne crée aucune entité. Les gardes
déterministes (noms, références, voix, nombres, provenance) et, au besoin, une vérification en fond s'appliquent avant
publication ; un échec ou un doute fait jeter la sortie entière, sans relance. Une ambiance publiée est enregistrée
avec son lieu avant affichage ; une ambiance arrivée pour un lieu quitté est jetée. Ces contrôles ne garantissent pas
l'absence de toute contradiction implicite dans du français libre.

Le contrôle garantit de façon déterministe l'absence de fuite d'entités non perçues. Ne contourne pas une limite de
contrôle par un nouveau mode, un mot-clé ou une exception propre à un exemple ; renforce le mécanisme commun, ou fais
écrire le fait par le moteur.

## Travail sur ce dépôt (tous les agents : Claude, Codex et leurs sous-agents)

Le point de reprise est `docs/etat-dev.md` : à lire avant tout chantier, et à tenir à jour.

- Python : `.venv\Scripts\python.exe` (installation dans le README).
- Tests sans appel au modèle : `.venv\Scripts\python.exe -m unittest discover -s tests -q`.
  En parallèle, priorité réduite : `.venv\Scripts\python.exe tools/tests.py` (moitié des cœurs ;
  `--processus N`, fichiers en arguments ou `--motif "test_*.py"` ; durées dans
  `artifacts/durees_tests.json`, non versionné).
- Luna passe par le forfait ChatGPT. Le coffre (`donjon/connexion.py`) sérialise le renouvellement
  du jeton ; plusieurs exécutions peuvent tourner en même temps. Luna pèse peu sur le quota du
  forfait : plusieurs bancs Luna en parallèle sont permis (4 à 8 exécutions) ; comparer les temps
  de réponse dans les mêmes conditions de charge. Toujours sur des copies, jamais sur
  `sauvegardes/`. Depuis un worktree, `SEUIL_AUTH` désigne le coffre du dépôt principal.
- Tout refus `ErreurMonde` qu'une proposition du MJ peut déclencher porte un `attendu`
  (`donjon/refus.py`) : le champ fautif, la valeur reçue et ce qui serait accepté, en
  identifiants. Le message reste pour le joueur ; `attendu` ne va qu'au MJ. Une cause par
  refus : ne fusionne pas des causes distinctes dans un même message.
- Une branche par jalon ou correctif, fusionnée dans `main` avec un commit « Fusion du … ».
  Tenir `docs/etat-dev.md` à jour à chaque fin de jalon.
- Worktrees : dans `.worktrees/<nom>` à la racine du dépôt (ignoré par git), jamais à côté du
  dépôt. Les fusions se font dans `.worktrees/integration` (branche `integration`), puis `main`
  avance en avance rapide. `tmp-worktrees/` est à Codex ; `.claude/worktrees/` reçoit les agents
  isolés de Claude Code. Supprimer le worktree et la branche une fois fusionnés.
- Charge du poste : l'utilisateur travaille sur la machine qui calcule. `banc_pnj` cède la priorité
  et plafonne ses nuits simultanées à la moitié des cœurs (`--processus`). Lancer les bancs de
  `main` et de la branche l'un après l'autre, sauf quand le chantier mesure le temps de calcul ;
  pas plus de deux agents qui font des bancs en même temps ; les autres processus Python lourds
  (suite de tests longue) en priorité réduite.
## Rythme des lots

Un lot doit tenir en 30 à 45 minutes. Le temps va au code, pas à la vérification : le lourd se
fait une fois, à l'intégration, pour plusieurs lots ensemble.

- **Un invariant par lot.** Un brief qui en porte plusieurs se découpe en lots successifs.
- **Pas de référence relancée.** Les résultats de `main` (empreintes, banc rapide, Luna) se
  calculent une fois par commit de `main` et se réutilisent (`artifacts/references/<commit>/`,
  non versionné) ; un lot ne lance que sa branche. `tools/comparer_bancs.py --reference main` et
  `tools/banc_multi.py --variante main=main` résolvent la référence en commit, y lisent chaque nuit
  ou partie déjà jouée et ne jouent et rangent que celles qui manquent ; le worktree courant n'y
  entre jamais. Le temps processeur ou les secondes lus du cache ont été mesurés ailleurs : ne
  comparer des temps que lancés ensemble (`--sans-cache`). `tools/references.py lister` montre le
  cache, `purger --garder N` retire ce qui n'est plus un ancêtre de `main` ou trop ancien.
- **Vérification du lot**, le minimum qui prouve l'invariant :
  - tests ciblés pendant le travail, et les fichiers de tests que le lot touche ou que son
    changement concerne directement ; **pas de suite complète dans le lot** : le superviseur la lance
    par script, sans agent, à la fusion (une fois par fusion ou groupe de fusions) et ouvre un petit
    lot si elle révèle un échec ;
  - un changement censé ne rien changer : empreintes sur 2 h (`tools/comparer_bancs.py
    --empreintes`), seulement les scénarios touchés et le Relais, 4 graines ;
  - un changement de comportement : banc rapide, 4 h de jeu, 4 graines, mêmes scénarios ; il suffit
    pour une usurpation, une boucle ou une régression grossière ;
  - Luna, si le lot touche le MJ : **une passe**, seulement les scripts qui exercent le changement.
  - Pas de banc de 8 à 12 h, d'audit de nuits, de `VERIFIER`/`VERIFICATION` sur 8 h, ni de campagne
    Luna à deux passes dans un lot, sauf si le brief le demande expressément.
- **Calculs longs sans agent qui attend** : un banc qui dépasse une dizaine de minutes, une nuit
  de 8 à 12 h ou une campagne se lance détaché (priorité réduite, sortie dans `artifacts/`, fichier
  de fin écrit en dernier). L'agent ne le surveille pas en boucle : il termine son tour par
  `CALCUL EN COURS : <fichier de fin attendu>` ; le superviseur le relance quand le fichier existe.
  Relire un journal toutes les quelques minutes relit tout le contexte de l'agent et coûte cher.
- **Vérification à l'intégration**, groupée tous les deux ou trois lots fusionnés et lancée en fond
  pendant le lot suivant : banc complet (8 à 12 h, 8 graines, quatre scénarios et `rixe`,
  `VERIFIER`), audit des nuits, `VERIFIER` et `spatial.VERIFICATION` sur 8 h, Luna deux passes sur
  les quatre bancs de référence et les bancs ciblés. Un défaut trouvé là devient un petit lot de
  correction. À la fusion, la suite complète est relancée seulement si la branche et `main` ont
  touché les mêmes fichiers de code depuis la base.
- **Rapport d'une page** : ce qui change et pourquoi (l'invariant, les fonctions), les mesures,
  les limites. Les fils bruts restent dans `artifacts/`.

