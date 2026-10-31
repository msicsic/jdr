# Tâche Codex 434 : K2, assistance de Luna à la négociation

Lot K2 de la refonte du MJ (`docs/plan-refonte-mj.md`, ligne K2 ; `docs/conception-valeur-llm.md`, « Pipeline
proposé » points 1 à 5, « Liberté du LLM », exemples « une part de vivres contre la promesse d'entretenir ce brasero » et
« ramène Brune avant la crue », et « Lots de valeur à ouvrir après décision »). Préalables fusionnés : K0 (lot 426,
suggestions déterministes, `dialogues.candidats_contrat`), K1 (lot 429, éditeur à deux termes), forme A du compilateur.
Décision du 2026-10-29 : contrats en deux temps, d'abord K0/K1, puis l'assistance Luna **à la demande**.

Lis `AGENTS.md` (contrat du MJ), `docs/etat-dev.md` (court), les deux documents ci-dessus, les rapports 426 et 429.

## Invariant (un seul)
**Quand le joueur demande de l'aide pour négocier (ou formule une intention sociale libre que K0 ne couvre pas), Luna
propose au plus deux alternatives de marché composées des seuls termes typés existants ; chacune est admise par la même
validation sur copie que K0 (`echanges.candidat_proposition`) avant d'être affichée, puis ouvre l'éditeur K1 prérempli.
Luna ne décide ni l'accord, ni le prix, ni la vérité d'une information, n'ajoute aucune clause et n'utilise que ce que
Corvus connaît.** Une intention qui demande une clause non exprimable (condition de succès, règlement conditionnel,
échéance non typée) est déclarée non prise en charge, sans clause effacée en silence. Le verdict reste celui du PNJ.

Mesure demandée (ligne K2 du plan) : nombre d'alternatives utiles **absentes de la référence K0** sur les mêmes scènes,
appels jusqu'à une offre utile ; pas la quantité de texte.

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/compilation.py`, `donjon/comprehension.py`, `donjon/echanges.py`, `donjon/dialogues.py`,
`donjon/accords_publics.py`, rendu web/console/TUI au besoin, tests. Lots en cours : 402 (calcul), 431 (admission
préalable, `portee_narrative.py`, `mj.py`), 433 (références des entités créées, `noms.py`, `enrichissement.py`).
Pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite.

## Vérification
Avec MJ simulé : demande d'aide devant Aubin au Relais (alternative absente de K0, par exemple une part contre une tâche
d'entretien), autre scène à l'auberge (Odile), intention à clause non exprimable (« ramène Brune… »), alternative que
la validation refuse (jamais affichée), besoin privé du PNJ jamais révélé ; éditeur prérempli, verdict du PNJ, état et
vues après recharge. Tests voisins verts (K0, K1, E5, propositions). **Luna : une passe ciblée** sur copies (ajoute un
petit script `negociation-aide` si aucun n'existe), en comptant les alternatives utiles hors K0 ; si la revue
automatique la bloque ou si le coffre est illisible, laisse la commande exacte dans les bruts. Pas de suite complète.

## Livraison
Branche `codex-k2-assistance-luna`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
dépôt de l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-434-k2-assistance-luna.md` ;
entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents
graves). Bruts dans `C:\Users\msics\donjon\artifacts\k2-assistance-434\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS :
<fichier de fin>` ou `QUESTION : …`.
