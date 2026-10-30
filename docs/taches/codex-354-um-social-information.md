# Tâche Codex 354 (refonte U-M social information) : l'acte d'information se choisit au formulaire

Lot d'interface de la refonte du MJ, après U-D, U-C, G16 (lot 345, paroles d'information formulées par le moteur) et
U-M corps/passage (344, 349), fusionnés. Lis `AGENTS.md` (« Contrat du MJ »), `docs/etat-dev.md` (court),
`docs/plan-refonte-mj.md` (ligne U-M social information), `docs/conception-valeur-llm.md` (section 2) et les rapports
293 (U-D), 325 (U-C), 345 (G16) et 344 (U-M corps), dont tu reprends la structure.

## L'invariant
**Le formulaire web transmet un acte d'information (demander où est quelqu'un ou quelque chose, demander qui parle,
dire où est une chose, demander si l'autre a une ressource) avec ses seuls paramètres publics : destinataire perçu ou
voix connue, sujet désigné parmi ce que Corvus connaît ; le descripteur U-D donne au moteur le même contenu typé que la
saisie équivalente, sans analyse de texte ni appel au modèle.** La réponse est celle du moteur (G16) : croyances du
répondant, refus et raisons, rien de plus. Le formulaire ne reçoit ni croyance d'autrui, ni position non connue, ni
entité non perçue.

## Fichiers attendus
`donjon/web/page.html`, `donjon/web/pont.py`, `donjon/dialogues.py` et le catalogue `donjon/gestes_publics.py`
seulement si un paramètre public manque. Ne touche ni `jeu.py`/`tui.py` (lot 353 en cours, puis U-T social
information), ni au MJ (`mj.py`, `compilateur.py`), ni aux règles de réponse de `paroles.py`.

## Vérification
- Parité avec la saisie typée : mêmes contenus, même réponse moteur, mêmes croyances apprises par ouï-dire ; voix qui
  se nomme, croyance fausse du répondant, refus par méfiance ; destinataire parti à la réception (refus public) ; zéro
  appel au modèle ; monde, paroles entendues, scène et fiche identiques après recharge. Tests du clic (Node) verts.
- Un autre scénario pour le même acte. Mesure : saisies évitées, clics jusqu'à la réponse.
- Pas de Luna, pas de suite complète.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Lots en cours : 352 (E3, PC fixe), 353 (U-T corps et
passage, laptop) ; signale tout fichier commun.

## Livraison
- Branche `codex-um-social-information`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-354-um-social-information.md`, entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\um-social-information-354\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
