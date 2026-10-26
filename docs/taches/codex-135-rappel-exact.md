# Tâche Codex 135 (MJ) : un rappel conforme aux mots réellement dits n'est pas refusé (N7)

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`,
copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus
2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche l'audit narratif (`narration.py`, dossier
`echanges_passes`, rappels du lot 112) et si besoin `noms.py` pour la projection ; **pas** `echanges.py`, `agendas.py` (lot 133),
ni `tenir.py`, `pnj.py`, `moteur.py` (lot 136). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 112 (rappels du passé, `echanges_passes`), 95 (preuve exacte des
segments), 132 (attestations exactes) et 123 (N7), puis `narration.echanges_passes`, l'extraction `rappels` de l'audit et la
projection publique des noms (`noms.public`) appliquée au dossier.

## Le défaut (N7, vérification Luna 057766f, lot 123)
`soir-noir` p1 n°5, « je demande à la voix comment elle s'appelle » : le candidat « Je te l'ai déjà dit : je m'appelle Ilse » est
refusé ; l'audit prétend que la voix avait dit « Je m'appelle une voix qui se dit Ilse ». Or `echanges_passes.voix_1` contient
exactement « Je m'appelle Ilse. Et toi, qui es-tu ? ». Affiché : « Une voix qui se dit Ilse. Et toi, qui es-tu ? », huit appels.
Fils dans `C:\Users\msics\donjon\artifacts\verif-luna-057766f\` (ce poste).

## L'invariant
**Les mots réellement prononcés, rappelés à l'identique, sont admis ; la référence publique d'un locuteur n'est jamais confondue
avec ce qu'il a dit.** Établis d'abord la cause dans le fil : la projection publique réécrit-elle un nom à l'intérieur d'une
citation enregistrée (mots du dossier ou de la réponse), ou l'auditeur confond-il la référence `voix_1` (« une voix qui se dit
Ilse ») avec ses mots ? Corrige le contrat commun : les citations enregistrées traversent la projection sans être réécrites
(seule la référence du locuteur est projetée), et un rappel qui reprend mot pour mot une parole du dossier est prouvé par le
moteur, comme les segments exacts du lot 95 et les attestations du lot 132, sans audit. Un rappel déformé reste contrôlé
sémantiquement. Aucun mot-clé, aucune règle propre aux noms ou à Ilse ; aucune fuite d'un nom que Corvus ne connaît pas (la
voix ne nomme Ilse que parce qu'elle l'a dit à Corvus).

## Vérification
- Tests MJ simulé/console après rechargement : le cas réel (rappel exact admis, sans audit), un autre rappel exact d'une autre
  parole (autre locuteur, autre scène), un rappel déformé encore refusé, et un nom jamais entendu de Corvus toujours projeté.
- Luna, **une passe** : `soir-noir`, `soir-voix`, `noms-dialogue`, référence `057766f` relue dans les bruts du lot 123 ; appels
  par tour avant/après, plus de refus N7, aucune fuite de nom.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-rappel-exact` poussée (pas `main`). `docs/contrat-mj.md`
si la règle change, `docs/etat-dev.md` (« Branche `codex-rappel-exact`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-135-rappel-exact.md`.
