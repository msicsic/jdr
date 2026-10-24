# Tâche Codex 47 b : garder « celui d'en face », avec une seule décision d'audience

Même branche `codex-audience` (elle porte déjà le lot 47 ; ce fichier s'y ajoute), même worktree
`tmp-worktrees/`. **Lot court** (`AGENTS.md`, « Rythme des lots »). Luna disponible sur ce poste.

## La décision de l'utilisateur (2026-10-24)
Le lot 47 a remplacé la règle d'adresse établie depuis la branche `parole` (« celui qu'il nomme, sinon celui qui est
en face ») par « sinon la cantonade, même avec quelqu'un en face ». **L'utilisateur la refuse** : « pour parler à tout
le monde, il suffit de dire « à tous » ». Le brief du lot 47 y poussait (« fais-en une seule décision »), c'est
l'erreur du brief, pas la tienne.

## Ce qu'il faut faire
Garder ce que le lot 47 a bien établi — **une seule décision d'audience, celle de `paroles.destinataires`**, que la
prévision, la préparation et Luna suivent (une proposition contraire est refusée avec `attendu` avant la revue), la
contre-revue ne jugeant plus que les mots et le contenu, et jamais « Précise à qui tu t'adresses » quand la règle
donne une audience — mais **rétablir la règle d'adresse établie** dans cette décision unique :
- nom ou vocatif : cette personne ;
- groupe explicite (« à tous », « à vous deux »…, la forme déjà reconnue) : ce groupe ;
- échange poursuivi : le même interlocuteur ;
- **sinon celui qui est en face** (la règle de la branche `parole`, égalité comprise : le joueur précise) ;
- **personne en face** : la cantonade, avec les répondants de `parole-corrections` (« Répondre à la cantonade »).
Chuchotement et « lui » sans antécédent : inchangés.

Conséquence voulue : « est-ce que quelqu'un a du bois ? », Aubin en face, va à Aubin ; Aubin répond ; les autres
saisissent les mots par l'ouïe commune sans répondre ; aucun « Précise à qui… ». Les tests du lot 47 qui attendaient
la cantonade avec quelqu'un en face s'adaptent (dis chacun) ; les anciennes scènes que le lot 47 avait rendues
explicites peuvent reprendre leur forme d'origine si elles passent. Mets à jour `docs/plan-ouie.md`,
`docs/contrat-mj.md`, `docs/etat-dev.md` et le rapport du lot 47 (une section « 47 b »).

## Vérification (minimale)
- Tests ciblés : `test_audience` (le cas réel du Relais : à Aubin, sans « Précise… » ; personne en face : la
  cantonade et ses répondants ; « à tous » : le groupe ; vocatif ; échange poursuivi), puis les fichiers que le
  lot 47 avait touchés.
- Luna, **une passe** : `noms-dialogue`, `soir-appel`, `echanges`, `relais`, référence `main` lue du cache ; appels
  par tour, texte affiché pour la question du bois.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

Commits signés, branche poussée (pas `main`).
