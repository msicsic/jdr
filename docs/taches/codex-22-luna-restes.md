# Tâche Codex 22 : les restes de Luna (forme d'un obstacle, fidélité, cases dans le récit, ambiance)

Branche `codex-luna-restes` (elle porte ce fichier, issue de `main` 8855312), worktree dans `tmp-worktrees/`.
Lis d'abord `AGENTS.md`, `docs/contrat-mj.md`, `docs/etat-dev.md` (entrées `codex-luna-noms` et sa fusion,
`codex-sous-obstacle` et sa fusion, `relances-luna`, `parole-corrections`, et « À revoir » : Luna après
`codex-luna-noms`, « passer sous un obstacle »), `docs/banc-luna-soir.md`, `docs/reverification.md`, puis
`donjon/mj.py`, `donjon/narration.py`, `donjon/consignes.py`, `donjon/coherence_physique.py`,
`donjon/faits_locaux.py`, `donjon/obstacles.py` (forme d'un passage), `tools/banc_parties.py`, `tools/banc_multi.py`.

**Luna disponible sur ce poste** (`SEUIL_AUTH` vers le coffre du dépôt principal ; toujours sur des copies,
jamais sur `sauvegardes/` ; 4 exécutions en parallèle au plus).

Deux autres lots tournent en même temps : Q (trajets réels, autre poste : `planification.py`, `obstacles.py`
pour le coût de route, `part_estimee.py`, `defense.py`, `pnj._marcher`) et R (signes, ce poste : `signes.py`,
`relations.py`, `spatial.etat_signes`, et le refus local d'« observer » dans `commandes`/`jeu.py`). **Ne touche
ni `planification.py`, ni `deliberation.py`, ni `signes.py`, ni la commande `observer`.** Dans `obstacles.py`,
seulement ce qui établit ou vérifie la forme (pas le coût de route) ; si un invariant exige d'aller plus loin,
change le minimum, isole-le dans un commit à part et dis-le.

## Les constats (tous vus dans des bancs Luna récents)
1. **Forme inconnue d'un obstacle** (banc `sous-obstacle-inconnu`, fusion de O) : « est-ce que je pourrais passer
   sous la poutre ? », la poutre sans forme décrite. Luna essaie d'établir la forme (`etablir_faits`,
   qualification) ; la contre-revue physique refuse toute qualification (« rien n'établit un vide sous elle »),
   5 à 7 appels avant le refus du moteur (« Le dégagement sous l'obstacle et sa hauteur ne sont pas encore
   décrits. »). Le contrat dit qu'une forme peut être établie par le MJ et vérifiée par le moteur : soit elle
   doit pouvoir l'être (plausible, compatible avec le nom, le texte et la masse), soit le moteur doit dire tout
   de suite ce qui manque. Tranche, par une règle commune à toute description physique, et justifie.
2. **Contre-revue de fidélité trop stricte** : une question « à quelqu'un » posée à la cantonade
   (« est-ce que quelqu'un a du bois ? », banc `noms-dialogue`) jugée individuelle, relancée ; `tous` jugé
   individuel ; un achat dit sans transfert. Le contrat de l'audience (individuelle, groupe, cantonade) est
   dans `docs/contrat-mj.md` : ce qui est déterministe ne doit pas dépendre du jugement de l'auditeur.
3. **Positions en cases dans le texte affiché** : un récit situe un objet hors de vue « à deux cases vers le sud
   et deux vers l'est », la poutre « à une case vers l'est » ; le refus du monde montré à la place d'une
   explication porte « case 5, 11 du plan » (`relances-luna`, limite). Le joueur ne lit jamais d'unité du moteur
   (case, coordonnée) : il lit des directions, des distances en pas ou en mètres, ou des repères. Trouve d'où
   vient chaque forme (contexte envoyé, refus du moteur, consignes) et corrige à la source, plus un contrôle
   déterministe du texte affiché s'il en manque un (le méta-langage est déjà refusé : étends ce mécanisme, pas
   une liste de mots propre à un exemple).
4. **Ambiance assortie d'une précaution** : une ambiance libre (« des bruits lointains ») suivie de « rien de tel
   ne t'est perceptible » ou d'une réserve semblable : soit l'ambiance est admise et dite sans précaution, soit
   elle est refusée. Trouve ce qui pousse Luna à cette précaution (consignes, verdict de l'auditeur relancé) et
   corrige le contrat commun.

Pour chacun : l'invariant général, jamais le cas de l'exemple (`AGENTS.md`). Le contexte des lots suivants est
dans `docs/plan-agendas.md` (Luna y recevra plus tard ce qu'un PNJ est prêt à dire) : ne l'anticipe pas.

## Vérifications
- Tests après rechargement (`tests/test_luna_restes.py`), sans modèle (réponses simulées) : chaque constat avec
  son cas réel et un autre de même nature (un autre obstacle sans forme, une autre question à la cantonade, un
  autre objet hors de vue, une autre ambiance) ; ce que lit le joueur et l'état après rechargement.
- Suite complète verte (`tools/tests.py --processus 3`).
- Empreintes : rien ne doit changer pour les PNJ (`tools/comparer_bancs.py --empreintes`, 2 h, quatre scénarios
  × 4 graines, contre 8855312) ; si un changement de forme d'obstacle touche les données, dis-le et mesure.
- **Luna** (`tools/banc_multi.py`, `main` 8855312 puis la branche, 2 passes chacune lancées ensemble) : les quatre
  bancs de référence (`relais`, `crypte`, `atelier`, `echanges`), `noms-dialogue`, `soir-appel`, `soir-noir`, les sept `sous-obstacle-*`, `force-4c-fuir` ;
  appels et secondes par tour MJ, relances, refus, replis ; textes relus (aucune case ni coordonnée, aucune
  précaution d'ambiance, la question à la cantonade sans relance, la forme inconnue en au plus 3 appels avec
  une réponse juste). Si un banc nouveau est utile (objet hors de vue, ambiance), crée-le dans `tests/data/bancs`.
- Docs : `docs/contrat-mj.md` (les règles changées), `docs/etat-dev.md` (« Branche `codex-luna-restes`, non
  fusionnée », compte de tests ; « À revoir » mis à jour).

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-22-luna-restes.md` : chaque constat, sa cause lue dans les fils (`--fil`), l'invariant,
les fonctions, les cas vérifiés, les bancs avant → après, les limites (ce qui reste sémantique).
