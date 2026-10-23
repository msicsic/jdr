# Rapport Codex 24 — A1, le socle des agendas

Branche `codex-a1-socle`, **non fusionnée**, depuis `origin/codex-a1-socle` **ccd8751**,
base fonctionnelle A0 **2ddebe4**. Worktree `tmp-worktrees/codex-a1-socle`.
Implémentation **162986d**, signature SSH vérifiée localement ; livraison poussée sur cette
branche, sans fusion dans `main`.

**Invariant et API.** `donjon/agendas.py` centralise l'accès au stockage historique :
`en_cours` renvoie des copies, dans l'ordre enregistré, filtrables par condition, objet,
personne et état actif ; les annulations à annoncer restent incluses par défaut.
`prendre`, `retirer_proposition`, `tenir`, `annoncer_abandon`, `echoir` et
`oublier_personne` portent les écritures. Les souvenirs des gestes restent à leur instant
historique ; le cycle d'échéance conserve l'ordre des souvenirs, remboursements et prêts
de clés. `verifier` porte la validation existante. `CHAMPS` conserve le défaut de stockage
à sa place dans l'esprit ; `depart` copie `profil["agendas"]`, sans activation ni écriture.
Les accords de mission passent par `contrats`, `installer_contrats`, `proposer_contrat`,
`repondre_contrat`, `payer_contrat`. `declares` lit les champs publics rendus ou sauvegardés.

**Sites convertis.** `deliberation`, `echanges`, `dialogues`, `paroles`, `biens`, `esprits`,
`monde`, `narration`, `corps`, `stratege`, `planification` (une lecture et l'import),
`tools/audit_nuits.py`, `tools/test_part_reel.py`, `tools/test_dialogues_reel.py`,
`tools/valider_mimo_parties.py` (comparaison indirecte de sauvegarde).
`pnj.py`, `signes.py` et les scénarios restent sans changement. L'audit charge le socle
livré avec son outil pour pouvoir aussi observer un moteur antérieur à A1.

**Preuves.** Le contrôle AST relève **46 accès directs sur 42bb9c0**, dans quatorze
fichiers ; aucun hors du module après conversion. Il couvre indices, affectations,
suppression et méthodes de dictionnaire usuelles, également pour la clé `agendas`.
Les dictionnaires publics produits pour le MJ et l'audit gardent leur format.
Cinq nouveaux tests : contrôle et éprouvette AST, lectures sans mutation, données de
départ sans effet ; part achetée à Aubin au Relais, sauvegardée promise puis remise ;
tâche payée à Tilo, sauvegardée acceptée puis abandonnée après perte du moyen d'allumage,
avec remboursement visible de 20 pièces. État, possession, argent, souvenirs et engagements
présentés au joueur sont contrôlés après rechargement. **Ciblés verts.**

Suite complète, une seule passe de `tools/tests.py --processus 3` :
**1 600 tests, 4 ignorés, verte (349,6 s)**, priorité réduite.
Empreintes contre **2ddebe4**, 2 h, Relais/mine/auberge/crue × 1985/7/42/2024 :
**16 paires identiques**, chronique, mesures et état final complet. Aucun plantage.
La référence, absente à ce commit, a été calculée une fois et conservée dans
`artifacts/references/2ddebe4017cfeec2d4fcd17d9fe923176f4112bb/a1-empreintes-2h.json`
du dépôt principal. Traces du worktree : `artifacts/empreintes-a1.json`,
`artifacts/tests-a1.json`, `artifacts/cibles-a1.json` (socle et comparateur : 11 tests verts).

**Limites.** Le stockage `esprit["engagements"]` reste inchangé, sans nouvelle clé d'agenda.
La conversion en agendas d'origine `parole`/`contrat` et les mécaniques futures attendent
le premier lot qui en a besoin. L'AST contrôle les accès explicites, sans analyse de flux
des clés calculées ; les copies empêchent une mutation du stockage par les lectures du module.
L'identité des nuits est établie sur les seules graines et durées prescrites ; aucune
garantie de stabilité du coût CPU n'est revendiquée. Aucun appel Luna, banc de 8 h ou audit
supplémentaire ; les traces brutes restent dans `artifacts/`, hors Git.
