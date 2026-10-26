# Lot 123 — Vérification Luna de l’intégration 057766f

26 octobre 2026 — **Validation partielle : remboursement rétabli, zéro audit illisible ; faux refus et confusion comptable subsistent.** Aucun code modifié. Même méthode et vingt scripts que les lots 99/111 : **40 parties, 302 saisies, 136 tours MJ, 437 appels**, `gpt-6-luna`/ChatGPT medium/libre, budget 200 par groupe/passe, quatre processus au plus, priorité `BelowNormal`, copies temporaires, coffre principal. Branche issue d’`e8b4ad7`, code identique à **057766f**. Quarante parties rangées sous ce commit, SHA-256 source/cache identiques ; **95 fichiers des références 42bb9c0 et 91a4351 inchangés**, exclusivement relus. Bruts du lot 111 absents du poste : parties retrouvées dans son cache, scripts et empreinte du harnais vérifiés avant lancement. Aucun rejeu des références historiques absentes.

Chaque cellule : **main (42bb9c0) → 91a4351 → 057766f**. Moyennes des deux passes ; médiane sur les tours réunis. Refus = validations moteur/fidélité/contre-revue ; relances/replis = détecteurs historiques. Refus locaux sans appel hors compteur ; main couvre onze scripts. Illisibles = appels d’audit rejetés pour forme, y compris ceux redemandés sans obstacle final : rapports bruts relus hors ligne, lecteur historique pour main, lecteur rétrocompatible pour 91a4351. Détail par groupe/fonction dans les bruts.

| Groupe | appels/tour | s/tour | médiane s | relances | refus | tours avec refus | replis | illisibles | tours MJ |
|---|---|---|---|---|---|---|---|---|---|
| référence | 3.05→3.08→2.92 | 12.05→10.28→10.63 | 10.66→9.32→10.07 | 3→5→4 | 12.5→8→8.5 | 8→6→6 | 0.5→0.5→0 | 0→7.5→0 | 33→31→31 |
| signes | 2.57→3.25→2.83 | 11.33→11.57→11.33 | 8.71→8.09→9.64 | 0.5→2.5→2.5 | 2→0→0 | 1→0→0 | 0→0→0 | 0→4.5→0 | 7→6→6 |
| ambiance | 3.67→3.33→2.00 | 16.63→12.04→7.79 | 15.77→10.50→6.69 | 2.5→1.5→0 | 0→0→0 | 0→0→0 | 0→0→0 | 0→2→0 | 3→3→3 |
| noms-soir | 3.57→4.62→4.46 | 14.13→15.48→17.18 | 12.46→12.77→15.18 | 2→3.5→3.5 | 1.5→2→1.5 | 1.5→2→1.5 | 0→0.5→0 | 0→1.5→0 | 14→13→13 |
| ressources-comptes | —→5.00→5.00 | —→17.62→19.80 | —→14.58→19.03 | —→1→2.5 | —→1→0 | —→1→0 | —→0.5→0 | —→2→0 | —→5→5 |
| sous-obstacle | —→1.95→2.20 | —→7.14→8.26 | —→7.22→7.50 | —→0→1 | —→7→7.5 | —→4→4 | —→0→0 | —→0→0 | —→10→10 |
| onze | 3.15→3.49→3.24 | 12.71→11.80→12.16 | 10.82→9.95→11.14 | 8→12.5→10 | 16→10→10 | 10.5→8→7.5 | 0.5→1→0 | 0→15.5→0 | 57→53→53 |
| ensemble vingt | —→3.38→3.21 | —→11.54→12.15 | —→9.57→10.91 | —→13.5→13.5 | —→18→17.5 | —→13→11.5 | —→1.5→0 | —→17.5→0 | —→68→68 |

| Fonction (s/tour MJ) | onze : main → 91a4351 → 057766f | vingt : 91a4351 → 057766f |
|---|---|---|
| auditer_narration | 4.90→4.57→4.31 | 4.05→3.95 |
| auditer_portee | 0.00→0.00→0.00 | 0.00→0.00 |
| contre_revue | 0.35→0.27→0.33 | 0.31→0.36 |
| fidelite | 0.31→0.68→0.74 | 0.78→0.83 |
| interpretation | 5.04→4.31→4.71 | 4.54→4.85 |
| recit | 1.65→1.23→1.38 | 1.25→1.37 |
| revision | 0.46→0.74→0.69 | 0.61→0.74 |

Sur vingt : **459→437 appels (−4,8 %)**, **11,543→12,146 s/tour (+5,2 %)**, médiane **9,57→10,91 s** ; **156→135 audits, 35→0 illisibles**, trois replis→zéro. Passes nouvelles : **3,38/3,04 appels/tour**, **13,19/11,10 s/tour**. Charges historiques différentes et poste partagé : aucune attribution causale de latence. Rappel documentaire, sans rejeu : 882907c→b0042c9 donnait **2,85→2,99 appels/tour, 12,7→10,3 s/tour**, 15→16 refus et 7,5→6,5 relances par passe (rapports 99/111).

**Défauts suivis** (indices de saisie à partir de zéro).

- **N4, remboursement Gorm exécuté 2/2**, `comptes` n°1, « Gorm, rends-moi les deux pièces que tu me dois. » : comptes moteur `marchand→joueur`, deux pièces rendues, dette absente, Brune toujours débitrice. P1 « ces deux pièces te revenaient. Elles sont rendues » ; p2 « Gorm te rend les deux pièces ». Aucun faux refus de quantité ; **6/6 appels**, contre 6/10 en 111. Faux refus narratif encore présent p1 : « La réponse établie dit que Gorm rend 2 pièces, pas qu’il les rend maintenant ; aucun geste actuel ne le prouve. » (texte exact complet dans le fil) ; ce refus ne perd plus le paiement.
- **N5, réserve sur “les faits” non reproduite 2/2**, `luna-restes-ambiance` n°1 : p1 « La conduite reste silencieuse » ; p2 « le faible crépitement du brasero ». Aucune réserve technique, deux appels chacun ; pas de garantie sur toutes les ambiances.
- **Achat exécuté et livré 2/2**, `soir-appel` n°5–6 : joueur→Aubin trois pièces rendues, Aubin→joueur une part de `planches_1` due ; planches portées au premier `ouest` rechargé. P1 « Les trois pièces lui ont été remises ; il te doit maintenant une part ». **Confusion persistante p2** : au remboursement n°4 « Pour les planches, je les avais payées », puis à l’achat « L’argent est rendu ; la planche, je te la dois encore ». Paroles de PNJ ; aucune inversion moteur constatée.
- **Identité refusée après présentation : non reproduite sous la même forme**, `soir-noir` n°2 « Je m’appelle Ilse » aux deux passes. N°5 : p1 « Une voix qui se dit Ilse. Et toi, qui es-tu ? », p2 « Tu n’es pas Brune… Qui es-tu, alors ? ». Pas de prétendu ancien refus, mais réponse dégradée et faux refus du passé (N7) : critère seulement partiel.
- **N1 non reproduit 2/2**, `atelier` n°8 : p1 « Tu vois le mur de l’atelier au nord-ouest », p2 « Tu en distingues la masse de pierre » ; trois appels chacun, aucune erreur de contrat.
- **N2 non reproduit, cas exact non exercé** : `soir-appel` dit « remises/remise », sans génération de la phrase historique « ne t’ont pas encore été données ». Ne prouve pas son admission.
- **N3 non reproduit 2/2**, `soir-noir` n°1 : parole « il y a quelqu’un ? » exécutée, réponses « Oui, il y a quelqu’un » / « Oui… il y a quelqu’un ». Cinq appels chacun après refus de fidélité, aucun abandon.
- **Fausse absence dans le noir non reproduite 2/2**, `signes-noir` n°2 : « tu ne la vois ni ne l’entends dans cette obscurité » / « Tu ne vois pas Ilse dans l’obscurité ». Corvus, Ilse et Brune restent dans l’antichambre rechargée. **N6 persiste** : `signes-guet` p1 n°1 rejette « tu ne le vois pas » pour couverture partielle, six appels ; p2 rejette même « Tu ne sais pas où se trouve Gorm », quatre appels.

**Nouveaux constats**, sans correction ni causalité attribuée à un lot.

7. **N7 — Rappel conforme rejeté**, `soir-noir` p1 n°5, saisie « je demande à la voix comment elle s’appelle ». Candidat « Je te l’ai déjà dit : je m’appelle Ilse » refusé : l’audit prétend que la voix avait dit « Je m’appelle une voix qui se dit Ilse ». Or `echanges_passes.voix_1` contient exactement « Je m’appelle Ilse. Et toi, qui es-tu ? ». Affiché : « Une voix qui se dit Ilse. Et toi, qui es-tu ? », huit appels. Cause probable : confusion sémantique entre référence publique et mots prononcés ; le dossier contient bien le précédent exact.
8. **N8 — Discours indirect transformé en réplique à la deuxième personne**, `ressources` p2 n°1, « je demande à Brune si elle a de quoi manger » → « Tu dis à Brune : “Tu demandes à Brune si elle a de quoi manger.” » ; p1 produisait « Brune, tu as de quoi manger ? ». Quatre appels, aucun refus. Cause probable : restitution littérale d’une reformulation descriptive dans la parole exécutée, admise par la fidélité. Constat de formulation, sans perte de transaction ni preuve de contradiction mécanique.

**Incidents et limites.** Aucun plantage du jeu, erreur réseau, budget épuisé, saisie écartée ni défaut de recharge. Incident auxiliaire avant tout appel : écriture des bruts hors du worktree refusée par le bac à sable (`PermissionError [WinError 5]`), reprise autorisée avec élévation ; trace complète `erreur-lancement.txt`. Quatorze parcours sous obstacle : mêmes positions, possessions, passages, blocages et durées rechargés que 91a4351, dont 12/12/6 s ; rendus de réussite/refus cohérents. Gorm dos tourné non inventé en crypte n°26, aucune prise. Recherche de traces toujours « Le sol en pierre ». Le harnais recharge après sauvegarde et en fin de partie ; six premiers `regarder` précèdent la sauvegarde, panneaux seulement capturés par marqueurs, solde d’or absent du résumé. Comptes contrôlés dans l’issue moteur, pas dans un solde rechargé capturé : aucune garantie universelle de rendu persistant ni de vérité sémantique. Aucune suite moteur relancée, aucun code corrigé. Aucune clé de signature configurée dans Git sur ce poste : commit non signé.

Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-057766f\` : quarante JSON/HTML, huit journaux (quatre groupes × deux passes), mesures, revue intégrale, contrôles de recharge, empreintes avant/après, preuves, scripts de lancement/analyse. Références historiques absentes uniquement citées d’après les rapports.
