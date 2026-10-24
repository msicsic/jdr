# Lot 54 — Accord des désignations publiques

Branche `codex-elision`, non fusionnée, base `5125d06`, brief `fda1346` ; 24 octobre 2026.

L'invariant : une désignation déterminée ou un nom propre inséré dans une phrase reçoit son
article, sa préposition et sa capitale ensemble. `francais.groupe_nominal` porte désormais
les contractions de **de/à**, l'élision et la capitale de début. `de`, `complement_de` et la
relation physique y délèguent. `inserer_designation` reprend aussi la liaison du texte source :
`d'Aubin` devient `du vieil homme voûté`, jamais `d'Le…`. `noms._remplacer_noms` utilise ce
chemin pour les noms et les références opaques dans la prose ; une référence typée seule
reste opaque. Les citations protégées conservent les mots réellement prononcés.

Les variantes locales de `noms`, `social`, `proximite` et `enrichissement` sont retirées.
Les insertions directes des adresses, dons, promesses, réponses, détails et noms d'objets
emploient le même accord (paroles, moteur, dialogues, agendas, sons, échanges, biens,
artisanat, faits locaux et passage). Aucune règle de scénario, consigne ou modèle ajouté ;
`planification.py`, `deliberation.py` et `signes.py` restent intacts.

Six tests nouveaux vérifient les formes propres, définies, indéfinies, singulières/plurielles,
élidées, capitales et références ; la console/MJ simulé, la parole sociale entendue, le don
et la promesse sont contrôlés après recharge. Le cas réel conserve la parole enregistrée
`Je me méfie d'Aubin.` et donne au dossier du MJ `Je me méfie du vieil homme voûté.` ;
l'autre nouvelle dit `doit au vieil homme voûté`, depuis ce que Brune peut nommer.
Les dons vérifient un homme et une femme, leur possession finale et le rendu de la promesse.

Empreintes : 2 h, Relais/auberge × 1985/7/42/2024, référence calculée une seule fois puis
réemployée. Six nuits entièrement identiques ; mesures identiques sur huit. Deux nuits de
l'auberge changent seulement cinq chaînes dans l'état final : graine 1985, quatre souvenirs
de Joss/Tilo, `à La grande fille…` → `à la grande fille…` et `appelle La vieille femme…` →
`appelle la vieille femme…` ; graine 42, une chronique, `près d'âtre` → `près de l'âtre`.
Les états complets de ces deux nuits ont été capturés pour le diagnostic : aucune autre
différence. Le comparateur rend donc 1 pour les textes attendus. Bruts :
`artifacts/empreintes-elision-final.json`, `ecarts-etats.json` et `etats-{reference,branche}/`.

Luna, une passe des deux scripts prescrits : **22 appels / sept tours MJ**, 3,14 appels/tour,
aucun repli ni erreur technique/recharge. `noms-dialogue` : bois demandé à Aubin (quatre
appels), passage et réponse d'Ilse (trois chacun), sans refus. `echanges` : la question du
gardien est refusée sémantiquement et Brune ne se présente pas ; son chuchotement nominal
reste donc localement inaccessible. Seul ce tour manquant est joué sur une copie préparée
avec Brune connue et Aubin inconnu : **quatre appels**, un refus du champ `propos.sujet`
corrigé par Luna, puis le sujet correctement accordé dans les deux dossiers et la citation
originale affichée. Brune répond : « Aubin ? C'est un brave homme… ». Bruts et textes affichés :
`artifacts/bancs-multi/20261024-222722-11984/` et `20261024-223203-10808/`.

Vérification : 127 puis 106 tests ciblés verts, six cas finaux rejoués verts. Suite unique :
**1 776 tests, 16 ignorés, 1 556 s**, trois processus à priorité réduite ; un attendu
« du nom de » adapté à « du nom d'Ilse » (19 tests rejoués verts), une `StopIteration`
de console dans `test_scenarios_libres` non reproduite sans modification (six tests verts).
Cause de cette dernière non établie : la suite brute n'est pas entièrement verte.
Bilan consolidé avec les contrôles finaux : **173 fichiers, 1 777 tests validés, 16 ignorés**,
dans `artifacts/tests-consolides-elision.json`. Aucune seconde suite complète.
Correctif signé SSH **8a9ed47**, signature vérifiée.

Limites : l'accord traite les groupes nominaux déterminés, sans analyser la syntaxe libre ni
réécrire les citations. Le h des noms sans article garde la convention historique d'élision ;
les objets peuvent déclarer `elision`. Les refus sémantiques observés avec Luna restent hors
de cet invariant. Les textes changent, les faits et les règles du monde restent les mêmes.
