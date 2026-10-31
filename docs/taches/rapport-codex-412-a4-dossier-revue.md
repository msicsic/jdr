# Lot 412 — A4, dossier de revue

31 octobre 2026 — `codex-a4-dossier-revue`, base `integration`
`2634e48e7ba39533bcb9e876487bac7536ee57af`, non fusionnée.

**Verdict : non validé pour fusion.** Le raccord du dossier et la détection
de l’omission sonore sont prouvés ; la passe Luna révèle une substitution
de manière sonore acceptée après un refus de fidélité. Aucun audit retiré.

**Invariant et changement.** `comprehension.sens_propose` joint les paramètres,
la manière et les récits transitoires proposés aux contrats communs de
séquence/attente, expression/son et passage. `couverture_action.entree` les
associe à chaque étape développée, dont celles des raccourcis, aux effets de
réussite/échec/échec critique et aux conditions d’exécution. Les autres
opérations conservent paramètres et titre moteur ; la parole garde son
contrat distinct. `MJ._auditer_action` fige ce dossier. La revue distingue
admission et fidélité, et compare les conséquences observables, même
temporaires, les clauses et la manière. Les textes libres ne prouvent aucun
effet. Mécaniques et registres d’esprit inchangés, aucune sélection sur la saisie.

**Preuves.** Cinq nouveaux tests : pureté du dossier, son présent accepté,
omission refusée avec l’effet dans `attendu`, attente développée, manière
littérale et branches distinctes. La vraie boucle console/PontWeb corrige
une omission pour « je fredonne doucement » au Relais et un rythme corporel :
un son, aucun jet, sauvegarde avant affichage et réponse retrouvée après
reprise. Deux minutes en bloc ou huit tranches de quinze secondes avec
recharges donnent le même monde complet et les mêmes vues. Les verdicts y
sont simulés. **171 tests ciblés, un ignoré** : seul échec initial, l’ancien
texte exact d’`attendu` ; le fichier adapté est rejoué **18/18, 11,50 s**.
Les cinq tests renforcés passent en **13,97 s**. L’égalité exacte de
`test_contre_revue_d_action_cite_le_plan` reste entière : sa fin attendue suit
le changement voulu (conséquences observables, clauses, manière).

**Mesures finales.** Empreintes **identiques**, Relais/auberge, 2 h × graines
1985/7/42/2024 : chronique, mesures et monde complet, aucun plantage.
Référence absente calculée une fois et cachée, puis branche ; aucune
comparaison de vitesse. Une passe Luna sur copies, quatre parties :
**62 appels / 26 tours MJ = 2,38 appels et 9,19 s/tour**, médiane 8,40 s ;
aucune interruption, erreur technique, erreur de recharge ni repli.
Onze refus, quatre obstacles narratifs, trois relances. Hors de ce dénominateur,
les quatre contre-épreuves directes sont justes (quatre appels, 23,75 s avec
préparation/fermeture) : deux sons présents acceptés, deux omissions refusées
avec le manque dans `attendu`. Fredonnement émis dans les deux scripts ;
omission du rythme effectivement refusée puis corrigée dans le script dédié.

**Limite bloquante.** Dans `luna/atelier.json`, « je siffle un air joyeux »
produit d’abord `emettre_son/sifflement`. La revue refuse la manière absente,
puis accepte `son/voix_melodique` : le rendu fait entendre des notes de voix,
ce qui substitue la modalité. Le contrat commun entre manière proposée,
opération et effet n’est donc pas encore garanti ; aucun succès global de
fidélité revendiqué. Les refus de préparation restent sur leur voie et le
repli historique après deux revues de geste illisibles reste présent.

Bruts : `C:/Users/msics/donjon/artifacts/a4-dossier-revue-412/`, notamment
`fin-reprise.json`, `mesures-luna.json`, `contre-epreuves-luna.json`,
`empreintes.json`, `commandes-reprise.json`. Deux travailleurs au plus,
priorité réduite ; aucune suite complète ni seconde passe Luna.
