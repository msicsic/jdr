# Tâche Codex 357 : la régression d'E3 sur les tâches payées

Petit lot de correction. La fusion d'E3 (lot 352, `codex-e3-delai-cru`, commit de fusion `fa9af2de` : le délai d'une
obligation est jugé sur les moyens crus du contractant) fait échouer quatre tests de `tests/test_taches_payees.py`, verts
juste avant (fusion d'E2 `dbb122b0`) et dans la suite complète de `7eb45ff` :
- `test_tilo_sans_flamme_ne_fait_pas_travailler_odile` : `'accepte' != 'impossible'` (ligne 89) ;
- `test_relais42_la_part_ne_reste_pas_due_soixante_minutes` : `unexpectedly None` (ligne 60) ;
- `test_relais_refus_connu_ni_vente_ni_encaissement_et_refus_retenu` : `True is not false` (ligne 77) ;
- `test_le_bien_du_payeur_peut_etre_emprunte_pour_agir_soi_meme` : `False is not true` (ligne 118).

Lis `AGENTS.md`, `docs/etat-dev.md` (court), les rapports 352 (E3), 350 (E2) et le brief/rapport des tâches payées
(cherche « taches-payees » ou « devis_pulsion » dans `docs/historique-lots.md`, sans le lire en entier).

## Invariant
Le contrat des tâches payées et des parts promises reste celui d'avant E3 : une tâche, une part ou un objet se
promettent, se font et s'abandonnent sur le même devis autonome (`planification.devis_pulsion`, `planifier_engagement`,
`echanges.empeche`) ; un contractant qui ne peut pas faire le travail selon ses croyances (Tilo sans flamme) le refuse
« impossible » ; un refus connu n'entraîne ni vente ni encaissement. **E3 ne doit changer que le jugement d'une limite
datée**, et seulement pour une obligation qui en porte une (aucune dans ces tests). Trouve où E3 a changé le chemin commun
des obligations sans limite (devis, durée, admissibilité, refus) et rétablis-le, sans retirer ce qu'E3 garantit pour les
obligations datées.

## Vérification
`tests/test_taches_payees.py` vert ; tests d'E1 à E4 (`test_reference_temporelle`, `test_realisation_datee`,
`test_delai_cru`, `test_accord_date`) verts ; voisins (propositions, refus retenus, devis observateur, échanges,
`test_crochetage_surenchere`, `test_refus_retenus`). Empreintes 2 h, quatre graines, Relais, auberge et mine contre
`dbb122b0` (avant E3) : identiques. Pas de suite complète, ni Luna, ni banc long.

## Contraintes
**Poste : le PC fixe.** Fichiers : ceux qu'E3 a touchés (`echanges.py`, `planification.py`, `deliberation.py`,
`agendas.py`) et les tests. Priorité réduite, deux processus au plus.

## Livraison
- Branche `codex-e3-taches-payees`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-357-e3-taches-payees.md` ; entrée « non fusionnée » de 8 lignes au plus
  dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\e3-taches-357\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
