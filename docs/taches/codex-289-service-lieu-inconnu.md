# Tâche Codex 289 : un service admis au plan, refusé à l'exécution (bénéficiaire de lieu inconnu)

**Diagnostic seul : aucun fichier de code du jeu, de test ou de scénario modifié.** Pas de Luna, pas de suite complète,
pas de banc comparatif.

## Le constat (lot 273, réalisation Sol, abandonnée)
Le bilan `docs/taches/bilan-codex-273-correction.md` est sur l'étiquette `archive/273-sol` :
`git show archive/273-sol:docs/taches/bilan-codex-273-correction.md`, section « Tilo : défaut réel ».

Auberge, capture à **226 min + 352 dixièmes**. Le plan de Tilo propose `servir marmite_1_1 pour mathurine` (pulsion
`{objet: marmite_1_1, servir: mathurine}`). Tilo est en cuisine, Mathurine au cellier, et Tilo ne sait pas où elle est
(lieu cru **inconnu**).
- `planification._mesurer_direct` admet le geste, et `pnj.refus_etape` renvoie `None`.
- `echanges.servir` le refuse à l'exécution.
- Le service réussit la minute suivante, après un déplacement.

Le rejet se reproduit d'un bloc comme en temps découpé. La même capture rechargée sur le parent du 273 donne la même
admission : la lacune est antérieure au 273. Le bilan de Sol propose d'exiger, pour tous les participants requis, une
présence crue ou une venue convenue ; sinon rechercher ou rejoindre avant le service.

**À peser contre le lot 259** (`docs/taches/rapport-codex-259-presences-regression.md`), qui a décidé qu'une
localisation inconnue n'est pas une absence crue et que la présence nécessaire se juge au moment du geste. Le lot 251
avait étendu aux participants d'un service le contrôle des cibles touchées (`pnj._a_reunir`).

## Fichiers fournis
Dans `C:\Users\msics\donjon\artifacts\demande-273-sol\` (PC fixe) :
- `echec-service-273.json`, l'état capturé. Il vient de la branche 273 : retire les deux champs qu'elle a ajoutés
  aux esprits (`fournitures`, `demandes_suspendues`), comme le fait déjà le script ;
- `admission-service-273.py`, le script d'admission ;
- les deux sorties de Sol (parent et correction).

## Ce qu'il faut établir
1. Sur l'intégration actuelle, la même capture rechargée reproduit-elle l'admission puis le refus ? Donne les fonctions,
   les valeurs lues et la cause exacte du refus dans `echanges.servir`.
2. Est-ce un **désaccord de contrat** entre l'admission (plan, revalidation, `refus_etape`) et l'exécution (`servir`) ?
   Ou bien l'admission est-elle voulue par le lot 259 et le refus un simple constat sur place ?
3. Le coût de jeu : un geste perdu puis repris, une boucle, un service jamais rendu, un plan qui renaît ? Observe-le
   sur la capture rejouée quelques minutes, puis sur un autre cas de même nature (autre PNJ, autre scénario).
4. Si c'est un défaut, l'invariant à corriger dans un petit lot, sans revenir sur le lot 259 (une localisation inconnue
   n'est pas une absence), sans lecture de position réelle, sans cas propre au repas ou au bénéficiaire. Sinon, pourquoi
   le comportement est juste.

Captures : monde, rendu et scène identiques après recharge. Un seul processus à priorité réduite à la fois.

## Livraison
- Branche `ds-service-lieu-inconnu` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) ;
  si la poussée échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-289-service-lieu-inconnu.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\service-289\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.
