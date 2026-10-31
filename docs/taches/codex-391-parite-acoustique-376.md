# Tâche Codex 391 : parité acoustique du laps entier et découpé après le lot 376

Question Q1 du lot 390 (`docs/taches/rapport-codex-390-suite-663d1308.md`, fusionné). Le lot 376 (« les messages ne
dépendent pas du découpage du temps », `rapport-codex-376-*.md`) a fait basculer trois méthodes que le 390 a
attribuées sans les corriger :
- `test_contact_position_inconnue.ContactPositionInconnueTests.test_contenant_dans_une_autre_salle` : messages
  différents selon le découpage ;
- `test_reprise_contact.RepriseContactTests.test_ilse_capture_141000_pas_de_reprise_par_la_minute` : des sons
  supplémentaires dans le bloc entier ;
- `test_etapes_chainees.EtapesTests.test_captures_mine_et_auberge_memes_plans_visites_monde_et_rendu_recharges` :
  les empreintes du monde ont changé.

Bruts du 390 : `C:\Users\msics\donjon\artifacts\suite-663d1308-390\` (PC fixe, `bissection/attribution.json`).
Lis `AGENTS.md`, `docs/etat-dev.md` (court), les rapports 376 et 390.

## Invariant (un seul)
**Un même laps, attendu d'un bloc ou découpé et rechargé en route, donne le même monde et les mêmes messages au joueur
(contrat du 376 et de `docs/plan-temps.md`).** Pour chaque méthode, trouve l'événement où le bloc et le découpage
divergent. Deux cas :
- c'est un défaut réel de parité, par exemple un son retenu deux fois ou émis à une frontière : corrige-le dans le
  contrat commun (ouïe, rendu événementiel, `ouie._au_joueur` du 390) ;
- l'attente du test datait d'avant le 376 et la nouvelle valeur est juste : adapte-la en citant la preuve, sans
  assouplir la parité.

Les empreintes de `etapes_chainees` ne se réancrent qu'avec la liste exacte des champs changés et leur cause.

## Vérification
Les trois fichiers, plus `test_temps_etat`, `test_messages_decoupage` (ou le fichier du 376) et `test_ouie_commune` ;
cas réel et autre cas, laps entier contre découpé avec recharge, état complet et texte affiché. Si du code du jeu
change : empreintes 2 h, Relais, mine, auberge et crue, quatre graines. Pas de suite complète, ni Luna.

## Contraintes
**Poste : le laptop.** Lots en cours : 374 (position crue), 375 (rouges e0826ef, laptop), 380 (U-M social comptes),
381 (A2 passage) ; pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs
longs détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin
(https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-parite-acoustique`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-391-parite-acoustique-376.md` ; entrée « non fusionnée » de 8 lignes
  au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\parite-acoustique-391\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
