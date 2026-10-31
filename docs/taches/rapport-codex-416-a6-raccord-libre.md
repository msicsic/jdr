# Lot 416 — A6, raccord libre et reprise de la revue

31 octobre 2026 — `codex-a6-raccord-libre`, base initiale `integration`
`f1b15632` ; raccord `f7dc9203`, reprise de code `20ac5f1e`.
**Forme de revue renforcée ; validation globale ouverte, tests voisins en cours.**
Le superviseur accepte le coût initial de 2,29 appels/9,08 s par tour, corpus
différent du repère. Aucune optimisation de coût ajoutée.

**Invariant.** La revue des gestes compare obligatoirement chaque paramètre
typé du candidat : opérations, références, méthodes, approches, formes sonores,
nombres et clauses. `comprehension.champs_types_revue` les sépare des proses
`intention`, `justification`, `recit`, sans lire la saisie. Ce contrat de revue
est distinct de l'empreinte conservatrice A5. Les paroles conservent leur revue
de contenu et leurs contrôles distincts ; aucun audit n'est retiré.

`couverture_action.schema/entree/verifier` imposent une table complète : chaque
champ porte sa valeur demandée, un jugement individuel et `perimetre=contrat_type`.
Champs manquants/supplémentaires, classement cosmétique, jugement contredisant
les valeurs et JSON illisible sont refusés avec `attendu`. Tous les écarts
sont contrôlés avant le verdict global ; celui-ci ne peut plus les neutraliser.
Les sens des valeurs viennent du registre commun des quatre familles A2,
exposé sans sélection selon les mots du joueur. Le jugement sémantique reste
à Luna : le moteur n'infère aucune intention depuis un mot-clé ou une prose.

`MJ._auditer_action` redemande une revue illisible une fois, avec son rapport
refusé et son attendu. Un second échec refuse le geste, sans l'exécuter ;
l'ancienne admission sans revue est supprimée dans ce portage. Une valeur
demandée par la revue mais inexprimable dans la grammaire du candidat conteste
sa représentation entière ; le nouveau candidat est intégralement préparé
et revu. Sinon, seuls les champs explicitement contestés sont libérés par A5.
Aucune nouvelle mécanique ni registre d'esprit ; U-P/U-C et sauvegarde conservés.

**Tests.** Première passe ciblée : 24 tests verts ; après finition du contrat,
quatre tests finaux verts en 29,00 s. Contre-épreuves sur sifflement/cri et
références : table exhaustive, champs non classables en cosmétique, refus
après deux rapports invalides, vraie nuance admise, proposition sonore refusée
puis reprise canonique. La vraie boucle console/PontWeb contrôle sons, « Compris »,
conversation, monde et vues après recharge. Les fixtures réseau sont portées
au rapport complet, sans changer leurs oracles de sens. L'assertion historique
« deux revues illisibles puis plan accepté » devient explicitement un refus,
conformément à la décision du superviseur. Les vingt fichiers concernés sont
en cours, puis les quatre fichiers du contrat seront vérifiés sur le code figé.
Un travailleur à priorité réduite ; aucune suite complète.

**Contre-épreuves Luna sur copies.** Trois sur trois avec le contrat complet :
sifflement fidèle admis ; `voix_melodique` pour « je siffle un air joyeux »
refusé sur `reussite.effets.0.texte`, demandé `sifflement` ; nuance joyeux/gai
admise. Une première table ne demandant que les valeurs échouait encore sur
la négative : diagnostic conservé, puis jugements individuels et registre A2
portés dans le contrat commun. Aucun cas particulier dans le moteur ou le prompt.

**Crypte, base `origin/integration` `19b711bf`.** La nouvelle passe Luna
sur copie donne 18 appels/9 tours, aucun repli, aucune erreur de recharge.
Elle répond à la question sans rappel de Gorm. Le rejeu hors réseau des vingt
réponses du fil défaillant du 416, sur cette même base, reproduit exactement
le repli à la même saisie, sans erreur de recharge. Les contrôles concernés
(`narration.py`, `noms.py`, `consignes.py`, `portee_narrative.py`) sont identiques.
Cela prouve un mécanisme de refus déjà présent sur la base pour ces réponses,
pas une fréquence comparable ni une régression causale de génération Luna.
Aucun retrait ou assouplissement d'audit pour masquer le repli.

**Passe autorisée terminée.** Atelier deux fois puis crypte, copies neuves,
`gpt-6-luna`, coffre du dépôt principal : **69 appels/31 tours, 2,23 appels et
9,78 s/tour**, médiane 8,71 s, deux replis, aucune erreur technique/recharge.
Premier atelier : voix substituée refusée ; la correction reste inadéquate et
le sifflement finit sans geste (« Corvus n'a rien tenté »). Second atelier :
sifflement canonique exécuté, sans substitution. **Intention servie une fois
sur deux**, pas une garantie générale. La crypte reproduit le repli historique
sur l'autre côté de la porte. Tous les résultats sont conservés ; aucun rejet
n'est rejoué pour améliorer le bilan. Le contrôle de forme ne garantit pas la
vérité du jugement de Luna ni sa compilation fidèle.
Les preuves initiales du raccord restent dans les bruts : 123 tests distincts
sans échec (un ignoré), sept requêtes publiques couvertes et empreintes
Relais/auberge identiques, 2 h × quatre graines ; aucun code PNJ modifié depuis.
Les résultats finaux des tests voisins et du contrat restent à lire. **Aucune fidélité universelle revendiquée.**

Bruts : `C:/Users/msics/donjon/artifacts/a6-raccord-libre-416/reprise/` :
`fin-base.json`, `diagnostic-crypte.json`, `contre-epreuves-luna-completes.json`,
commandes, copies et fils. Fin attendue de la reprise : `fin.json`.
