# Lot 32 — Questions sur une personne connue absente

24 octobre 2026. Branche `codex-question-absent`, **non fusionnée**, base `2590c4a`,
brief `894187d`. Correctif signé SSH **b8a1f84**.

**Invariant et fonctions.** Connaître un nom permet de demander ce que l'on sait de son
porteur ; cela ne donne pas accès à son corps. `noms.verifier_saisie`, commun à la console,
au parseur et au MJ, réemploie `commandes.est_question` après l'analyse de
parole et exclut `commandes.faisabilite`. `verifier_nom` exige toujours le lien nominal,
mais exige la perception seulement pour une cible de geste. Une perception nommée laisse
au moteur son refus précis ; une adresse passe dès la saisie par `paroles.destinataires`,
avec ses règles de regard et d'ouïe. `commandes.cri` préserve d'abord les appels et leurs
réponses négociées à distance. Chaque refus garde sa cause et un `attendu` adapté.
Aucun prompt ajouté ; Luna reste `gpt-6-luna`, comparaison désactivée.

**Preuves après recharge.** Sept nouveaux tests, **104 tests ciblés validés**. Captures
`signes-guet` et `signes-noir` : une interprétation et un audit, réponse persistée avant
affichage, état et rendu inchangés ; ni corps ni esprit des absents transmis. Cas réels et
analogues : gestes, faisabilité, perceptions, noms sans lien, paroles adressées et appels
distants ; refus à zéro appel en ligne et hors ligne. Suite complète unique, trois
processus à priorité réduite (1 522,8 s), puis bilan consolidé : **1 670 tests, 15 ignorés,
aucun échec restant**, 155 fichiers. Deux reprises ciblées vertes (38 tests,
70,3 s ; 10 tests, 21,6 s) corrigent le refus prématuré d'une réponse d'appel et adaptent
l'ancienne attente d'interpellation au refus local, sans relancer la suite entière.

**Luna, une seule passe**, ChatGPT, effort `medium`, priorité réduite, coffre principal
via `SEUIL_AUTH`, copies temporaires seulement (`tools/banc_parties.py --fil`).

| Script | Appels | Appels/tour MJ | Secondes/tour MJ | Replis |
|---|---:|---:|---:|---:|
| signes-guet | 4 | 2,00 | 12,3 | 0 |
| signes-noir | 2 | 2,00 | 12,1 | 0 |
| echanges | 12 | 4,00 | 20,8 | 0 |
| noms-dialogue | 14 | 3,50 | 14,9 | 0 |

Les trois questions sur les absents passent au MJ ; il rappelle les pas entendus sans les
attribuer, ou dit ignorer la peur d'Ilse. Aucun guet caché révélé ni activité invisible
affirmée. « observer Ilse » : **0 appel**, manque de lumière pour « cette personne » ;
« je pousse Aubin » non relié : **0 appel**, sans jet ni déplacement. Brune reliée s'écarte,
Ilse répond. Aucun arrêt ni rechargement invalide. Deux tours relancés hors des questions
ciblées : audience de la salutation et de la question collective sur le bois refusée par
la contre-revue ; aucun texte refusé affiché. Les trois mentions sans
fondement comptées dans `echanges` sont les noms cités dans les refus locaux.

**Banc rapide.** Relais, 4 h, graines 1985/7/42/2024, un processus, base puis branche.
Référence calculée une fois et rangée dans `artifacts/references/2590c4a…/` du dépôt
principal. États finaux, mesures hors temps de calcul, relevés et audit identiques par
graine ; aucun plantage, usurpation ni violation. Constats inchangés : un `fige_presse`,
un `noir_long`. Aucune conclusion de performance sur ces lancements séquentiels.

**Limites.** La reconnaissance des questions reste syntaxique : ponctuation, interrogatifs,
inversion. Saisies mixtes, questions sans marque reconnue et noms absents du lexique restent
des limites. La compatibilité mécanique de la prose reste en partie sémantique ; cette
passe ne garantit pas toute absence de contradiction. Traces : `artifacts/question-absent/`.
