# Tâche Codex 18 : rendre lisible le code des noms (sans changer le comportement)

Branche `codex-noms-lisibles` (elle porte ce fichier, issue de `main` 276524c), worktree dans `tmp-worktrees/`.
Lis d'abord `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-noms`, `codex-luna-noms`, `codex-restes-fusions`),
`docs/taches/rapport-codex-2-noms.md`, `docs/taches/rapport-codex-8-luna-noms.md` et `docs/contrat-mj.md`.

**Pas de Luna sur ce poste** : ce lot n'en a pas besoin (le contexte envoyé au MJ doit rester identique octet
pour octet, ce qui se prouve sans modèle).

## Le constat
À la relecture des fusions, le code des noms est jugé trop dense pour être relu et modifié sans risque :
`donjon/noms.py` (321 lignes) en est le cœur — `texte`, `public`, `reference`, `verifier_references` et
`verifier` tiennent des règles distinctes dans des expressions d'une ligne, des lambdas imbriquées, des
`import` locaux répétés, des noms d'une lettre ; le calcul d'un numéro neuf est écrit deux fois (`designation`
et `reference`) ; les variantes d'un nom (`reel`, `reel.split(',')[0]`, `reel.split()[0]`) et leur motif
`(?<!\w)…(?!\w)` sont refaits à plusieurs endroits. Le même style se retrouve dans les ajouts de `codex-noms` et
`codex-luna-noms` ailleurs (`voix.py`, `paroles.py`, `narration.py`, `mj.py` : fonctions de noms, de
présentation, de clarification nominale, de contre-revue de fidélité).

## Le travail
1. Réécrire `donjon/noms.py` pour la lecture, dans le style du reste du dépôt (docstrings et commentaires en
   français, une règle par fonction, noms parlants, pas de lambda imbriquée dans un `re.sub` quand une fonction
   nommée le dit mieux) : une seule fonction pour les variantes d'un nom et leur motif ; une seule pour le
   numéro d'une personne ou d'un élément ; `public` séparé en « quels champs gardent les citations » et « la
   projection » ; `verifier_references` et `verifier` lisibles ligne à ligne. Les `import` locaux qui évitent
   un cycle restent locaux, mais une fois par fonction et commentés si le cycle n'est pas évident.
2. Même travail, limité aux fonctions de noms ajoutées par `codex-noms` et `codex-luna-noms`, dans `voix.py`,
   `paroles.py`, `narration.py` et `mj.py` (liste-les dans le rapport). Ne touche pas au reste de ces fichiers.
3. **Aucun changement de comportement.** Les signatures publiques restent (`connait`, `apprendre`,
   `designation`, `nom`, `resoudre`, `texte`, `reference`, `public`, `verifier_references`, `references`,
   `entendre`, `presenter`, `verifier`, `PERSONNES`, `CHAMPS_REFERENCES`, `LISTES_REFERENCES`), ainsi que les
   messages et les `attendu` des refus. Si tu trouves un défaut en relisant, ne le corrige pas dans ce lot :
   écris-le dans le rapport avec un test qui le montre (marqué `expectedFailure`), pour un lot suivant.

## Preuve d'identité
- **Contexte du MJ identique** : écris un petit outil (ou un test) qui, pour chaque scène de `tests/data/bancs`
  et chaque capture de `tests/data/scenes`, charge le monde et calcule ce que reçoit le MJ (contexte complet
  projeté par `noms.public`, références, rendu de la scène et du bilan pour le joueur) ; compare l'ancien code
  (`main` 276524c, par un worktree temporaire) et le nouveau : identiques octet pour octet. Ajoute des cas
  difficiles construits (dépouille d'un défunt connu ou non, voix qui se dit / qu'on appelle, élément porté par
  une personne inconnue, homonymes de désignation, citations entre guillemets contenant un nom).
- `tools/comparer_bancs.py --empreintes`, 2 h puis 8 h, quatre scénarios × 4 graines, contre 276524c :
  identique.
- Suite complète verte (`tools/tests.py --processus 3`) ; `pyflakes` sans nom indéfini sur les fichiers touchés.
- Mesure du temps de `noms.public` et `noms.texte` sur le corpus, avant → après (il ne doit pas augmenter de
  plus de 5 % ; s'il baisse, tant mieux, mais ce n'est pas le but).

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-18-noms-lisibles.md` : fonctions réécrites, règles qu'elles portent (une phrase
chacune), preuve d'identité, défauts relevés non corrigés, limites. Mets à jour `docs/etat-dev.md`
(« Branche `codex-noms-lisibles`, non fusionnée »). D'autres branches sont en cours (relations 3c en fusion, qui
rend des signes avec des noms ; part estimée ; force 4c) : garde les signatures et les fichiers hors périmètre
intacts.
