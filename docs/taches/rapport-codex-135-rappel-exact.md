# Lot 135 — Mots historiques et rappel exact

Branche `codex-rappel-exact`, non fusionnée ; base `d509da1` (lot 132 voulu).

**Cause établie dans le fil 057766f, soir-noir p1, saisie 5.**
`echanges_passes.voix_1` contient bien « Je m’appelle Ilse. Et toi, qui es-tu ? ».
Mais `paroles_entendues` contient « Je m’appelle une voix qui se dit Ilse.
Et toi, qui es-tu ? » et `presentation` est aussi projetée. Le motif de l’audit
reprend cette seconde version. Il ne s’agit donc pas seulement d’une confusion
sans source : la projection fournit deux historiques contradictoires.
Extraction exacte dans `artifacts/rappel-135/cause{,-projection}.json`.

**Contrat commun.** `noms.public` conserve `texte` et `presentation` des événements
de parole entendus par Corvus, et les textes du dossier public `echanges_passes` ;
les références des locuteurs et les autres descriptions restent projetées.
Une parole privée ne bénéficie pas de cette protection. `narration.echanges_passes`
fournit pour chaque parole un `rappel_exact` historique, construit par le moteur
avec la désignation publique et les mots enregistrés. `textes_etablis` et
`segments_etablis` lui donnent la preuve locale du lot 95, sans audit ni création
d’une nouvelle parole. Le garde nominal protège uniquement la citation historique autonome ou celle dont
l’attribution entière est ainsi prouvée ; les mots doivent aussi avoir été entendus.
`consigner` reconstruit la preuve depuis le monde avant sauvegarde. Aucun lexique
de formulations du MJ, nouveau mode, scénario ou consigne supplémentaire à Luna.

**Tests.** Console/MJ simulé sur le cas réel Ilse dans le noir et une autre parole
d’Aubin au refuge : exact admis sans audit, déformé refusé puis exact affiché,
conversation, paroles et monde rechargés ; la citation fausse « La lune est verte »
reste seulement une parole entendue. Nom jamais entendu projeté, parole privée
protégée contre la fuite, preuve historique retirée refusée avant sauvegarde.
15 tests ciblés finaux verts (5,63 s), dont six nouveaux tests.
Les premières erreurs de préparation des nouveaux tests ont été corrigées ;
les permissions Windows des copies temporaires ont nécessité une exécution élevée.

**Luna, passe finale.** ChatGPT `gpt-6-luna`, medium/libre, une exécution réduite,
copies et coffre principal ; 13 tours MJ, 52 appels, zéro repli/erreur de recharge.
Les versions `paroles_entendues` et `echanges_passes` sont cohérentes dans les audits
finaux relus. Références 057766f uniquement lues dans les bruts du lot 123.

| Script | Appels/tour référence p1 / p2 → lot | s/tour lot |
|---|---:|---:|
| soir-noir | 5,40 / 4,60 → 4,20 | 15,00 |
| soir-voix | référence absente des bruts → 4,00 | 14,76 |
| noms-dialogue | 3,75 / 3,75 → 3,75 | 17,11 |

Le N7 historique du tour 5 n’est pas observé ; toutefois ce tour répond par un
refus actuel de se nommer, sans exercer le rappel. **Critère sémantique seulement
partiel** : au tour 2, l’auditeur rejette encore à tort un rappel extrait de
« Tu es dans le noir, toi aussi ? », qui figurait dans une parole plus longue.
La preuve a ensuite été étendue aux phrases entières du découpage commun (jamais
aux sous-textes arbitraires) : ce passage archivé est maintenant admis localement
sans obstacle, sans nouvel appel Luna (`reprise-fragment.json`), et deux scènes
console rechargées exercent la reprise d’une phrase seule. Le même tour
refuse « On m’appelle Ilse » comme présentation non identique à la décision moteur.
Un autre obstacle concerne l’ambiance dans noms-dialogue. Aucune fuite de nom
observée, ni faux nom historique réécrit dans les paroles projetées contrôlées.
Les formulations libres ne sont donc pas déclarées corrigées universellement.

**Écart de vérification.** Un premier lancement prématuré a joué soir-noir et
soir-voix avant la découverte de la projection résiduelle de `paroles_entendues`,
puis a été interrompu pendant noms-dialogue. Une seule passe finale a suivi la
correction de cause. Ce lancement supplémentaire dépasse la passe unique prévue ;
il est conservé, non utilisé comme référence. Aucun troisième lancement.
Le contrôle ciblé final (5,63 s) a chevauché la suite : dépassement bref de la
limite de deux processus de calcul, déclaré ici.
La restriction finale aux paroles entendues par Corvus, ajoutée pendant la passe,
ne change pas les citations publiques de ces scripts ; elle est exercée en test.
Bruts initiaux/finals : `artifacts/bancs-multi/20261026-211700-35304/` et
`20261026-212028-36800/` ; mesures `artifacts/rappel-135/mesures-finales.json`.
Poste partagé et références historiques : pas de conclusion causale de latence.

**Suite complète unique : 2 081 tests, 229 fichiers, 1 101,71 s**, deux processus
réduits ; **deux échecs MiMo historiques `6 != 5`, zéro erreur** :
`test_fournisseurs_jeu.test_mimo_correction_avant_action_sur_deux_scenes` (atelier)
et `test_restes_fusions.test_mimo_rejets_et_actions_sur_deux_scenes_apres_reprise`.
Mêmes assertions que sur la base du lot 132 ; référence non relancée. Aucun autre
échec, aucune seconde suite. La suite avait déjà exécuté les cinq premiers tests
nouveaux avant l’extension aux phrases ; les **15 ciblés finaux**, dont le sixième
nouveau test, vérifient le code final. Bruts `artifacts/rappel-135/suite.{json,log}`.
Bilan global non entièrement vert.

**Limites.** La preuve est déterministe pour la reprise entière du rendu historique
fourni par le moteur et les phrases entières du découpage commun. Une formulation libre comme « Je te l’ai déjà dit… », un
sous-texte arbitraire, une attribution libre et un geste passé restent sémantiques.
La correction de la source contradictoire ne garantit pas leur jugement universel.
Le rappel exact ne prouve ni la vérité de la parole ni l’identité corporelle d’une voix.
Pas de changement des modules réservés aux lots 133 et 136, ni de fusion sur main.
Aucune clé Git de signature configurée : commit non signé.
