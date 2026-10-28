# Tâche Codex 258 (A5, préalable au lot 5) : le devis d'un acteur vu par un observateur

Le lot 257 (`docs/taches/rapport-codex-257-faire-ou-confier.md`, fusionné) s'est arrêté au constat prévu : pour choisir
entre faire et confier, le mandant doit estimer le plan d'un tiers, mais `agendas.devis_mandat` (lot 256) planifie
**comme le tiers**, sur une copie qui garde ses connaissances privées. Preuve rechargée : retirer seulement la croyance
privée d'Aubin sur le lieu de Brune change le devis de 0,225 à impossible sans changer l'esprit de Gorm. Bruts :
`C:\Users\msics\donjon\artifacts\confier-257\` (`diagnostic_257.py`, `diagnostic.json`).

## L'invariant
**Le devis du plan d'un acteur vu par un observateur ne dépend que de données que l'observateur détient : départ et
possessions crus de l'acteur, connaissances que l'observateur sait partagées ou transmises, ses propres relations et
refus retenus, et, pour les capacités ou préférences de l'acteur qu'il ignore, une estimation neutre explicite (valeurs
médianes déclarées une fois, documentées).** Un contexte explicite sépare **observateur** et **acteur** dans les devis
sociaux ; l'esprit du mandant n'est pas recopié en le présentant comme celui du tiers. Le devis réel du jugement du
mandaté (256) reste intact. **Aucun choix autonome n'est raccordé** dans ce lot : il prépare le lot 5 (faire ou confier),
qui reprendra ensuite le choix du sous-but et celui du mandataire en deux fonctions séparées.

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le PC fixe**, au plus 2 processus, priorité réduite.

**Fichiers autorisés d'avance** : `agendas.py` (devis vu d'un observateur, à côté de `devis_mandat`), `planification.py`
(contexte observateur/acteur dans `Vue`, `depart`, coûts ; toutes les lectures projetées dans `_entrees`, caches réel et
estimé séparés), `relations.py` (lecture de l'autorité que l'observateur croit avoir, distincte d'`autorite_mandat`) ; tests
`tests/test_agendas_*`, `tests/test_planif_*` et voisins. **Pas** : `social.py`, `esprits.py` (lot 255 en cours),
`echanges.py` hors lecture, `deliberation.py`, le MJ, les scénarios.

## Vérification
- Épreuves des deux charges du 257 (Gorm → Aubin → Brune, information à Ilse) : déplacer réellement Aubin hors de la
  perception de Gorm, changer son savoir privé, ses possessions non vues, ses liens privés : **devis vu par Gorm
  inchangé** ; changer les croyances de Gorm (où il croit Aubin, ce qu'il croit qu'il porte) : devis changé. Devis réel du
  256 inchangé. Pureté (aucune écriture), sauvegarde et rechargement identiques (monde, rendu).
- Comme aucune décision ne change : empreintes 2 h (`tools/comparer_bancs.py --empreintes`), Relais, mine, auberge, crue
  et hameau, quatre graines, référence `origin/integration` à ta base (cache) : jeu et état complet identiques.
- Pas de suite complète.

## Livraison
- Branche `codex-devis-observateur` poussée. Rapport d'une page `docs/taches/rapport-codex-258-devis-observateur.md` ;
  entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\observateur-258\`. Si la
  poussée est refusée par le contrôle automatique, laisse le commit local et dis-le : le superviseur le récupère. Termine
  par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
