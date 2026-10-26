# Lot 142 — Une déclaration candidate ne lie pas la correction

Branche `codex-correction-parole`, non fusionnée ; base `4725388`.
Aucune clé Git de signature configurée. Fichiers réservés aux lots 140/143 intacts.

**Cause N9 et invariant.** Le fil `soir-noir` p1 n°2 du lot 141 porte bien
`« Qui est là ? »`. L'interprétation invente « Corvus. Qui es-tu ? » et déclare
`nom=true`. Le moteur conserve les mots imposés ; la préparation refuse donc
le contenu `nom` (« Corvus ne se nomme pas dans ce qu'il dit »). Le cumul dans
`MJ._echanger_prepare` transforme malgré tout cette déclaration en obligation.
La correction historique `qui=true` et le secours sont bloqués avant toute
revue : deux appels d'interprétation, zéro revue, aucune parole enregistrée.
Le lot 128 n'a pas créé ce cumul ; le rapport 100 décrivait déjà la conservation
des déclarations non examinées, que le contrat du lot 104 n'avait pas supprimée.

`MJ._verifier_fidelite_parole` contrôle toujours la couverture de la déclaration
sur sa propre proposition. Le type présent dans le contenu refusé par préparation
ne lie pas la correction. L'omission déclarée reste dans `operations_a_examiner`,
distinct des obligations : correction et secours perdent le raccourci aux mots
exacts jusqu'à une revue lisible. Une revue illisible garde cette attente, aussi
pour les déclarations du contenu préparé. Seule une revue lisible confirme les
obligations selon le contrat commun de `couverture_action` :
un type présent dont elle refuse le sens reste candidat ; une omission qu'elle
reconnaît reste exigée pendant la correction et le secours. Aucun prompt,
scénario, vocabulaire ni contrôle de perception modifié.

**Relecture.** La première livraison (`e55e252`) supprimait trop largement les
déclarations non examinées et réécrivait trois tests pour une reconnaissance
préalable : l'achat omis puis abandonné passait sans revue. Régression reconnue
et corrigée, intention des tests de paiement, audience et message technique
rétablie : `propos` déclare l'achat absent, la correction retire la déclaration,
la revue le reconnaît, aucun « Tu dis », paiement ou transfert.

**Preuves console.** Après relecture : **22 tests ciblés verts, cinq fichiers,
24,80 s**, deux processus réduits. Première reprise : un champ `motif` manquant
dans une nouvelle simulation, corrigé ; aucun défaut restant dans les ciblés.
Les deux propositions historiques sont conservées dans `tests/data/n9-lot141.json`
et rejouées après une voix entendue : `qui` exécuté, une seule nouvelle parole,
aucun nom de Corvus établi par le faux contenu. Autre script : déclaration
d'achat erronée ajoutée à une question de faim, refus local puis correction
exécutée. Deux scripts vérifient aussi une omission suspectée mais écartée par
revue sur les mots exacts : une seule parole, aucune obligation automatique.
Revue illisible : nouvelle revue obligatoire avant l'abandon du type ; sans
revue lisible, correction et secours ne prononcent rien.
Achat reconnu par revue, y compris verdict défavorable au faux type : correction
et secours sans achat refusés, aucun paiement ni transfert. Paroles, possessions,
conversation et rendu contrôlés après recharge ; N3 conservé.

**Mesures avant relecture**, non relancées : passe Luna unique sur copies, `soir-noir`, `soir-voix`,
`noms-dialogue`, une exécution en priorité réduite ; références `9a39738` relues
du cache, sans rejeu. `soir-voix` est absent de cette référence (le lot 141 jouait
`soir-appel`) : aucune comparaison historique inventée.
**50 appels, 13 tours MJ, 3,85 appels/tour**, zéro repli, arrêt, erreur technique
ou défaut de recharge. Un refus local d'omission corrigé au dernier tour de
`soir-noir` ; aucun « Tu n'as encore rien dit ». N9 est exécuté en quatre appels,
sans première erreur de typage dans cette passe : la correction historique est
prouvée par le rejeu simulé. Comparaisons par tour, référence p1/p2 → branche :

| Script | Appels/tour | Secondes/tour |
|---|---:|---:|
| soir-noir | 3,80 / 4,60 → 4,20 | 13,82 / 15,16 → 13,77 |
| soir-voix | sans référence → 4,00 | sans référence → 14,82 |
| noms-dialogue | 3,25 / 3,75 → 3,25 | 12,75 / 13,56 → 11,44 |

Suite complète unique : **2 118 tests, 235 fichiers, 1 247,64 s**, deux processus
réduits ; deux échecs MiMo et une erreur dans le test d'audience. Sa première
adaptation masquait la régression signalée ci-dessus ; le contrôle de l'omission
est rétabli et vérifié dans la reprise ciblée. Aucune seconde suite complète ni
nouvelle passe Luna, conformément à la relecture limitée à cette voie.
Les deux échecs MiMo historiques `6 != 5` sont reproduits sur l'archive intacte
de `4725388` : 13 tests, 11,39 s, deux échecs, zéro erreur. Commit non signé,
branche poussée ; aucune fusion de `main`.

**Limites.** La confirmation du sens par revue reste sémantique et faillible.
Une correction aux mots exacts sans opération déclarée, sans contenu opérant et
sans obligation confirmée ni analyse restant à faire conserve le raccourci : ce lot ne garantit
pas la détection de toute opération omise dans une saisie libre. Une revue
illisible ne valide jamais le contenu typé proposé ; elle permet une nouvelle
proposition jugée sur son propre contenu, les obligations confirmées et les
analyses restant à faire.
Pas de conclusion de vitesse sur poste partagé. Bruts :
`artifacts/correction-142/`.
