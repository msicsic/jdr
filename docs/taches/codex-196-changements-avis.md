# Tâche 196 (diagnostic) : une parade générale aux changements d'avis intempestifs des PNJ

Demande de l'utilisateur, 2026-10-27 : **trouver une parade générale aux changements d'avis intempestifs, pas au cas par cas.**
Diagnostic et proposition de conception : **aucun fichier de `donjon/`, scénario ou test du jeu modifié**, aucune fusion, pas de
Luna. Tu peux écrire un outil de mesure dans `tools/` (un détecteur) et le rapport. **Poste : le laptop**
(`C:\Users\msics\donjon`, l'utilisateur y travaille et une suite de tests y tourne) : **un seul processus de calcul** à la fois,
priorité réduite. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`, `PYTHONIOENCODING=utf-8`. Bruts dans
`C:\Users\msics\donjon\artifacts\avis-196\`. Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

## Le problème
Les PNJ (`deliberation.choisir`, appelé à chaque événement et au moins chaque minute, puis `planification.chercher`) changent
d'avis en boucle dans des familles qu'on a corrigées une par une : fuite ↔ lumière (lot 155), les deux pentes d'eau de Gorm
(lot 58), le garde-manger ouvert et fermé des centaines de fois (lots 103 et `boucles-pnj`), lumière ↔ abri (`besoins`,
`boucles-pnj`), aller voir ↔ garder (lot `ouie-temoins`), séjour lumière/inspection d'Aubin (lot 90), torche allumée/éteinte de
Brune (lot 146 e), avertissements et lectures redits (lots 64, 108, 191), alternances entretien/garde de Gorm (lots 174, 188).
Il en est résulté une dizaine de parades locales : `INERTIE`, `REPRISE`, l'hystérésis entre recours d'un même besoin, les refus
retenus selon leur cause, les gestes défaits (`DEFAIT`), les attentes bornées, le sommeil et le réveil des agendas,
`REVOIR_FEU`, les indices de recherche, la stabilité des agendas actifs… Chaque nouvelle famille passe à côté.

Hypothèse de l'orchestrateur, **à vérifier ou réfuter, pas à reprendre telle quelle** : trois causes générales.
1. **Choix sans engagement** : chaque choix compare tout à zéro ; deux options presque égales l'emportent tour à tour ; rien ne
   compte le coût d'un changement (trajet fait, progrès perdu).
2. **Deux juges pour la même chose** : planificateur et exécution, ou choix et continuation, n'évaluent pas pareil (lumière à
   la salle ou devant la cible, eau à la destination ou en chemin, « fini » avant d'avoir servi).
3. **Croyances qui basculent sans fait nouveau** : deux sources se remplacent (deux mesures, deux souvenirs) et la décision suit.

## Ce qu'on te demande
Lis `AGENTS.md` (règle de conception : invariant général, jamais le cas de l'exemple), `docs/plan-agendas.md` (§ 6.1, 6.4 :
hystérésis et ténacité, A4c « hystérésis générale dans le score », jamais faite), `docs/plan-decision.md`,
`docs/plan-planificateur.md` (sections des boucles), puis `deliberation.py` (`choisir`, `_candidats`, `Palier`, `Urgence`,
inertie), `agendas.py` (stabilité), `esprits.py` (révision des croyances). Les rapports des lots cités sont dans `docs/taches/`.
1. **Inventaire des parades** existantes : où, ce qu'elles empêchent, ce qu'elles laissent passer, et ce qu'elles ont en commun.
2. **Inventaire des boucles connues** et classement par cause (les trois ci-dessus, ou d'autres que tu trouves), avec la
   preuve dans le code ou les rapports.
3. **Un détecteur générique** (`tools/`), sans changer une nuit : « un PNJ revient à une décision qu'il vient de quitter alors
   qu'aucune des entrées de cette décision n'a changé » (définis ces entrées à partir de ce que lit réellement le choix ; un
   aller-retour justifié par une entrée nouvelle n'est pas une faute). Fais-le tourner sur des nuits existantes ou rejouées :
   quatre scénarios et le hameau, quelques graines, 4 h, un processus. Donne le nombre et les exemples d'allers-retours non
   justifiés, et ce que les parades actuelles laissent passer.
4. **Une proposition de contrat commun** : ce qui fait garder ou quitter une intention (une liste fermée de raisons :
   accompli, impossible, entrée de décision changée, palier d'urgence franchi, autre option meilleure d'une marge au moins égale
   au coût du changement, ou mieux si tu trouves), le « juge unique » entre choisir, continuer et dire « fini », et la règle de
   révision des croyances. Pour chaque proposition : les parades qu'elle rendrait inutiles, ce qu'elle risque (PNJ qui
   s'entêtent, réactions retardées à une urgence, coût), et comment la vérifier comme une garantie (à la manière de `VERIFIER`).
5. **Un découpage en lots** d'un invariant chacun (30 à 45 min), dans l'ordre, avec ce que chacun mesure.

## Livraison
Branche `codex-changements-avis` : `docs/taches/rapport-codex-196-changements-avis.md` (deux à trois pages), le détecteur dans
`tools/` si tu l'as écrit, une ligne dans `docs/etat-dev.md`. Commit local ; ne pousse pas, ne fusionne pas, ne touche à aucune
autre branche.
