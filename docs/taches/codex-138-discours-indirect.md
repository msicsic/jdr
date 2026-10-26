# Tâche Codex 138 (MJ) : une demande rapportée au discours indirect devient une réplique du personnage (N8)

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`,
copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus
2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche l'interprétation d'une parole et sa revue
de fidélité (`paroles.py`, `mj.py` pour la seule voie de la parole, schéma de parole) ; **pas** `narration.py`, `noms.py`
(lot 135), ni `tenir.py`, `pnj.py`, `moteur.py`, `commandes.py`, `planification.py` (lot 136). Termine ton dernier message par
`LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 91 (mots exacts et opérations), 104, 128 (opérations analysées
avant le contenu) et 123 (N8), puis `paroles.analyser` (verbes de parole, « je demande à X… »), la réplique proposée par
l'interprétation (`parole_joueur`) et `mj._verifier_fidelite_parole`.

## Le défaut (N8, vérification Luna 057766f, lot 123)
`ressources` p2 n°1, saisie « je demande à Brune si elle a de quoi manger » : Corvus dit « Tu dis à Brune : “Tu demandes à Brune
si elle a de quoi manger.” ». La passe 1 donnait « Brune, tu as de quoi manger ? ». Quatre appels, aucun refus : la revue de
fidélité a admis une réplique qui est la description de la demande, pas ce que Corvus prononce. Fils dans
`C:\Users\msics\donjon\artifacts\verif-luna-057766f\` (ce poste).

## L'invariant
**La réplique d'une parole est ce que Corvus prononce, au discours direct ; une saisie au discours indirect (« je demande à X
si… », « je lui dis que… ») est transposée, pas recopiée.** Établis d'abord dans le fil d'où vient la phrase (interprétation,
correction, secours local aux mots exacts) et pourquoi la revue l'admet. Corrige le contrat commun : la définition de `replique`
partagée par l'interprétation et la revue, et le cas où le moteur reprend lui-même les mots du joueur (le secours ne doit pas
prendre une forme narrative pour une réplique). Aucun mot-clé propre à « demander », aucune règle propre à Brune ou à la faim :
le critère porte sur la forme rapportée en général (personne grammaticale, verbe introducteur). Une parole déjà au discours
direct ou entre guillemets reste recopiée mot pour mot.

## Vérification
- Tests MJ simulé/console après rechargement : le cas réel (réplique au discours direct, opération `ressource` conservée), un
  autre discours indirect (« je lui dis que la porte est forcée », autre personnage), une parole entre guillemets inchangée, et
  le secours aux mots exacts qui ne produit plus « Tu demandes… » comme réplique.
- Luna, **une passe** : `ressources`, `soir-appel`, `noms-dialogue`, référence `057766f` relue dans les bruts du lot 123 ;
  appels par tour avant/après, aucune réplique à la deuxième personne décrivant la demande.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-discours-indirect` poussée (pas `main`).
`docs/contrat-mj.md` si la règle change, `docs/etat-dev.md` (« Branche `codex-discours-indirect`, non fusionnée »). Rapport
d'une page : `docs/taches/rapport-codex-138-discours-indirect.md`.
