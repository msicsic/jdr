# Tâche Codex 54 : un nom public s'accorde comme tout groupe nominal

Branche `codex-elision` (elle porte ce fichier, issue de l'intégration **5125d06** : lots 38 à 51 compris), worktree
dans `tmp-worktrees/`. **Lot court** (`AGENTS.md`, « Rythme des lots ») : un invariant, vérification minimale,
rapport d'une page. **Luna disponible sur ce poste** (copies seulement ; `tools/banc_multi.py --connexion chatgpt`).

Lots en même temps sur l'autre poste : 52 (`planification.py`), 53 (`deliberation.autour`, `signes.py`). Ne touche
pas à ces fichiers.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-noms`, `codex-noms-lisibles`, `codex-audience`, `codex-ressource`),
puis `donjon/francais.py` (`de`, ligne 56 et 66), `donjon/noms.py` (projection publique, `nom`, ligne 244),
`donjon/social.py` (ligne 362), et ce qui écrit le `sujet` d'une conversation validée. Bruts :
`C:\Users\msics\donjon\artifacts\luna-47b-final\relecture.txt` (`echanges`, le chuchotement).

## Le constat
Dans le dossier du MJ, le sujet de la conversation validée d'un chuchotement devient « Je me méfie d'Le vieil homme
voûté. » : la projection publique d'un personnage dont le joueur ignore le nom (« le vieil homme voûté ») est collée
après une préposition élidée ou contractée sans être accordée (« du vieil homme voûté », « de la batelière »,
« de l'homme »). Trois fonctions au moins font l'élision chacune à sa manière (`francais.de`, `noms`, `social`).

## L'invariant
**Toute désignation insérée après une préposition (de, à) ou un article passe par une seule fonction d'accord du
français** : article défini contracté (du, des, au, aux), élision (d', l'), majuscule de début seulement en tête de
phrase, nom propre sans article. Les trois implémentations deviennent une, appelée partout où un nom, une désignation
publique ou un `personne_<n>` projeté entre dans une phrase. Pas de cas propre au « vieil homme » ni au chuchotement.

## Vérification (minimale)
- Tests : la fonction commune sur les formes (nom propre, défini masculin/féminin/pluriel, élidé, indéfini,
  majuscule) ; la chaîne réelle (chuchotement à Brune sur le vieil homme, `echanges`) après rechargement : sujet
  « Je me méfie du vieil homme voûté. » ; un autre cas de même nature (une rumeur ou une nouvelle sur une personne
  désignée, dans le récit du joueur).
- Empreintes 2 h, Relais et auberge, 4 graines (`tools/comparer_bancs.py --empreintes --reference 5125d06`) : seuls
  les textes peuvent changer ; dis lesquels.
- Luna, **une passe** : `echanges`, `noms-dialogue` ; textes affichés.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/etat-dev.md` (« Branche `codex-elision`, non fusionnée »).
Rapport d'une page : `docs/taches/rapport-codex-54-elision.md`.
