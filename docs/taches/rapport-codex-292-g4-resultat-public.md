# Lot 292 — G4 : résultat public du moteur

2026-10-29. Branche `codex-g4-resultat-public`, base intégration `9e52df4`.
Code `d1e50c4` poussé sur origin. **Non fusionnée ; vérifications en cours.**

`jeu.conclure` enregistre le résultat public dans la conversation et sauvegarde
avant affichage. Il ne demande plus de récit ni d’audit après exécution.
La proposition et sa contre-revue, la fiche tenter/annuler, les contrôles
d’admission et les dialogues restent inchangés. TUI (`SeuilApp.boucle_jeu`)
et web (`lancer_web` / `PontWeb`) utilisent cette même boucle et ce même
`conclure` pour les propositions du MJ, immédiates ou confirmées. Les commandes
locales avaient déjà leur rendu et leur sauvegarde sans modèle ; leur silence
sur les petits pas reste conservé (G7 hors périmètre).

`narration.rendre_resultat` conserve maintenant les jets et leurs issues.
Le rendu commun des effets dans `Moteur._appliquer_effet` complète les coups du
joueur par son jet et, si la cible est visible, la perte de PV infligée ;
la prise affiche son jet réellement enregistré. Aucune caractéristique adverse
supplémentaire n’est publiée par ces ajouts. Les dépôts réutilisent le repère
commun `SOL_AUX_PIEDS`. Blessure, inconscience, issue de ligature/traînage,
transfert et allumage sont des phrases moteur, sauvegardées avec le résultat.
Aucune mécanique PNJ n’est modifiée, aucune consigne Luna ajoutée.

`raconter` et `demande_initiale` sont supprimés, comme `--recit-moteur` :
ce rendu est désormais le défaut unique du jeu. `MJ.raconter_resultat` et
la voie du comparateur restent pour leurs appelants explicites :
`tools/test_operations_reel.py`, `tools/valider_mimo_parties.py` et les tests
unitaires de narration/admission. Ils ne sont plus appelés par la boucle.
Les audits des voies non portées sont conservés.

**Vérifications déterministes.** Dix scènes sur copies comparées au moteur
exact de `9e52df4` : assommer, autre coup blessant et coup manqué, ligoter,
traîner, prise réussie/manquée, poser/prendre/allumer. État mécanique complet
identique après recharge (seul le texte du journal est exclu), fiche, carte
et scène identiques **10/10**. Le nouveau contrat console avec MJ simulé
vérifie les trois scènes réelles et leurs autres cas, la confirmation,
le geste immédiat, le succès/l’échec, l’absence d’appel après tenter et la
présence sur disque du texte avant affichage. Les anciennes attentes de
`test_recit_resultat` fondées sur un récit Luna/repli sont remplacées par ces
attentes moteur ; les autres fichiers retirent seulement l’option devenue
inutile ou transforment un récit simulé en interdiction d’appel.
Tests ciblés : 25 fichiers, un travailleur réduit ; résultats à reprendre dans
`fin-tests.json` / `tests-g4.json`, archivés automatiquement à la fin du processus.
Ni suite complète ni banc PNJ : aucun changement de décision mécanique.

**Luna.** Une seule passe, trois scripts `force-4b-assommer`,
`force-4f-ligoter`, `poser-sol-relais`, `integ=9e52df4` et `lot=.`, un
travailleur réduit, copies et coffre principal. Référence lue du cache ou
jouée une seule fois si absente. L’observateur archive les résultats bruts,
le monde et les vues rechargés ; l’analyse compte les appels suivant chaque
exécution, vérifie le texte exact sauvegardé et affiché, expose les refus
par cause et sépare les incidents de référence du contrôle de l’invariant.
Aucun gain de délai annoncé avant lecture des mesures ; une passe reste
insuffisante pour attribuer causalement les écarts de temps.

Bruts, scripts et empreintes : `C:/Users/msics/donjon/artifacts/g4-292/`.
Démarrage vérifié : premiers fichiers de partie produits (`demarrage-verifie.json`).
Fichier de reprise écrit en dernier même en cas d’erreur : `fin-luna.json`.
Le lot reste ouvert jusqu’à lecture et analyse de cette passe. La complétude
est éprouvée sur les familles ciblées ; les déplacements cumulés et les paroles
typées restent leurs lots dédiés, sans retrait de leurs contrôles transitoires.
