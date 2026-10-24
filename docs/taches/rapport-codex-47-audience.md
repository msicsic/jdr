# Lot 47 — Une seule décision d'audience

Branche `codex-audience`, **non fusionnée**, base `60da18c`, brief `d22190d`.
24 octobre 2026. Correctif signé SSH `2100c41`, signature vérifiée.

## Cause et règle

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
