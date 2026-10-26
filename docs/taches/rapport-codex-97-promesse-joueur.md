# Lot 97 — devis réservés aux personnages autonomes

Branche `codex-promesse-joueur`, non fusionnée, base `be5fe50`, code signé SSH
`886eae5`. Le plantage est reproduit avant correction dans la console réelle
avec MJ simulé, sur la crypte et sur le Relais : même `TypeError` dans
`Vue.pertinent`. Dans cette reproduction, l'acteur sans profil est **Gorm**,
auditeur qui devrait aller chercher le bien demandé ; l'identité de l'acteur de
la partie initiale n'est pas enregistrée dans sa trace. Le joueur n'est donc
pas la seule frontière à protéger.

Invariant : aucun devis autonome pour un acteur sans profil. `_devis_proposition`
et `devis_service` renvoient l'absence de devis avant toute recherche ou inscription
provisoire ; les fournitures futures d'un bénéficiaire sans profil suivent cette
même limite. `_livraison_proposition` conserve la remise possible en main et
refuse la prise future sans autonomie. `chercher` et `devis_pulsion` signalent
explicitement un appel interne invalide (`ValueError` avec identifiant), sans
toucher aux graphes ni aux certificats. Le refus ordinaire passe par le bilan
`impossible` et les faits du dialogue ; aucune nouvelle `ErreurMonde`.

Vérification : **17 tests ciblés, un ignoré**, 16,50 s, deux processus réduits.
Deux scénarios, remises acceptées/refusées selon possession, absence de transfert
et d'engagement fantôme, état rechargé, sortie console et conversation persistée ;
gardes vérifiés aussi pour le joueur et un identifiant inexistant. Empreintes
Relais **2 h × quatre graines identiques** à la base : chronique, mesures et état
complet ; quatre références calculées une fois et rangées dans le cache commun.
Passe Luna unique : crypte **42 tours / 22 appels**, ressources **3 tours /
12 appels** ; aucun arrêt, erreur technique, repli ni défaut de rechargement.
Attente moyenne par tour MJ : **8,0 s / 12,4 s**, sans comparaison de performance.
Suite complète unique : **1 967 tests, 16 ignorés, 1 912,52 s**, deux processus
réduits ; une erreur TUI de remplacement de fichier temporaire (`WinError 5`
dans `Monde.sauver`, avant l'action du test). **Rejeu du seul test vert en
1,73 s**, sans modification ; aucun défaut restant reproduit, aucune seconde
suite complète. Bruts dans `artifacts/reproduction-97.txt`,
`tests-cibles-97.json`, `tests-complets-97.json`, `rejeu-tui97.txt`,
`empreintes97.json` et `luna97/`.

Limites : un personnage sans profil ne reçoit pas d'autonomie nouvelle ; sa
livraison future est refusée même si le joueur pourrait imaginer un trajet.
Les remises du joueur exigent toujours l'effet matériel réel du moteur, sans
exécution automatique de ses promesses. Le jugement des tâches reste celui de
l'auditeur et de ses croyances ; aucune garantie sémantique nouvelle sur Luna.
