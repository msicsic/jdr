# Lot 47 — Une seule décision d'audience

Branche `codex-audience`, **non fusionnée**, base `60da18c`, brief `d22190d`.
24 octobre 2026. Correctif signé SSH `2100c41`, signature vérifiée.

## Cause et règle du lot 47 (historique, remplacée par 47 b)

`destinataires` choisissait quelqu'un en face, `preparer_parole` pouvait remplacer
ce choix par `tous` ou `personne`, et la contre-revue jugeait encore cette audience.
Une question collective pouvait donc finir en demande de préciser à qui parler.

La prévision et la préparation utilisent désormais la seule décision de `destinataires` :
nom/vocatif, groupe explicite, échange poursuivi, sinon cantonade à voix haute, même
avec quelqu'un en face. « Lui » sans antécédent et le chuchotement restent individuels,
résolus par le regard ; le chuchotement exige le contact. Les désignations publiques sont lues entières, sans limite arbitraire de quatre mots.
La cible d'une intention non citée « je <verbe> [à] <personne>… » est lue par `analyser` / `_cible_intention`, sans nouvelle
liste de verbes ni transformation automatique d'un geste en parole.

`parole_prevue.personnage` donne une seule adresse. Une proposition contraire est refusée
avec `attendu` avant la revue ; `audience_libre` et `audiences_fideles` disparaissent.
`MJ._verifier_fidelite_parole` et `couverture_action` contrôlent encore les mots et le contenu
sur copie (`contenu_conforme`), avec les conséquences du moteur et les noms publics.
Deux contenus refusés ne demandent plus à qui parler. Répondants, mémoire, rendu et
sauvegarde suivent les chemins communs existants. Contrats d'ouïe et du MJ mis à jour.

## Vérifications et mesures

Six nouveaux tests de chaîne complète avec MJ simulé : le Relais réel (Aubin en face,
trois présents et une voix), une question différente à l'auberge, adresses individuelles
contraires refusées, contenu contraire corrigé, autre parole sans question, restitution
et achat nommés. État, argent, engagement, souvenirs et texte conservé après recharge ;
un geste visant une personne reste un geste. Anciennes scènes individuelles rendues
explicites, sans modifier les règles d'échange, les scénarios ou les fichiers réservés.

Suite complète **une seule fois**, `tools/tests.py --processus 3`, priorité réduite :
1 733 tests, 16 ignorés, 1 488,9 s ; six échecs et douze erreurs initiaux (anciennes
adresses implicites et désignations tronquées). Après corrections et reprises ciblées :
**166 fichiers validés, 1 734 tests couverts, 16 ignorés**, aucun défaut restant.
Bilan reproductible : `artifacts/consolider-codex-47.py`, traces initiales conservées.

Luna `gpt-6-luna`, copies, coffre principal, `banc_multi`, **une seule passe**.
Référence `main` `42bb9c0` lue du cache, clé vérifiée avec son outil historique.

| Script | Appels/tour main → lot | Tours MJ main → lot |
|---|---:|---:|
| noms-dialogue | 3,00 → 3,00 | 4 → 4 |
| soir-appel | 3,60 → 4,75 | 5 → 4 |
| echanges | 2,75 → 3,67 | 4 → 3 |
| relais | 3,00 → 2,63 | 9 → 8 |

Ensemble : **68 → 63 appels**, 3,09 → 3,32 appels/tour ; 12,6 → 14,2 s/tour,
zéro repli, erreur technique ou recharge invalide. Question du bois, deux scripts :
**quatre appels chacun**, aucun refus d'audience :
`Tu dis : « est-ce que quelqu'un a du bois ? »` ;
Aubin, Brune, Ilse et la voix de l'ouest répondent. Aucun « Précise à qui… » affiché.

## Limites

La passe a révélé les intentions nominales non reconnues : restitution devenue publique,
achat non accepté. Le dernier correctif d'analyse les conserve individuelles ; les
propositions initiales de Luna sont rejouées en tests sur le code final, avec restitution effective et refus individuel
de l’achat par le moteur, sans paiement fictif. Les tests de transfert réel restent verts. **Les mesures ci-dessus précèdent ce dernier correctif** ;
pas de seconde passe Luna, conformément au brief. Elles ne mesurent donc pas son gain.
La grammaire reste bornée aux formes décrites : intentions indirectes ou complexes non
résolues, choix de parler et sens du contenu encore sémantiques. Les temps de cache et
une seule passe ne permettent pas d'attribuer une variation de coût au seul lot.

Bruts : `artifacts/codex-47-*`, `artifacts/analyser-codex-47.py`,
`artifacts/bancs-multi/20261024-195146-56088/`. Aucun banc long ni seconde suite complète.
`main` non touchée ; livraison sur cette branche, sans fusion.


## 47 b — Celui d’en face redevient le défaut

Décision de l’utilisateur du 24 octobre 2026 ; base `e28df5c`, brief `d33e492`, même
branche et worktree. La cantonade avec quelqu’un en face, décrite au lot 47 ci-dessus,
est abandonnée. Correctif signé SSH **`f10f9d3`**, signature vérifiée.

**Règle.** `paroles.destinataires` choisit : nom/vocatif, groupe explicite, échange
poursuivi, sinon celui d’en face ; à égalité, le joueur précise. Sans interlocuteur
perçu à portée de voix, la parole à voix haute reste à la cantonade et ses auditeurs
peuvent répondre. Chuchotement et « lui » sans antécédent gardent leurs contraintes.
Prévision et préparation suivent cette décision unique ; une proposition contraire
est refusée avec `attendu` avant revue. Aucun mot-clé collectif, scénario ou cas du bois.
Les contrats d’ouïe et du MJ sont actualisés.

**Tests adaptés, chacun :**

| Fichier | Attentes modifiées |
|---|---|
| `test_audience` | Cas réel → Aubin ; auberge → Lucien ; défaut sans question → Aubin ; refus de contenu → Aubin. |
| `test_luna_noms` | Défaut, correction d’une autre cible et question conservée → Ilse seule ; Aubin témoin. |
| `test_luna_restes` | Sens de ressource et adresse fixée → Ilse ; transfert réel vérifié séparément du dossier sémantique. |

Onze autres fichiers de scènes individuelles retrouvent leur saisie antérieure au
lot 47. Les neuf tests d’audience couvrent aussi « à tous », vocatif, échange poursuivi,
cantonade sans interlocuteur perçu et refus inchangés de « lui » et du chuchotement.
Monde, souvenirs et texte sauvegardé contrôlés après recharge : au Relais, Aubin seul
répond, Brune, Ilse et la voix de l’ouest retiennent ses mots. **234 ciblés**, deux anciens
doubles adaptés puis **14 tests verts**.

**Constat Luna et contrat final.** La revue rejuge encore l’audience sous « contenu
non conforme ». Son dossier est ensuite réduit à `replique`, `contenu`, `sens_contenu`,
sans adresse, auditeur ni effet. Les sens typés décrivent le contenu indépendamment
de son audience. **70 tests ciblés verts** sur ce contrat final, références publiques
et transfert réel après recharge compris.

**Une passe Luna**, copies et coffre principal ; `main` `42bb9c0` lu du cache, clé
vérifiée avec son outil historique, aucun rejeu ni comparaison de temps au cache.

| Script | Appels/tour main → 47 b | Tours MJ main → 47 b |
|---|---:|---:|
| noms-dialogue | 3,00 → 3,50 | 4 → 4 |
| soir-appel | 3,60 → 4,25 | 5 → 4 |
| echanges | 2,75 → 3,67 | 4 → 3 |
| relais | 3,00 → 2,75 | 9 → 8 |

**68 → 64 appels**, 22 → 19 tours MJ, 3,09 → 3,37 appels/tour. Zéro repli, erreur technique
ou recharge invalide. Question du bois : `noms-dialogue`, **six appels**, un faux refus
puis `Tu dis à Aubin : « est-ce que quelqu'un a du bois ? »` ; Aubin seul répond :
« Oui. Les planches de bac sont là, à deux mètres vers le sud et un mètre vers l’est.
Elles sont à moi. » Destinataires et répondants `[aubin]`, témoins perçus `[brune, ilse]`.
`soir-appel`, **quatre appels**, deux refus de contenu puis « Précise ce que tu veux dire :
les mots ou le contenu proposés ne correspondent pas à ta demande. » Rien n’est dit.
Aucun « Précise à qui… » dans les quatre parties.

**Suite :** campagne complète unique, interrompue par le plantage du PC. Résultats
récupérés : **71 fichiers, 892 tests verts**. Reprise des seuls **95 fichiers sans résultat**,
trois processus à priorité réduite : **845 tests verts en 79,8 s**. Bilan consolidé avec
les vérifications du contrat final : **166 fichiers validés, 1 737 tests, 16 ignorés**,
aucun échec ni erreur. Aucune seconde suite complète. Résultats d’avant interruption,
reprise et provenance par fichier : `artifacts/codex-47b-suite-*.json` ; consolidation
reproductible par `artifacts/consolider-codex-47b.py`.

**Limites :** cette passe précède la réduction finale du dossier, validée en simulation ;
pas de seconde passe Luna. On ne conclut ni à la disparition des faux refus sémantiques,
ni à un gain de coût final. Reconnaissance grammaticale bornée ; aucune extension de groupe.
Bruts : `artifacts/codex-47b-*`, `artifacts/analyser-codex-47b.py`,
`artifacts/bancs-multi/20261024-203012-58008/`. `main` et les scénarios non modifiés.
