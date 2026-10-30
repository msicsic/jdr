# Tâche Codex 364 : E6 reprise, une proposition datée en texte libre ouvre le choix direct

Reprise du lot 363 (branche `codex-e6-libre-date`, non validé, rapport `docs/taches/rapport-codex-363-e6-libre-date.md`).
La passe Luna a montré que la compilation libre ne garantit pas les clauses temporelles : « demain » devient 86 400 s
sans précision, le verrou est mal compilé, des clauses non portées finissent en parole sans contrat (« D'accord » sans
accord). **Décision de l'utilisateur (2026-10-30)** : le texte libre renvoie au choix direct d'E5 ; Luna ne compile pas
seule les dates. C'est la ligne du lot 288 pour les contrats (K0/K1 déterministes d'abord, assistance Luna K2 plus tard).

## Invariant (un seul)
**Quand une saisie libre propose un accord daté, le moteur n'engage rien depuis la compilation : il ouvre le formulaire
de choix direct d'E5, prérempli avec les seuls termes typés et admissibles (destinataire perçu, prestation, prix ; la
limite seulement si elle vient d'une durée explicite dans les mots, sinon champ vide à remplir), et l'accord n'existe
qu'après la validation du formulaire par le consentement U-C.** Tout ce qui ne peut pas être prérempli reste vide et
visible ; une clause non portée (paiement futur, prêt daté, maintien continu, alternative) donne une raison publique de
refus, **jamais une parole d'accord sans contrat** ni une exécution partielle. Le joueur voit et corrige la limite avant
validation : aucun repère inventé n'est engagé.

## Vérification
- Les scripts Luna du 363 (`tools/preparer_banc_e6.py`, `luna-a-jouer.txt`) : « huile dans dix minutes » ouvre le
  formulaire prérempli puis l'accord après validation ; « huile demain » ouvre le formulaire avec la limite vide ou
  signalée à préciser ; verrou, prêt, paiement futur, maintien : refus public, aucun « D'accord » sans contrat. **Luna,
  une passe** sur ces scripts (si la revue automatique bloque, dépose la commande, l'orchestrateur la jouera).
- Parité formulaire/menu E5 : même accord, mêmes comptes, mêmes paroles ; monde, comptes et rendu après recharge.
- Tests ciblés et voisins (E1 à E5, compilateur, comprehension, consentement). Pas de suite complète ni de banc long.

## Contraintes
**Poste : le PC fixe.** Pars de la branche `codex-e6-libre-date` ; fusionne d'abord `origin/integration` (git merge,
sans rebase ; etat-dev : version de l'intégration puis l'entrée du lot). Garde du 363 ce qui sert (délai structuré
`limite: {dans_secondes}` et sa résolution pour le préremplissage) ; retire ce qui engage un accord daté directement
depuis la compilation. Lots en cours : 360 et 362 (régressions de la suite) touchent `paroles.py`, `mj.py`,
`propositions.py` : signale tout recouvrement. Deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-e6-libre-date` (même branche), poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-364-e6-libre-vers-formulaire.md` ; entrée de 8 lignes au plus dans
  `docs/etat-dev.md` (remplace celle du 363).
- Bruts dans `C:\Users\msics\donjon\artifacts\e6-364\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
