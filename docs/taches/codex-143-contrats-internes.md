# Tâche Codex 143 (MJ) : aucune explication affichée n'expose les contrats internes du moteur (N10)

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`,
copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus
2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche le contrôle de la voix d'auteur et l'audit
narratif (`narration.py`) et, si besoin, les consignes (`consignes.py`) ; **pas** la voie de la parole de `mj.py` ni
`paroles.py` (lot 142), ni `corps.py`, `vecu.py`, `deliberation.py`, `tenir.py` (lot 140). Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 25, 101 (garde de voix d'auteur et réserves de preuve) et
`relances-luna` (« moteur » hors des répliques), puis le rapport du lot 141 (N10) et ses fils dans
`C:\Users\msics\donjon\artifacts\verif-luna-9a39738\`.

## Le défaut (N10, vérification Luna 9a39738, lot 141)
`atelier` p1 n°12 : « il faudrait que le moteur fournisse un geste de fouille ou de recherche adapté » ; `relais` p2 n°22 :
« Le moteur n'en reconnaît pas […] dont tu connais précisément l'identifiant ». Ces phrases passent l'audit et sont affichées.
Le garde déterministe de voix d'auteur refusait déjà « moteur » hors des répliques : établis d'abord par quelle voie ces textes
y échappent (explication d'un refus du monde, `ExplicationCedee`, dialogue d'obstacle, repli, segment exact, attestation).

## L'invariant
**Tout texte affiché au joueur, par n'importe quelle voie, explique l'obstacle dans la fiction ; le vocabulaire des contrats
internes (moteur, identifiant, proposition, champ, schéma…) n'y paraît pas hors d'une réplique.** Corrige la voie qui contourne
le garde commun pour qu'elle y passe, et, si la liste du garde est incomplète, complète-la par catégorie (vocabulaire technique
du contrat), jamais par phrase. Ne censure pas les mots ordinaires (lot 101) : « identifiant » ou « champ » au sens courant dans
une réplique ou une ambiance restent admis si le garde existant les admet. Aucune règle propre à l'atelier ou au pied-de-biche.

## Vérification
- Tests MJ simulé/console après rechargement : les deux phrases réelles refusées puis reformulées dans la fiction, par la voie
  exacte qui les laissait passer ; une autre explication d'obstacle admise ; un mot ordinaire non censuré.
- Luna, **une passe** : `atelier`, `relais`, `luna-restes-ambiance`, référence `9a39738` lue du cache (lot 141) ; appels par tour,
  aucune explication technique affichée, pas de hausse nette des relances.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-contrats-internes` poussée (pas `main`).
`docs/contrat-mj.md` si la règle change, `docs/etat-dev.md` (« Branche `codex-contrats-internes`, non fusionnée »). Rapport
d'une page : `docs/taches/rapport-codex-143-contrats-internes.md`.
