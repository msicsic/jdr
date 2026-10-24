# Lot 35 — Une accusation reçue ne devient pas une confidence sur soi

Branche `codex-soi-meme`, non fusionnée, issue de `41c1c7c` (brief `2a96b84`).
Correctif signé SSH `8fa071f`, 24 octobre 2026. Aucun changement du MJ ni des scénarios.

**Cause établie.** Les deux nuits de crue ont été rejouées sur huit heures, graines 2024 et 7,
avec Corvus dans `chambre_cloche`, comme dans l'audit (le placement de départ par défaut donne
une autre nuit). À 421, Aubin accuse Brune de porter les planches ; à 373, il lui dit qu'elle
semble guetter la réserve. `bavarder` appelait directement `_adopter` puis enregistrait une
rumeur chez l'accusée. Brune la transmettait à Gorm à 421, ou à Ilse à 391. Il s'agit bien d'un
comportement, sans erreur d'attribution du récit. La lecture initiale est celle d'Aubin,
pas une lecture de ses propres signes par Brune.

**Invariant et fonctions.** `social.bavarder` emploie désormais `social.recevoir`, comme les
témoins auditifs : l'accusation peut être prononcée et entendue, sans apprendre à l'accusé une
rumeur sur lui. Les conséquences sur les biens des destinataires restent comptées une seule
fois, y compris les incidents regroupés. `social.nouvelles` exclut les nouvelles qui accusent
leur transmetteur, même dans une ancienne sauvegarde ; `recevoir` exige un contenu `aveu`
pour transmettre une accusation contre son propre locuteur, joueur comme PNJ. Les aveux
explicites conservent leur effet dans `relations`. `signes.lire` et la perception des signes
écartent l'observateur lui-même, y compris pour une liste de signes ou de tons fournie par un
appelant. Aucun nouveau mode, mot-clé, texte de prompt ou cas de scénario.

**Preuves après rechargement.** `tests/test_soi_meme.py` : quatre tests, quatorze sous-cas
(Brune/planches et Ilse/marteau ; portage et intention ; anciennes rumeurs de portage,
d'intention ou de mensonge ; aveux du joueur et d'un PNJ ; signes visuels et tons).
La minute du moteur vérifie les mots affichés, la possession, les souvenirs et le récit
rechargé. Les dix sous-cas de réception/transmission échouent avec les fonctions de
`41c1c7c`. Les deux captures des nuits réelles, prises avant la répétition fautive,
ont aussi été reprises sur quinze minutes puis sauvegardées et rechargées : aucune nouvelle
auto-accusation retransmise. Les 58 tests ciblés sociaux, de parole et de signes sont verts ;
le fichier enrichi a ensuite été revérifié.

**Banc rapide prescrit.** `comparer_bancs.py`, référence `41c1c7c`, crue et Relais,
4 h × quatre graines (1985, 7, 42, 2024), trois processus à priorité réduite : huit nuits par
version, aucun plantage ni usurpation ; constats d'audit identiques nuit par nuit. Les mesures
de jeu sont identiques sauf crue 1985 : l'accusation de Gorm à Brune à 203 n'est plus soumise
à persuasion (`connu` dans la chronique, au lieu de `doute`) ; un jet et une rumeur doutée en
moins, soit les moyennes 7,75 → 7,5 jets et 1,25 → 1 rumeur doutée. Aucun changement de boucle
ou de déplacement. Référence absente du cache : calculée une fois et rangée dans
`artifacts/references/41c1c7c1b8e05d76e4c707c4466b9313fd7b081e/`. Temps de calcul sans conclusion
de performance, la charge n'étant pas constante. Suite complète unique, trois processus,
2 207,3 s : quatre erreurs d'environnement (deux sockets Web refusés et deux fichiers TUI
bloqués, arrêtés seuls). Reprises hors bac à sable : Web 8 tests verts, TUI 33 tests verts
(187,3 s, un processus). **Bilan consolidé : 1 680 tests, 16 ignorés, aucun échec restant**
sur 156 fichiers. Les blocages TUI ont allongé le lot au-delà des 45 minutes visées.

**Limites.** Aucun choix autonome d'avouer n'existait pour les PNJ ; ce lot n'en ajoute pas
et n'introduit donc pas de nouvelle pondération par leurs valeurs. Le joueur décide de ses
aveux. La garde porte sur les accusations structurées reconnues par `social.accuse`, pas sur
la compréhension sémantique de toute prose libre. Les anciennes rumeurs et leurs effets
historiques restent sauvegardés, mais ne sont plus transmissibles contre soi ; la chronique
passée n'est pas réécrite. Aucun appel Luna ni campagne lourde d'intégration.

Bruts : `artifacts/codex-35/` du worktree (rejeux `avant-audit-*`, captures `scene-*`,
`reprises-reelles.json`, `contre-preuve.txt`, `cibles.json`, `soi-meme.json`,
`comparaison.json`, `suite.json`, `reprise-web.json`, `reprise-tui.json`, `validation.json`).
