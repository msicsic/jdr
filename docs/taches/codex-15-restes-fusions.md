# Tâche Codex 15 : les restes des fusions (relations 3b, corps 4a, MiMo)

Branche `codex-restes-fusions` (elle porte ce fichier, issue de `main` 5594028), worktree dans
`tmp-worktrees/`. Lis d'abord `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-relations-3b` et
`codex-force-4a`, lignes « Fusionné après … » et « À revoir »), `docs/taches/rapport-codex-6-relations-3b.md`,
`docs/taches/rapport-codex-7-force-4a.md`, `docs/plan-relations.md` (§ 3.5, bandes et seuils).

Cinq défauts relevés à la relecture des fusions. Chacun se corrige par la règle commune (règle d'`AGENTS.md`),
avec le cas réel et un autre cas de même nature, testés après rechargement.

## 1. La parole tenue apprise trop tard
Dans `echanges.remettre`, l'`engagement_tenu` s'inscrit avant le souvenir `recu` du bénéficiaire : celui-ci
n'apprend que la parole est tenue qu'à une annonce ultérieure, alors qu'il reçoit l'objet en main (objet vendu
d'avance, part différée). Invariant : recevoir de la main de qui l'avait promis, c'est constater la promesse
tenue, à l'instant même (relations comprises : confiance, dette). Cas : un objet vendu d'avance puis remis ;
une part différée remise.

## 2. Les seuils écrits en dur
`echanges.accueil` (`r["rancune"] >= 60`) et `voix.repond` (`rancune >= 60 or peur >= 60`) emploient 60, alors
que les bandes de 3b mettent rancune et peur à 40 (sortie sous 30, hystérésis). Invariant : toute lecture d'un axe
en tant que « en veut », « craint », « se méfie » passe par les lectures graduées de `relations` (`en_veut`,
`craint`, `se_mefie`, avec leur hystérésis), jamais par un nombre local. Si un seuil plus fort est voulu pour une
conduite (refuser de répondre n'est pas seulement en vouloir), il se déclare dans `relations` avec sa raison.
Cherche toutes les comparaisons numériques d'axes hors de `relations.py` (`test_relations_socle` peut être étendu
pour l'interdire). Mesure l'effet au banc.

## 3. Les refus de la 4a sans `attendu` en identifiants
« Partie terminée » et « sans connaissance » portent un `attendu` en texte libre. Contrat (`donjon/refus.py`,
`AGENTS.md`) : champ fautif, valeur reçue, ce qui serait accepté, en identifiants ; une cause par refus.

## 4. La dépouille garde le vivant
Une dépouille garde le portrait et la manière de parler du vivant. Ce que le joueur et le MJ reçoivent d'un corps
mort ne doit contenir que ce qui se voit d'un corps (apparence, blessures visibles, ce qu'il porte), jamais sa
voix ni sa manière de parler ; le nom seulement si on le connaît (déjà fait, `noms.PERSONNES`). Vérifier aussi
`noms.nom` employé pour un PNJ qui parle d'un défunt : il doit juger d'après ce que sait ce PNJ, pas le joueur.

## 5. Les tests MiMo quand `jsonschema` est installé
Sur un poste où `requirements-mimo.txt` est installé, six sous-tests échouent (`test_mimo`,
`test_fournisseurs_jeu` : quatre états d'affichage historiques « I/G devenant L », deux comptes de transport 6
au lieu de 5). Ici ils sont sautés. **N'installe pas `jsonschema` dans le `.venv` partagé** (d'autres agents s'en
servent) : crée un environnement à part dans ton worktree (`python -m venv .venv-mimo`, puis les requirements du
README et `requirements-mimo.txt`). Trouve si ce sont les tests qui ont vieilli (attentes d'avant un changement
fusionné depuis) ou un défaut réel de l'adaptateur MiMo ; corrige en conséquence, sans appel réseau.

## Vérifications
- `tests/test_restes_fusions.py` : chaque point, cas réel et autre cas de même nature, après rechargement, ce que
  voit le joueur.
- Suite complète verte avec le `.venv` partagé (`tools/tests.py --processus 4`) et, pour le point 5, les fichiers
  MiMo avec `.venv-mimo`.
- `planification.VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h graine 42, chaque scénario.
- Banc rapide (`tools/comparer_bancs.py --reference 5594028`, 4 h, 4 graines, quatre scénarios, `--processus 4`
  au plus, l'un après l'autre) : les points 2 et 1 changent le comportement, relève les écarts (réponses aux
  appels, accueil, méfiances, rancunes) ; aucune usurpation ni violation.
- Luna (connexion sur ce poste, `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, plusieurs exécutions en
  parallèle permises, sur des copies seulement) : seulement si le point 4 change ce que reçoit le MJ ; une scène
  avec une dépouille vue (préparée dans `tests/data/bancs`), « je regarde le corps », « je fouille le corps ».
- Docs : `docs/plan-relations.md` si un seuil change, `docs/etat-dev.md` (« Branche `codex-restes-fusions`, non
  fusionnée », compte de tests).

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-15-restes-fusions.md` : pour chaque point, cause, correction, cas vérifiés ; mesures
avant → après ; limites. Les branches `codex-garde-pret` et `codex-force-4b` sont en cours de fusion (elles
touchent `relations` et `planification`) : garde les changements localisés.
