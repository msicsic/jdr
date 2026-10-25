# Lot 67 — Une offre conditionnelle n'est pas une dette

Branche `codex-prime-offre`, non fusionnée, base **cd25fcd** (intégration
**d78cfcc** déjà incluse ; `origin/integration` n'avait pas avancé au départ).

**Invariant et changement.** Le contrôle des comptes ne savait représenter que
les soldes dus, les remises et leur absence. Il extrayait donc une prime promise
comme une dette actuelle, puis la refusait. `propositions.offre` donne désormais
aux missions et aux marchés la même forme : débiteur de la contrepartie, créancier,
prestation conditionnelle et contrepartie, avec les termes typés du lot 29.
`dialogues.offre_mission` prend le montant dans l'accord ou `prime_base`, vérifie
les fonds et écarte les offres refusées ou payées. Le dossier public de mission
donne aussi le lieu actuel du donneur : « ici » peut être jugé dans l'état présent,
sans être assimilé automatiquement à une condition nouvelle.

`biens.offres_joueur` et `mj._echanger` fournissent ces offres à la narration et
aux comptes ; `paroles._proposer` rapporte les termes validés d'un échange.
L'auditeur extrait une offre avec `etat: offre`, séparément de `du` et `rendu`.
`narration.controler` compare exactement rôles, prestation et contrepartie, et
`consigner` refait ce contrôle avant écriture. Les formulations du moteur peuvent
fonder un engagement conditionnel sans lancer sa réalisation. La remise de mission
reste atomique : transfert et paiement au même geste ; son règlement est fourni
comme compte `rendu` au récit de résultat. Aucun nouveau solde intermédiaire,
aucun cas propre à un objet ou personnage, aucune consigne de scénario ajoutée.

**Preuves sans modèle.** Cinq tests nouveaux : vraie console et fournisseur simulé,
sauvegarde puis recharge. L'offre de 20 pièces passe avec sa condition, en discussion
ordinaire comme en négociation typée, sans dette ni repli ; la remise paie dans le
bon sens et clôt l'offre ; un marché contre une tâche différée conserve sa promesse
sans inventer sa réalisation. Mauvais montant, prestation et rôles, ainsi que fausse
dette actuelle, sont refusés ; garde refait à l'enregistrement. Les 44 tests ciblés
des comptes, propositions, dialogues et portée passent (un ignoré).
La suite unique relève deux tests de noms inconnus devenus incompatibles avec le
banc `comptes` désormais présenté, et deux accès directs au stockage des contrats.
Préparation inconnue rendue explicite et accès remplacés par `agendas.contrats` :
les 22 tests de parole et les 28 tests offres/dialogues/socle rejoués sont verts.
Suite unique : **1 839 tests, 16 ignorés**, 1 973,6 s, trois processus à priorité
réduite ; un échec et deux erreurs initiaux, tous corrigés et rejoués dans leurs
fichiers. Aucun défaut restant connu ; aucune seconde suite complète.

**Luna, une seule passe.** `crypte`, `ressources`, `comptes` avec noms préparés.
Prime réelle : **4 appels, aucun refus, aucune relance ni repli** ; affiché :
« Vingt pièces, quand tu me remettras l’anneau du veilleur ici. »
Crypte entière : 25 appels / 9 tours MJ, aucun repli ni erreur. Ressources :
11 appels / 3 tours, aucun repli ; la dernière question demande une relance de
compte, puis affiche les deux sens sans inversion. Comptes : Gorm rencontre un
délai réseau avant toute opération (un repli technique) ; Brune refuse de rendre
ses deux pièces, dans le bon sens, en trois appels. Aucune erreur de recharge.
Cette passe ne valide donc pas le remboursement de Gorm en ligne.

Le cache du `main` **42bb9c0** contient la crypte (24 appels / 9 tours, aucun repli),
mais pas les autres scripts dans les conditions présentes. Le lanceur récent ne
peut rejouer ce vieux commit (`ImportError: agendas`), échec avant tout appel au
modèle. Le cache intégré **f033364** est relu : crypte 24 appels, ressources 9,
comptes sans noms préparés zéro ; périmètres différents, pas de comparaison de
latence ni de total global. Bruts : `artifacts/bancs-multi/20261025-091824-10028/`.

**Limites.** La comparaison est déterministe sur les termes extraits ; reconnaître
une offre, résoudre les pronoms et juger une reformulation restent sémantiques.
Une offre omise ou mal extraite peut encore provoquer un faux refus ou laisser
passer une contradiction. Pas de garantie générale sur toute paraphrase française.
Ni `main`, ni `planification.py`, ni `signes.py`, ni le modèle Luna ne sont modifiés.
