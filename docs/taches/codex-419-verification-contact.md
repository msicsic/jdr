# Tâche Codex 419 : une vérification de contact ne fait perdre ni le moyen ni le but

Famille C du lot 414 (`docs/taches/rapport-codex-414-suite-4539dd68.md`, fusionné). Le lot 374 (position crue comme
hypothèse datée) fait expirer la position d'autrui. Un PNJ qui comptait sur quelqu'un (donneur, vendeur, protecteur,
interlocuteur d'un appel ou d'un rendez-vous) inspecte, questionne ou appelle désormais avant d'agir. Plusieurs
méthodes ont basculé parce que cette vérification **remplace ou fait perdre** le moyen et l'intention qu'elle devait
préparer :
- `test_recours_prioritaire` (deux méthodes, intention absente après l'aide adoptée) ;
- `test_contre_offre`, `test_offre_sensee`, `test_propositions_redites` (recours ou appel attendus remplacés) ;
- `test_achat_promis_annule` (offre retardée) ;
- `test_agendas_activation` (plus de plan pour le marchand) ;
- `test_gardien_detresse` (cri attendu remplacé) ;
- `test_empathie_peur.test_gorm_attend_un_moyen_sur_pour_le_feu_mais_execute_encore_sa_ronde` ;
- `test_dynamique_besoins.test_lucien_attend_une_information_apres_la_reprise_du_ballot` ;
- `test_signalements` (deux méthodes) ;
- `test_eau.test_l_eau_qui_monte_fait_fuir_vers_la_galerie`.

La dernière colonne du rapport 414 donne, pour chacune, la question précise. Bruts :
`C:\Users\msics\donjon\artifacts\suite-4539dd68-414\` (laptop).

Lis `AGENTS.md`, `docs/etat-dev.md` (court), les rapports 374, 413, 414 et 417.

## Invariant (un seul)
**Quand la position d'un contact nécessaire est expirée, la vérification (inspection, question, appel) est un préfixe du
plan qui porte le moyen et le but qu'elle prépare. Elle se fait une fois par hypothèse (consommée, lot 374), puis le
plan reprend avec la position constatée ou apprise. Si le contact est trouvé absent, le moyen cède à son recours
ordinaire.** La vérification ne fait perdre ni l'intention, ni l'aide adoptée, ni la demande ou l'offre en cours. Elle ne
se répète pas sans preuve nouvelle. Elle ne remplace pas un cri ou un appel qui était lui-même le moyen.

Pour chaque méthode, le rapport classe le cas :
- défaut du raccord vérification/plan : à corriger dans le contrat commun ;
- attente devenue fausse par la décision du 374 (un PNJ « savait » où était l'autre) : à adapter, preuve citée ;
- question ouverte : à lister avec sa question précise.

Ne touche pas aux méthodes de la famille R (lot 417) ni aux empreintes (famille E).

## Vérification
Les fichiers concernés ; cas réel et autre cas après recharge, même laps entier ou découpé. Banc rapide 4 h, quatre
graines, auberge, mine et crue, contre la base : appels et retours suspects au plus ceux de la base. Pas de suite
complète, ni Luna.

## Contraintes
**Poste : le laptop.** Lots en cours : 402 (vérification d'intégration, calcul seul), 416 (A6, `mj.py`), 418 (S1m
renoncements : `memoire.py`, `deliberation.py` ; touche le moins possible ses fonctions, et fusionne `origin/integration`
avant de livrer). Pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs
détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin
(https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-verification-contact`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-419-verification-contact.md` ; entrée « non fusionnée » de 8 lignes au
  plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\verification-contact-419\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
