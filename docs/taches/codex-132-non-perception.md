# Tâche Codex 132 (MJ) : une non-perception vraie n'est pas refusée comme une absence (N6)

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le PC fixe** (Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`,
copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus
2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche l'audit narratif et son dossier
(`narration.py`, `perception.py` si besoin, `mj.py` pour la transmission) ; **pas** `signes.py` (lot 129), ni `deliberation.py`,
`pnj.py`, `banc_pnj.py` (lot 130). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/contrat-mj.md`, les rapports des lots 102 (couverture de la vue), 95 (preuve exacte des segments moteur),
111 et 123 (N6), puis `perception.couverture_vue`, `narration.INSTRUCTIONS_AUDIT` (règle de portée) et `narration.controler`.

## Le défaut (N6, persistant depuis le lot 111)
`signes-guet`, « Que fait Gorm en ce moment ? » depuis la galerie : « tu ne le vois pas » est refusé parce que « la
non-perception de Gorm n'est pas établie par la vue partielle » (six à huit appels) ; au lot 123, p2 refuse même « Tu ne sais pas
où se trouve Gorm » (quatre appels). Le lot 102 a voulu qu'une **absence** hors de la surface couverte soit refusée ; l'audit
applique la même exigence à une **non-perception**, qui est vraie dès que l'entité n'est pas perçue maintenant, quelle que soit la
couverture. Coût : relances et latence, et un texte final plus pauvre.

## L'invariant
**Une affirmation de non-perception d'une entité que Corvus ne perçoit pas maintenant est établie par le moteur ; une absence
reste soumise à la couverture.** Établis d'abord la cause dans les fils (`artifacts/verif-luna-057766f/`, lot 123) : ce que le
dossier fournit sur l'entité nommée, et pourquoi l'auditeur conclut. Corrige le contrat commun : le dossier d'audit doit permettre
de prouver la non-perception de façon déterministe (par exemple, les entités connues de Corvus et non perçues maintenant, en
références publiques, sans révéler leur position ni une entité inconnue), et la règle de portée doit distinguer « ne pas voir /
ne pas savoir où » de « n'être pas là ». Si une partie peut être vérifiée par le moteur sans l'auditeur (preuve exacte comme au
lot 95), préfère-la. Aucun mot-clé, aucune règle propre à Gorm, à la galerie ou à ce script ; aucune fuite d'entité non perçue :
le contrôle de fuite reste déterministe et inchangé.

## Vérification
- Tests MJ simulé/console après rechargement : le cas réel (non-perception admise sous couverture partielle) et un autre cas de même
  nature (objet ou personne connus, autre salle) ; une **absence** affirmée hors couverture reste refusée (le cas du lot 102 dans
  le noir avec Ilse et Brune présentes) ; une entité jamais perçue n'apparaît pas dans le dossier.
- Luna, **une passe** : `signes-guet`, `signes-noir`, `soir-noir`, référence lue du cache (`057766f`, lot 123) ; appels par tour
  avant/après, plus de refus N6, aucune fausse absence affichée.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-non-perception` poussée (pas `main`).
`docs/contrat-mj.md` si la règle change, `docs/etat-dev.md` (« Branche `codex-non-perception`, non fusionnée »). Rapport d'une
page : `docs/taches/rapport-codex-132-non-perception.md`.
