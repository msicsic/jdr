# Lot 292 — G4 : résultat public du moteur

2026-10-29. Branche `codex-g4-resultat-public`, base `9e52df4`.
**Non fusionnée ; clôture avec une assertion de monde encore rouge.**

`jeu.conclure` mémorise et sauvegarde le rendu moteur avant affichage,
sans récit ni audit après exécution ; même boucle console/TUI/web.
Propositions, contre-revues et confirmations conservées. Blessures visibles
et dépôts au sol rendus par le moteur ; aucune mécanique PNJ modifiée.
`raconter`, `demande_initiale`, `--recit-moteur` supprimés.
`MJ.raconter_resultat` reste pour les outils explicites et le comparateur,
sans appel par le jeu ; petits pas silencieux conservés.

**Correction demandée à la clôture :** le test TUI original reste **inchangé**.
G4 ne change pas les informations de jet déjà montrées au joueur.
`rendre_resultat` masque le calcul et les valeurs, conserve une phrase
« La tentative réussit/échoue. » ; le journal garde le calcul. Les valeurs
ajoutées aux coups/prises sont retirées. Les nouveaux tests G4 contrôlent
l’issue et les conséquences ; les commandes locales gardent leur affichage.

**Tests.** Première passe : **362 tests / 25 fichiers, 2 échecs, 0 erreur,
851,350 s**, un travailleur réduit. Attribution par rejeux isolés :

- TUI `test_manoeuvre_composee_et_recit_echec_partiel` : **vert sur `9e52df4`**,
  donc régression G4, corrigée dans le code sans changer ce test.
- Prise réussie : le nouveau test n’existe pas sur la base ; sa scène console
  et son assertion ont été reproduites sur `9e52df4`, puis la branche.
  **Même échec** : Brune est saisie puis réussit `defense.degager` durant les
  deux secondes du geste, `tenu_par=joueur` disparaît. L’assertion de prise
  persistante reste inchangée et rouge. Le dégagement du PNJ n’a pas de
  phrase publique : **limite préexistante, complétude générale non garantie**.

Reprise finale des seuls fichiers concernés : **35 tests, 34 succès, un échec
conservé, 0 erreur, 305,990 s** ; **TUI originale 28/28 verte**. Bilan retenu
sur les 25 fichiers : **361 succès / 362 tests**, un échec sur ce comportement
préexistant, sans le masquer par un changement d’attente de monde.
Dix comparaisons au moteur exact de la base : **10/10** états mécaniques,
scènes, fiches et cartes identiques après recharge, textes du journal exclus.
Ni suite complète ni banc PNJ supplémentaire.

**Luna : une passe**, trois scripts sur copies, `integ=9e52df4` → `lot=.`
sur `d1e50c4`, un travailleur réduit ; référence absente jouée puis rangée
une fois. Aucun incident. **Trois résultats exacts, sauvegardés et affichés,
effets mécaniques identiques à la référence** :

| Résultat | Monde rechargé | Après exécution, référence → lot |
|---|---|---:|
| Assommer, tour 2 : coup réussi, 1 PV, effondrement | Gorm inconscient, blessure de 1 PV | 1 récit + 1 audit → 0 |
| Ligoter, tour 2 : personne maintenant ligotée | Brune liée par `corde_rixe`, corde en entrave sur elle | 1 récit + 1 audit → 0 |
| Poser, tour 1 : torche au sol, à tes pieds | Salle et case du joueur | 1 récit + 1 audit → 0 |

Après correction du rendu : **ces trois plans admis rejoués sans modèle**,
mêmes effets, texte corrigé exact/sauvegardé, valeurs masquées. Aucune seconde
passe Luna ; boucle d’appels inchangée.

Mesures : **12 → 7 appels**, **28,65 → 22,20 s** ; sur huit saisies hors
quitter : **1,50 → 0,875 appel/saisie**, **3,58 → 2,78 s**. Le résumé par
tour avec appels donne 2,40 → 2,33 appels et 5,73 → 7,40 s, dénominateur
cinq → trois tours. **Régression avant ligature** : `impossible` corrigé
dans la même saisie, refus **0 → 1**, compilation/revue **2 → 3 appels**,
**6,35 → 8,99 s**. Replis et relances narratives **0 → 0** ; aucune après
exécution. Pas d’attribution causale des durées avec une seule passe.

Bruts, six parties/fils, états/vues, mesures, reproductions, tests et
manifeste : `C:/Users/msics/donjon/artifacts/g4-292/`. Fins initiales conservées ;
`fin-cloture.json` expose le bilan final et l’échec résiduel. Aucun calcul actif.
