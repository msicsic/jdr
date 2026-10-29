# Tâche Codex 294 (refonte G1) : la saisie libre passe par un compilateur à petit contexte public

Troisième lot de code de la refonte du MJ, après G2, G4 et U-D (lots 291 à 293, fusionnés). Lis `AGENTS.md`
(« Contrat du MJ », clause de transition), `docs/plan-refonte-mj.md` (ligne G1), `docs/conception-refonte-mj.md`
(sections 1, 2 « Éléments à reprendre », 4 et 9, ligne G1) et `docs/conception-valeur-llm.md` (sections 4 et 7). La
branche `origin/prompt-simplifie` est la base : `donjon/compilateur.py` (`compiler`, `extraire_contexte`,
`normaliser_proposition`, `SCHEMA_COMPILATEUR`), `paroles.section_contenu`, `donjon/sources.py`, et
`MJ._echanger_decouple` dans son `donjon/mj.py` (vers la ligne 768), avec ses tests `test_schema_compilateur` et
`test_proto`.

## Le constat
Sur l'intégration, une saisie libre passe par `MJ._echanger` (`donjon/mj.py`, vers la ligne 978) : de grosses
consignes, un dossier de faits complet et un schéma qui choisit entre action, parole, faits ou dialogue. L'interprétation
pèse 44,7 % de l'attente (lot 287). Le prototype compile la même intention avec un contexte public réduit (objets,
inventaire, interlocuteurs, noms et lieux connus, comptes, accords, atelier, parole prévue) et un schéma des actions et
des actes de parole dérivé du contrat. G2 (refus publics) et G4 (résultat rendu par le moteur) sont déjà portés :
la compilation est la seule attente nominale qui reste avant validation.

## L'invariant
**Une saisie libre est interprétée par un seul appel nominal au compilateur, sur un contexte public réduit qui couvre
les actes actuels (gestes, opérations, paroles typées, avis, demandes, marchés, négociation de mission) ; la
proposition reste sur copie jusqu'à son admission par le moteur (G2), et son résultat est rendu par le moteur (G4).**
Le contexte ne contient que des données perceptibles ou connues de Corvus, sous leurs références publiques ; aucune
entité non perçue, aucun nom non appris. Les corrections bornées sur copie (`retour_refus`, `attendu`) restent, sans
explication libre. Une intention exprimable et fidèle au contrat ne doit pas finir en « précise… » ni en `propos` vide
(défaut `conversation_pnj` du prototype pour la négociation de mission : à résoudre).

Le contexte réduit ne retire aucun fait dont dépend la validité d'un acte : mesure sa taille, ne fixe pas de plafond
arbitraire. La contre-revue et la fidélité de parole restent en filet pour les actes à effets issus du libre (contrat,
« Fidélité de la saisie ») ; ne les retire pas.

Reprends du prototype les contrats, pas ses réparations sémantiques silencieuses (une normalisation qui change le sens
d'une proposition sans le dire). Ne fusionne pas `prompt-simplifie` en bloc : l'intégration a changé depuis sa base
(paroles, refus, comptes, actes, avis, rappels).

## Découpage
Si les familles d'actes ne tiennent pas toutes dans le créneau, livre d'abord les gestes et opérations, puis les
paroles typées, en gardant l'ancienne voie pour le reste derrière une bascule temporaire nommée, que G21 retirera. Dis
dans le rapport ce qui est porté et ce qui reste sur l'ancienne voie. Ne présente pas un portage partiel comme complet.

## Fichiers attendus
`donjon/compilateur.py` (nouveau, porté), `donjon/paroles.py` (`section_contenu`), `donjon/sources.py`,
`donjon/mj.py` (raccord de la voie libre). Ne touche pas aux mécaniques des PNJ, au rendu du moteur (G4) ni aux refus
publics (G2).

## Vérification
- Tests ciblés : porte `test_schema_compilateur` (schéma invariant, variantes d'actes) et les cas utiles de
  `test_proto`. Pour chaque famille portée : la saisie réelle d'un banc et un autre cas de même nature, en console avec
  MJ simulé. Contrôle le plan admis, le monde et le rendu après recharge, et l'absence d'entité non perçue dans le
  contexte. Reprends les tests de `_echanger` qui exercent les familles portées ; adapte seulement ce qui attendait
  l'ancienne requête, en le disant.
- **Luna, une passe**, scripts `relais`, `crypte` (négociation de la prime), `echanges`, `ressources`, `soir-appel`,
  `avis-joueur`, contre la référence de l'intégration (`tools/banc_multi.py --variante integ=<commit de ta base>
  --variante lot=.`, référence absente jouée une fois et rangée). Copies seulement, jamais `sauvegardes/`,
  `SEUIL_AUTH` vers le coffre du dépôt principal. Mesures :
  - réussite au premier coup et corrections récupérées, intentions abandonnées ;
  - appels et secondes par tour, taille de l'entrée et préfixe en cache ;
  - refus par cause, relances, replis ;
  - la négociation de mission typée et jouée.
- Lance la passe Luna détachée, avec un fichier de fin écrit même en cas d'échec, et vérifie qu'elle démarre avant de
  rendre la main. L'analyse sépare un incident réseau de la référence du contrôle de l'invariant.
- Pas de suite complète (le superviseur la lance).

## Contraintes
**Poste : le laptop.** Une vérification d'intégration (lot 284) y tourne : deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-g1-compilateur` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) ;
  si la poussée échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-294-g1-compilateur.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g1-294\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
