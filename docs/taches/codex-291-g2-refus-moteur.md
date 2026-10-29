# Tâche Codex 291 (refonte G2) : un refus se lit dans le message du moteur, jamais dans une explication libre

Premier lot de code de la refonte du MJ. Lis `AGENTS.md` (nouveau « Contrat du MJ », clause de transition),
`docs/conception-refonte-mj.md` (sections 2, 4 et 9, ligne G2) et `docs/conception-valeur-llm.md` (section 7). La
branche `origin/prompt-simplifie` est la base de réflexion : `retour_refus`, `reponse_du_moteur` et la boucle bornée de
`MJ._echanger_decouple` (vers la ligne 768 de son `donjon/mj.py`).

## Le constat
Sur l'intégration, quand toutes les propositions de Luna sont refusées par le monde, `MJ._echanger_prepare`
(`donjon/mj.py`, vers les lignes 660 à 850) redemande à Luna un dialogue d'explication. Cet appel est ensuite audité ;
s'il est refusé, `ExplicationCedee` fait lire le refus du monde. Coût : un appel et un audit de plus avant que le joueur
lise un refus que le moteur sait déjà dire. Risque : une explication libre transforme un défaut de proposition en
impossibilité de fiction (« il faut une échelle »), ou prête un refus à un PNJ qui n'a rien dit (lot 287, section 2).

## L'invariant
**Quand le monde refuse une intention, le joueur lit le message public du moteur (`reponse_du_moteur`), exact et sans
`attendu`, sans appel à Luna ni audit pour l'expliquer.** La boucle de correction bornée sur copie reste : un refus avec
`attendu` est transmis à Luna (`retour_refus`), qui peut proposer une autre interprétation de la même intention.
Plusieurs refus du monde distincts se lisent dans l'ordre, une cause par refus. Un refus de forme (`RefusDeForme`) n'est
jamais affiché comme une impossibilité du monde : s'il reste après les corrections, le joueur lit une demande de
précision sobre, écrite par le moteur.

Ce que le lot ne fait pas : pas de compilateur (G1), pas de rendu du résultat (G4), pas de clic (U-D), aucune autre
voie retirée. La contre-revue et la fidélité de parole restent (filet du contrat). Supprime `ExplicationCedee` et
l'appel d'explication seulement s'ils n'ont plus d'usage ; dis ce qui reste.

## Fichiers attendus
`donjon/mj.py` (la boucle de `_echanger_prepare` et ses sorties), `donjon/refus.py` seulement si un message public
manque à une cause. Ne touche pas aux mécaniques des PNJ.

## Vérification
- Tests ciblés : la saisie réelle qui produisait l'explication libre et un autre cas de même nature, en console avec MJ
  simulé :
  - un refus de portée ;
  - un passage trop bas (`sous-obstacle-trop-bas`) ;
  - un refus de forme persistant ;
  - deux refus distincts.

  Pour chacun : texte affiché, zéro appel d'explication, monde et rendu identiques après recharge. Reprends les tests
  qui exercent `ExplicationCedee`, `_sans_relance`, les replis et les explications ; trouve-les par recherche. Adapte
  seulement ceux dont l'attente était l'explication libre, en le disant.
- **Luna, une passe**, scripts `relais`, `sous-obstacle-relais`, `sous-obstacle-trop-bas`, `atelier`, contre la
  référence de l'intégration en cache (`tools/banc_multi.py --variante integ=<commit de ta base> --variante lot=.`,
  référence absente jouée une fois et rangée). Copies seulement, jamais `sauvegardes/`, `SEUIL_AUTH` vers le coffre du
  dépôt principal. Mesures :
  - appels et secondes par tour ;
  - zéro appel d'explication ;
  - refus par cause, relances, replis ;
  - le texte de chaque refus lu par le joueur.
- Pas de suite complète (le superviseur la lance).

## Contraintes
**Poste : le laptop.** Une vérification d'intégration (lot 284) y tourne : deux processus au plus, priorité réduite ;
la passe Luna est légère.

## Livraison
- Branche `codex-g2-refus-moteur` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) ; si
  la poussée échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-291-g2-refus-moteur.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g2-291\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
