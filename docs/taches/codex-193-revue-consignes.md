# Tâche 193 (revue vierge) : les consignes de Luna, contradictions, répétitions et règles devenues inutiles

Revue en **lecture seule** demandée par l'utilisateur le 2026-10-27. **À lancer après la fusion du lot 180 c** (comptes écrits
par le moteur), qui change les consignes de narration. Aucun code du jeu, consigne, test ou outil modifié ; aucune fusion ; pas
de Luna. Le chantier du prompt est gelé (`docs/plan-prompt.md`, « État au 2026-10-27 ») : cette revue prépare une éventuelle
réécriture, elle ne la fait pas. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`, `PYTHONIOENCODING=utf-8`, au plus un
processus. **Bruts et texte proposé dans `C:\Users\msics\donjon\artifacts\consignes-193\`, jamais dans le dépôt.** Termine par
`LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

## Le contexte en trois lignes
« Le Seuil » est une aventure textuelle : le MJ (le modèle Luna) interprète la saisie du joueur, propose au moteur des actions
typées, puis raconte ; plusieurs appels relisent ce qu'il écrit (audit narratif, contre-revue d'action, fidélité des paroles,
révision). Les consignes de ces appels ont grossi lot après lot, chaque correctif ajoutant sa phrase, et personne ne les a relues
d'un trait. Le contrat qui ne se discute pas est dans `AGENTS.md` (« Contrat du MJ ») : il prime sur tout le reste.

## Ce qu'on te demande
1. **Trouver toutes les consignes envoyées à Luna**, par voie (interprétation, audit narratif, contre-revue, fidélité, révision,
   récit, explication…) : `donjon/consignes.py`, et les chaînes d'instructions de `mj.py`, `narration.py`,
   `couverture_action.py` et des autres modules qui en définissent (cherche-les, ne te fie pas à cette liste). Mesure leur taille
   par voie (`tools/mesure_prompt.py` peut aider) et dis lesquelles sont permanentes ou conditionnelles.
2. **Inventaire, chaque entrée avec les passages cités mot pour mot et leur emplacement (fichier, constante, ligne)** :
   - **contradictions** : deux consignes qui exigent des choses incompatibles ou en tension (bref contre exhaustif, refuser
     contre admettre, ambiance libre contre contrôle d'une même phrase…), y compris entre deux voies (ce que le narrateur doit
     écrire et ce que l'auditeur refuse) ;
   - **répétitions** : la même règle dite plusieurs fois, avec des nuances qui divergent ;
   - **règles devenues inutiles** : ce que le moteur contrôle désormais lui-même de façon déterministe (refus local de portée,
     comptes écrits par le moteur, gardes lexicales, refus avec `attendu`) ; vérifie dans le code que le contrôle existe bien ;
   - **règles propres à un exemple** (un objet, un lieu, un personnage, une formulation), contraires à `AGENTS.md`.
3. **Proposer un texte réorganisé** pour chaque voie, dans les bruts seulement : une règle à un seul endroit, dans l'ordre de la
   décision, sans perdre aucune exigence du contrat du MJ ; une table de correspondance ancienne règle → nouvelle place (ou
   « retirée, contrôlée par … »).
4. **Rapport** `docs/taches/rapport-codex-193-revue-consignes.md` (deux pages au plus) : tailles par voie, les contradictions
   classées par risque (celles qui expliquent probablement des relances ou des faux refus connus en premier : relis pour cela
   les rapports 162, 165, 168, 170 et 176), les répétitions, les règles inutiles, et ce qu'une réécriture devrait mesurer
   (deux passes Luna, critère des refus du lot 95 : pas plus d'un refus juste perdu sur cinq rejeux). Dis aussi pourquoi le
   lot 170 (doublons retirés, relances 14 → 19) a pu dégrader le comportement, si tu le vois dans les textes.

## Livraison
Branche `codex-revue-consignes` : le seul rapport et une ligne dans `docs/etat-dev.md` (« Revue des consignes 193, lecture
seule »). Commit ; si la poussée est bloquée, laisse le commit local et dis-le.
