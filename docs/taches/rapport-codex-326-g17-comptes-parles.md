# Lot 326 — G17, comptes parlés

Branche `codex-g17-comptes`, **non fusionnée**, base `integration eb15b5e`.
Bruts : `C:/Users/msics/donjon/artifacts/g17-326/`.

**Invariant.** La résolution comptable porte ses rôles, ses termes, son état
et ses effets par opération. `comptes_parles.difference` conserve les effets
même quand le journal cumule plusieurs paiements. `formuler` et
`comptes_narratifs.phrases` fixent les personnes grammaticales depuis les
identifiants débiteur/créancier, sans lire une phrase de Luna. Les comptes
réglés, différés, absents ou refusés et les termes des offres sont distincts.
Les missions proposées, négociées, acceptées ou refusées utilisent la même
admission ; une discussion d'offre ne produit aucun paiement.

**Chaîne.** `paroles.preparer_parole` et `dialogues.preparer_conversation`
admettent les mots dans le registre G15 sur la copie transactionnelle.
Le rejeu de la transaction les enregistre sur le monde à sauvegarder avant
affichage. L'issue publique, le rendu et les citations relisent cette émission.
Le dossier grammatical public est partagé avec le MJ. Le contrôle à
`narration.consigner` vérifie les références d'émission et leurs rendus exacts :
montant, rôle inversé, omission ou doublon ne passent pas la publication.
Le MJ ne rédige ni ne fait auditer les répliques déjà fixées ; un propos libre
résiduel conserve sa rédaction et ses contrôles. Les autres opérations de la
même parole conservent leurs faits moteur.

**Vérification sans réseau.** Console réelle avec fournisseur simulé : Gorm et
Aubin remboursent, Brune refuse, un débiteur sans argent conserve son dû,
un règlement partiel conserve le solde ; achat de planches et autre achat de
part ; offres de mission à vingt et trente pièces ; négociation, acceptation
et refus sans paiement. Contrôle des mots, bourses, dettes, possessions,
livraisons et missions, conversation, fiche et registre après recharge.
Deux créances et deux achats dans une même parole exercent le cumul ; un
propos libre mêlé à une réclamation garde son audit. Tests historiques portés
de la citation proposée par Luna à la citation moteur, assertions d'état
conservées ; les contrôles du dialogue libre restent exercés.

**203 tests distincts / 18 fichiers verts**, zéro échec, erreur ou saut dans
les dernières validations par fichier (`tests-valides.json`, sans cumul).
Les essais intermédiaires en échec restent archivés : attentes historiques
à porter, prémisse invalide de deux marchés atomiques dans une parole et
frontières de segments au raccord. La dernière reprise de G15/G17/narration
est verte (52 tests) ; la dernière reprise G17/passage aussi (28 tests).
Le raccord utilise un espace quand le découpage commun prouve qu'il conserve
les segments, sinon un saut de ligne. Les archives réelles 86/87 restent vertes.
Pas de suite complète ni de banc PNJ.
Deux travailleurs au plus, priorité réduite, uniquement sur des copies.

**Luna.** Une seule passe `comptes` / `soir-appel`, référence historique
`cdaf371` déjà en cache, jamais relancée. Référence relue : six tours MJ,
26 appels, deux relances, trois obstacles, un refus, zéro repli. Le lanceur refuse une référence
absente du cache. Passe de branche à lancer détachée ; zéro réécriture et
zéro repli comptable restent à vérifier sur son fil. `fin-luna.json` est
écrit en dernier, même en cas d'échec.

**Limites et intégration.** Garantie sur les répliques à contenu comptable
typé admises par ce contrat, pas sur toute la sémantique du français libre.
Les voies non portées conservent leurs contrôles ; aucune décision des PNJ
n'est modifiée. Recouvrement G19 (lot 327) : contrôle à l'entrée de
`narration.consigner` et conservation des frontières de segments dans
`raccorder_emissions`. Les règles de rappels ne changent pas.
