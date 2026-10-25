# Lot 89 — Fidélité du contenu et décision d'audience

25 octobre 2026 — `codex-fidelite-audience`, **non fusionnée**, base `96c6396`.
**Validation partielle ; objectif global d'appels non atteint.** Aucun changement
de `main`, des scénarios, de l'audience ou du modèle `gpt-6-luna`.

**Mesure préalable.** Toutes les contre-revues des quarante parties 882907c
(lot 79), trois parties du lot 82 et deux du lot 84 : **16 + 14 + 10 revues de
parole**. Cinq refus, tous injustifiés selon le contrat moteur :

| Lot/script | Nombre | Motif de la revue et erreur |
|---|---|---|
| 82, soir-appel/noms-dialogue | 2/1 | « quelqu'un » porte sur l'ensemble, `ressource` sur l'interlocuteur : rejugement d'audience |
| 84, soir-appel | 1 | `demande` avec valeur 3 ne représente pas explicitement l'échange : forme pourtant exécutable |
| 84, ressources | 1 | La question de dette devient réclamation : conséquence admise par le moteur |

Aucun refus justifié de parole dans ce corpus ; le refus de geste sous obstacle
du lot 79 est exclu. Motifs exacts et sources : `artifacts/refus-historiques.json`.

**Contrat corrigé.** `MJ._auditer_action` sépare parole et gestes. Le rapport
obligatoire porte `perimetre` : seul `sens` peut refuser ; `adresse` et
`validation_moteur` ne relancent pas le MJ. `couverture_action.verifier` exige
toujours les opérations demandées, même hors périmètre. `sens_parole` fournit
les opérations exécutables communes et le prix calculé par `offre` : la revue
compare le sens, sans redécider la représentation. Après le défaut Luna ci-dessous,
`paroles.SENS_CONTENU.reclamer` est aligné sur le contrat existant : interroger
sur son dû ou le réclamer ; le moteur décide du règlement. Cette clarification
est mesurée sur `8c47cc7` dans la section « Seconde mesure » ci-dessous.

**Tests.** Quatre nouveaux tests de vraie console : bois/Aubin et nourriture/Lucien
au premier contrôle malgré une objection d'adresse ; achats de parts sous demande
chiffrée et proposition, paiement/livraison ; questions de dette à Aubin/Gorm ;
mots contraires et autre ressource refusés, opération manquante toujours bloquée.
État, parole unique, sortie, conversation et inventaire après recharge contrôlés.
**71 tests ciblés consolidés verts**, après correction d'une scène de dette.
Suite complète unique : **1 931 tests, 16 ignorés**, 199 fichiers, trois processus,
**1 444,24 s** ; huit échecs d'attentes de dossier dans deux anciens fichiers et
une erreur Windows de remplacement de sauvegarde temporaire dans le test TUI.
Attentes adaptées ; reprise finale des deux fichiers, du seul test TUI en erreur
(inchangé) et des quatre nouveaux tests : **15 tests verts, 56,40 s**.
**Bilan consolidé sans défaut restant reproduit**, sans seconde suite complète.

**Luna, une passe**, ChatGPT medium/libre, copies, priorité réduite, une exécution ;
quatre références 882907c exclusivement en cache : **53 → 57 appels / 14 tours**,
**3,79 → 4,07 appels/tour** ; relances **4 → 2** (0,29 → 0,14/tour), refus **0 → 2**,
replis du détecteur **0 → 2**, un tour avec erreur réseau, aucun arrêt/défaut de recharge.

| Script | Appels/tour, référence → lot | Relances |
|---|---|---|
| soir-appel | 4,25 → 4,25 | 1 → 2 |
| noms-dialogue | 4,00 → 3,50 | 2 → 0 |
| ressources | 3,67 → 4,33 | 1 → 0 |
| echanges | 3,00 → 4,33 | 0 → 0 |

Le bois passe au premier audit dans les deux scripts et Aubin répond sur ses
planches. L'achat du soir subit un délai de **203,4 s avant proposition** : aucun
achat exécuté. Le remboursement finit sur le rendu moteur après deux relances.
La question de dette reste bloquée : `qui` extrait à tort, correction puis repli
incomplets. Définition commune ensuite clarifiée, sans rejouer Luna. `echanges` :
champ interdit de `propos` refusé avant revue puis corrigé ; trois alertes lexicales
du harnais sont les noms saisis repris par des refus locaux, sans fuite narrative.

**Limites.** Périmètre appliqué déterministement, classement et opérations encore
sémantiques : faux refus classé `sens` et écart classé hors périmètre restent
possibles. L'invariant général n'est pas garanti. Temps historiques sous d'autres
charges, aucun gain causal revendiqué. Bruts du worktree : `artifacts/verification-luna-lot89.json`,
`bancs-multi/20261025-210728-32172/`, `tests-cibles*` et `tests-complets.{log,json}`.

## Seconde mesure

25 octobre 2026 — **Deux passes des quatre scripts sur le commit signé `8c47cc7`**,
ChatGPT medium/libre, copies temporaires, deux exécutions parallèles à priorité réduite.
Les huit parties de **882907c sont exclusivement relues du cache** ; huit parties
de `8c47cc7` jouées et rangées. **Aucune erreur technique, aucun arrêt ni défaut
de recharge.** Moyennes par script sur ses deux passes ; chaque cellule donne
**882907c → 8c47cc7**. Refus : validations moteur/contre-revue ; relances : narratives.

| Script | Appels/tour | Relances | Refus | Replis du harnais |
|---|---|---|---|---|
| soir-appel | 4,25 → 5,25 | 1 → 2,5 | 0 → 0 | 0 → 0 |
| noms-dialogue | 3,75 → 4,125 | 1,5 → 0,5 | 0 → 1 | 0 → 0 |
| ressources | 3,67 → 4,33 | 1 → 0,5 | 0 → 0 | 0 → 0 |
| echanges | 3,00 → 4,00 | 0 → 0 | 0 → 0 | 0 → 0 |

Ensemble : **104 → 125 appels / 28 tours MJ**, **3,71 → 4,46 appels/tour** ;
moyennes par passe : relances **3,5 → 3,5**, refus **0 → 1**, replis **0 → 0**.
L'objectif global de réduction des appels reste **non atteint** ; les secondes
des références sont historiques, sans conclusion causale sur la latence.

**Causes, effets et comparaison des sorties.**

- **Deux refus et deux demandes non exécutées**, un par passe, `noms-dialogue`
  n° 3 : « Ilse, tu m'entends ? ». La revue extrait `qui` alors qu'elle déclare
  les mots conformes ; le moteur exige cette opération absente. La correction
  propose `qui`, justement jugé contraire à la question d'audition ; l'extraction
  initiale conservée bloque ensuite le repli littéral. Les deux références
  prononcent la question et Ilse répond. **Régression reproduite**, même si le
  détecteur historique de replis ne compte pas « Ta demande n'a pas été exécutée ».
  Aucun autre refus de validation dans les huit parties.
- **Question de dette**, `ressources` n° 2 : `reclamer` correctement extrait aux
  deux passes, sans `qui`, sans refus ni repli ; « Non. Je ne te dois aucune pièce. »
  puis « Aubin, vieux passeur ne te doit aucune pièce. » s'affichent. Le second
  passage demande une relance narrative de compte, sans échec du tour.
- **Champ interdit de `propos`**, `echanges`, question du gardien : **non reproduit
  aux deux passes**, question dite et réponse reçue sans refus ni correction.
  Les cinq refus locaux de désignation (n° 4 à 8, noms Brune/Aubin/Ilse inconnus)
  sont identiques, texte pour texte, aux deux références : zéro appel Luna,
  aucune régression. Les alertes lexicales correspondantes reprennent les noms
  saisis ; elles ne constituent pas des fuites narratives.
- **Achats du soir exécutés aux deux passes** : or **26 → 23**, `planches_1`
  portée après déplacement et recharge. Une proposition explicite et une demande
  historique chiffrée sont acceptées au premier contrôle. Les relances du soir
  portent sur les comptes narrés : offre inventée ou dette inversée à la question
  du bois, désignation de la part livrable refusée sémantiquement, offre et solde
  de livraison confondus ou omis.
  Elles aboutissent à une narration, sans repli ni nouvelle transaction. La
  première narration d'achat admise cite toutefois `planches_1` et emploie
  « rendues » pour les pièces payées ; qualité de prose non améliorée par ce lot.

**Correction de la régression dans le contrat commun.** L'analyse choisissait des
codes dans une liste dont les sens étaient regroupés en description. Elle
évalue maintenant **chaque opération séparément**, par un booléen obligatoire
portant sa propre définition de `SENS_CONTENU` dans le schéma. Tous peuvent être
faux ; aucun mot ni type n'est exempté. Le contrôle structurel refuse les cartes
incomplètes ou mal typées avant accumulation ; les opérations reconnues restent
exigées sur les corrections. Le périmètre de fidélité et les effets moteur ne
changent pas. Le classement du sens demeure sémantique, donc sans garantie
générale contre toute extraction erronée.

Un nouveau test de console/recharge couvre le cas d'Ilse et une autre question
ordinaire à Aubin, chacun avec une analyse lisible puis une analyse mal typée
relue sans correction du contenu : paroles, destinataires, conversation, sortie
et or après recharge. **77 tests ciblés verts, six fichiers, deux processus à
priorité réduite, 53,93 s** ; couverture des achats manquants et conservation des
opérations également revérifiées. Pas de seconde suite complète. Une erreur de
délimiteur corrigée avait empêché l'import des premiers tests et d'une tentative
de banc ; cette tentative n'a fait **aucun appel Luna**.

**Reprise de `noms-dialogue` après correction : deux passes**, mêmes références
en cache : **14 appels sur quatre tours chacune**, soit **3,50 appels/tour**,
**zéro relance, refus, repli, erreur technique ou défaut de recharge**. « Ilse,
tu m'entends ? » est prononcée au premier contrôle avec toutes les opérations
fausses ; Ilse répond « Oui, je t'entends », et la sauvegarde rechargée conserve
le tour. Bois à Aubin et passage demandé à Brune restent correctement typés.
Lors de cette reprise, les trois autres scripts ne sont pas rejoués : leurs
chiffres ci-dessus restent ceux de `8c47cc7`, pas une moyenne artificielle sur
deux versions du code. Aucun autre changement de code.

Bruts : `artifacts/bancs-multi/20261025-214008-41452/` (mesure de `8c47cc7`),
`20261025-214903-31636/` (reprise corrigée), `seconde-mesure-analyse.{json,txt}`,
`reprise-noms-dialogue-analyse.json` et `tests-seconde-mesure.{log,json}`.

## Base d'intégration

25 octobre 2026 — Comparaison demandée **96c6396 → c57b1d3**, deux passes
des quatre scripts sur chaque commit, ChatGPT medium/libre, quatre exécutions
au maximum, priorité réduite, copies temporaires. **Seize parties jouées et
rangées en cache** ; les huit parties de 882907c sont uniquement relues.
Empreintes SHA-256 des **24 parties** vérifiées contre leur copie en cache.
Aucun arrêt, erreur technique ou défaut de recharge. **Aucun changement de code
pour ce complément**, aucune nouvelle suite de tests.

**Conclusion sur le coût du lot 89.** `c57b1d3` n'ajoute **aucun appel
systématique** par rapport à sa base `96c6396`. Ensemble : **122 → 120 appels
sur 28 tours MJ**, soit **4,36 → 4,29 appels/tour**. Par passe, moyennes : refus
**4,5 → 0,5**, relances narratives **1 → 2,5**, replis du détecteur **0 → 0,5**.
Les fonctions totalisent **60 → 60** `repondre_au_joueur`, **25 → 33**
`auditer_narration`, **37 → 27** `auditer_action`, **0 → 0** `auditer_portee`.
Deux passes ne démontrent pas un gain général de temps ; les secondes mesurées
ici sont **16,7 → 17,6 s/tour**, malgré les deux appels économisés. La comparaison
avec 882907c seule n'isolait pas le lot 89.

### Décomposition par fonction

Moyennes des deux passes, **appels par tour MJ du script** (4 tours dans
soir-appel/noms-dialogue, 3 dans ressources/echanges). R = `repondre_au_joueur`
(interprétation, récit et corrections), N = `auditer_narration`, F =
`auditer_action` (ici fidélité de parole), P = `auditer_portee`. Toutes les
fonctions sont comptées : **aucun autre appel** ; arrondi à trois décimales.

| Script | Commit | R | N | F | P | Total |
|---|---|---|---|---|---|---|
| soir-appel | 882907c | 2,25 | 1,25 | 0,75 | 0 | 4,25 |
| soir-appel | 96c6396 | 2,25 | 1 | 1,375 | 0 | 4,625 |
| soir-appel | c57b1d3 | 2,375 | 1,25 | 1,125 | 0 | 4,75 |
| noms-dialogue | 882907c | 2,125 | 1,375 | 0,25 | 0 | 3,75 |
| noms-dialogue | 96c6396 | 1,75 | 0,75 | 1,25 | 0 | 3,75 |
| noms-dialogue | c57b1d3 | 1,75 | 1 | 0,75 | 0 | 3,5 |
| ressources | 882907c | 2,333 | 1,333 | 0 | 0 | 3,667 |
| ressources | 96c6396 | 2,333 | 1 | 1,5 | 0 | 4,833 |
| ressources | c57b1d3 | 2,5 | 1,5 | 1 | 0 | 5 |
| echanges | 882907c | 2 | 1 | 0 | 0 | 3 |
| echanges | 96c6396 | 2,333 | 0,833 | 1,167 | 0 | 4,333 |
| echanges | c57b1d3 | 2 | 1 | 1 | 0 | 4 |

**Quel lot a ajouté l'appel ?** Le commit du **lot 82, `3510d00`**, supprime
dans `_verifier_fidelite_parole` les retours anticipés pour adresse explicite,
et pour mots identiques sans contenu typé. Une parole valide au premier essai
passe désormais par **R interprétation + F fidélité + R récit + N narration**,
soit quatre appels, aussi bien sur `96c6396` que sur `c57b1d3`.

- `echanges` : salutation, question du gardien et avertissement à tous passaient
  sans F sur 882907c ; **+1 F par tour de parole vient du lot 82**, non du 89.
  Le passage sans incident de la base et les deux passages finaux ont exactement
  R=2, N=1, F=1 par tour. Les cinq commandes locales refusées pour noms inconnus
  n'appellent aucun modèle et restent hors du dénominateur MJ.
- `ressources` : les trois paroles étaient également exemptées de F. Leur coût
  sans incident passe donc de trois à quatre appels dès le lot 82. Les valeurs
  supérieures à quatre viennent des corrections ou des relances narratives.
- `noms-dialogue` : Brune n° 2 et Ilse n° 3 deviennent contrôlées par F au lot 82 ;
  le bois n° 1 l'était déjà. L'ambiance n° 4 reste **R + N**, sans F ni P. Ainsi,
  le script final sans incident coûte **3 × 4 + 2 = 14 appels**, soit 3,50/tour.
- `soir-appel` : dans les deux références 882907c, seule la question à Ilse
  n° 3 saute F ; les trois autres paroles sont déjà revues. Le plancher devient
  quatre appels pour chaque parole au lot 82 ; les écarts supplémentaires des
  tableaux sont des corrections, audits relus ou récits révisés.

Le **lot 83** (`b2be935`, `be8e175`) renforce la cohérence et la résolution des
comptes audités : un rapport illisible peut nécessiter une relecture N, sans
nouvel appel normal. Le **lot 84** (`7578a56`) change la remise des parts, sans
ajouter de fonction Luna. Le **lot 89** change le contrat et le dossier de F,
mais ni ses points d'appel ni sa boucle de reprise, déjà présents dans la base.

**Pourquoi ne pas retirer F aux paroles apparemment vides ?** Une réplique exacte
avec `propos` peut avoir perdu une opération demandée : cela ne certifie pas
qu'il n'y a rien à contrôler. C'est précisément observé ici dans `soir-appel`,
passe finale 2 : le MJ propose d'abord `propos` pour payer une planche ; F détecte
`proposition` manquante. Supprimer F sur ce critère réintroduirait la perte de
paiement corrigée au lot 82 et couverte par `test_paiement_effectif`. Ce raccourci
retirerait donc un contrôle utile du lot 82. Le lot 89 n'ajoutant pas d'appel
normal, conformément à la demande, aucun code n'est modifié pour ce complément.

### Effets et limites observés avec la bonne base

La base laisse **cinq tours MJ non exécutés** en passe 1 : bois dans soir-appel
et noms-dialogue, audition d'Ilse, question de dette et question du gardien.
Leurs récits absents économisent N sans constituer une réponse réussie.
Sur `c57b1d3`, **aucun de ces tours n'est abandonné**. Cela explique une partie
des N supplémentaires, en plus des relances narratives.

**Attribution rectifiée :** l'extraction de `qui` pour « Ilse, tu m'entends ? »
est également présente sur `96c6396`, qui bloque le tour en passe 1. Le défaut
constaté dans « Seconde mesure » n'était donc pas attribuable au lot 89 sur la
seule comparaison à 882907c. Le renforcement commun de `c57b1d3` l'évite dans
les deux nouvelles passes ; aucune nouvelle garantie générale de classification.

Le **seul refus de validation final** est le `propos` omettant l'achat, décrit
ci-dessus ; la correction aboutit à une transaction. Le **seul repli narratif
final**, `ressources` passe 2 n° 2, vient de trois récits qui ajoutent ou substituent
le compte inverse (« tu ne me dois rien ») au résultat « Aubin ne te doit aucune
pièce ». Le garde des comptes les refuse ; le joueur lit finalement l'issue
moteur exacte. Le tour est prononcé, sauvegardé et résolu : ce n'est ni un appel
de fidélité supplémentaire ni une question de dette bloquée.

**Limite matérielle et narrative restante :** dans l'achat final de la passe 2,
la correction propose `demande: {type: objet, objet: planches}` au lieu d'une
part. La revue l'admet ; l'inventaire rechargé contient **`planches` (lot entier)**,
contre `planches_1` dans l'autre passe finale et les deux passes de la base.
Le récit admis annonce en outre « Il te rend les trois pièces immédiatement »,
alors que les comptes fournis portent un paiement joueur → Aubin et l'or vaut
**23**. Ce sont des défauts sémantiques de fidélité et d'audit, non un appel
systématique ajouté. Ils restent **non corrigés dans ce complément consacré
à l'attribution des appels** ; ce rapport ne valide pas l'invariant général du
sens des quantités ni celui de toute affirmation affichée.

Bruts et preuves : `artifacts/bancs-multi/20261025-215328-39640/`,
`base-integration-analyse.{json,txt}`, `base-integration-verification.txt`,
`verification-cache-base-integration.json`. Les compteurs sont contrôlés contre
la liste des fonctions de chaque tour et leur somme égale exactement les appels.
