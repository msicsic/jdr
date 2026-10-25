# Lot 79 — Vérification Luna de l'intégration 882907c

25 octobre 2026 — **Validation partielle : remboursements et lumière restitués ; achat exécuté une passe sur deux,
contradictions mécaniques encore affichées.** Aucun changement de code.
Deux passes des vingt scripts du lot 70 : **40 parties, 302 saisies, 388 appels**, `gpt-6-luna`/ChatGPT,
medium/libre, budget 200 par groupe/passe ; quatre exécutions au plus, priorité réduite, copies temporaires,
`SEUIL_AUTH` principal. Aucun arrêt, erreur technique/recharge, tour écarté ou repli détecté.
Quarante parties rangées dans le cache de **882907c**, identité SHA-256 vérifiée.
**42bb9c0, f033364 et fbcf0ff exclusivement relus du cache** : 102 parties inchangées, mesures du lot 70 reproduites exactement.

Chaque cellule : **main→f033364→fbcf0ff→882907c**, moyenne des deux passes, mêmes scripts et harnais.
Ratios sur les tours MJ ; relances narratives, refus moteur/contre-revue et replis du détecteur historique.
Secondes historiques sous des charges différentes : aucune conclusion causale de performance.

| Groupe | appels/tour | s/tour | relances | refus | tours avec refus | replis | tours MJ |
|---|---|---|---|---|---|---|---|
| Référence : relais/crypte/atelier/echanges | 3,05→2,89→3,05→2,63 | 12,1→10,8→12,9→11,6 | 3→2→4→1 | 12,5→9→12→7 | 8→7→8→6 | 0,5→0→0→0 | 33→31→31→31 |
| Signes : écart/noir/guet | 2,57→2,00→2,67→2,50 | 11,3→9,4→12,9→13,7 | 0,5→0→2→1,5 | 2→0→0→0 | 1→0→0→0 | 0→0→0→0 | 7→6→6→6 |
| Ambiance | 3,67→2,00→2,33→2,00 | 16,6→9,1→13,8→10,7 | 2,5→0→0,5→0 | 0→0→0→0 | 0→0→0→0 | 0→0→0→0 | 3→3→3→3 |
| Noms et soir | 3,57→3,81→4,04→3,96 | 14,1→13,3→18,5→15,8 | 2→0,5→2,5→2,5 | 1,5→1,5→1,5→0,5 | 1,5→1,5→1,5→0,5 | 0→0→1→0 | 14→13→13→13 |
| **Ensemble onze** | 3,15→2,96→3,21→2,91 | 12,7→11,1→14,4→12,8 | 8→2,5→9→5 | 16→10,5→13,5→7,5 | 10,5→8,5→9,5→6,5 | 0,5→0→1→0 | 57→53→53→53 |
| Ressources/comptes | —→3,00→3,40→3,60 | —→10,8→14,4→16,5 | —→0→1→1,5 | —→0→0→0 | —→0→0→0 | —→0→0→0 | —→3→5→5 |
| Sept sous-obstacle | —→1,90→2,10→2,20 | —→7,8→9,0→10,5 | —→0→0,5→1 | —→7→7,5→7,5 | —→4→4→4 | —→0→0→0 | —→10→10→10 |
| **Ensemble vingt** | —→2,80→3,06→2,85 | —→10,6→13,6→12,7 | —→2,5→10,5→7,5 | —→17,5→21→15 | —→12,5→13,5→10,5 | —→0→1→0 | —→66→68→68 |

Onze scripts : **2,81/3,00 appels/tour**, **12,5/13,1 s/tour** ; vingt : **2,75/2,96**, **12,3/13,2 s/tour**.
La baisse des appels ne suffit pas à valider le comportement : l'achat manque en passe 2.
`comptes` conserve la préparation nominative du lot 70, différente de f033364.

**Les huit constats du lot 70** (indices de saisie à partir de zéro ; non-reproduction ne vaut pas garantie générale).

| Ancien constat | Résultat sur 882907c |
|---|---|
| 1. Remboursement masqué | Corrigé dans les deux parties `soir-appel` n° 4 : « te rend les deux pièces » ; or 24→26. |
| 2. Marché rejeté | Partiel, `soir-appel` n° 5 : passe 1 « je te remettrai la planche », paiement 26→23, puis `planches_1` portée après le premier `ouest` rechargé ; passe 2 sans achat (N1). |
| 3. Remboursement vrai rejeté | Persiste, `soir-appel` passe 1 n° 4 : « Les planches, elles, restent à moi » extrait comme compte-objet absent, rejeté ; sortie corrigée « Tiens, tes deux pièces », six appels, aucun repli. |
| 4. Mauvaise cible | Non reproduit, `relais` n° 22 : « Tu ne vois pas de pied-de-biche… », deux/quatre appels ; aucune proposition visant le couteau, inventaire rechargé inchangé. |
| 5. Faux refus spatial | Non reproduit, `crypte` n° 26 : souvenir « trois mètres vers le sud et un mètre vers l’est », trois appels chaque fois, aucun rejet narratif ; distance toujours refusée par le moteur. Nouveau défaut d'orientation en N3. |
| 6. Lumière rejetée | Corrigé dans les deux parties `crypte` n° 25 : « ta lanterne et […] un brasero », deux appels ; extraction des deux éclairages, brasero contributeur hors de vue. |
| 7. Mot « refus » censuré | Non reproduit, mais mot non exercé dans les récits proposés : `comptes` n° 2 « Non. Ces deux pièces… » / « Je ne te les rends pas », sans rejet. Cette campagne seule ne clôt pas ce cas lexical. |
| 8. Présentation rejetée | Non reproduit, `soir-noir` n° 2 : « C’est Ilse » / « Je suis Ilse », puis adresse « une voix qui se dit Ilse ». Passe 2 : ajout de présentation de Corvus bloqué avant parole, corrigé en « Qui est là ? », cinq appels. |

Gorm rembourse aux deux passes de `comptes`, or 24→26 ; Brune reste débitrice de deux pièces.
Prime de vingt pièces, impressions répétées d'Ilse et souvenir de la poutre dans le dos maintenus aux deux passes.
Les quatorze parcours sous-obstacle sont cohérents après recharge : questions sans action, passages 12/12/6 s,
refus sans déplacement ni temps consommé ; aucune forme inventée enregistrée.

**Défauts nouveaux numérotés** (cause probable ; aucune correction ni attribution certaine à un lot).

1. **N1 — Paiement réduit à des mots**, `soir-appel`, passe 2 n° 5, « je paie Aubin trois pièces pour une de ses planches » :
   « Il ne confirme pas l’échange ; les planches restent à lui. » Contenu `propos` sans opération, déclaré conforme par
   la contre-revue ; accord narratif ensuite refusé, demande abandonnée. Or 26, aucune `planches_1` portée après recharge.
   Le contrat saisie/contenu/couverture perd l'effet demandé ; ce n'est pas un refus de vente calculé par le moteur.
2. **N2 — Hors de vue devient absent**, `signes-noir`, passe 2 n° 2, « Ilse a-t-elle peur de Brune ? » :
   « elle n’est pas là pour que tu le lui demandes ». Ilse est pourtant dans l'antichambre avec Corvus après recharge.
   L'audit dit lui-même que l'absence n'est pas établie, mais classe la phrase `mecanique`/`etablie` ; affichage en deux appels.
3. **N3 — Orientation fausse admise**, `crypte`, passe 2 n° 26, attente puis prise discrète des crochets :
   « Gorm est […] face à toi ». Gorm est au sud-ouest du joueur et orienté sud-est dans le contexte ;
   l'audit qualifie cette assertion de contredite, tout en renvoyant `mecanique`/`etablie`. Trois appels, phrase affichée.
   Comme N2, incohérence entre motif et verdict sémantique ; aucune prise exécutée.
4. **N4 — Compte exact mal identifié**, `comptes`, passe 1 n° 1, « Gorm, rends-moi les deux pièces que tu me dois. » :
   « Gorm te rend les deux pièces » est rejeté après extraction `gorm`/`Corvus` au lieu de `marchand`/`joueur`.
   Sortie finale « Gorm te rend 2 pièces », cinq appels ; mêmes rôles et remboursement, faux rejet dû aux références de l'audit.

**Limites et bruts.** Faux audits d'ignorance, d'ambiance et de ton persistent ; recherche de traces encore
« Le sol en pierre », déjà connue. Le harnais recharge après sauvegarde et en fin de partie ; six premiers `regarder`
précèdent la première sauvegarde. Il capture les marqueurs des panneaux, pas leur rendu : aucune garantie générale nouvelle
sur le rendu persistant ou les contradictions mécaniques. Aucun test moteur supplémentaire, code, modèle, consigne ou `main` modifié.
Bruts du dépôt principal : `artifacts/verif-luna-882907c/` : quarante JSON, journaux, mesures par script/passe,
`revue-condensee.txt`, `controles.txt`, `obstacles.txt`, `verification.json`, `coherence.json`, `transactions.json`
et scripts de lancement/relecture. Détail des incidents dans `constats.md`.
