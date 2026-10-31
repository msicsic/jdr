# Lot 433 — Référence publique dès la création

31 octobre 2026 — `codex-reference-neuve`, base reçue `1c7df834`
(issue d’`integration`, ancêtre d’`origin/integration`). PC fixe `msi-desktop`.

**Invariant.** Une entité créée par une proposition admise est inscrite dans
le registre commun sur la copie transactionnelle, avant toute attestation,
description ou préparation du geste suivant. Rejeter la proposition laisse
le monde original et son registre inchangés.

**Changement.** `noms.inscrire` est la porte commune, idempotente, d’attribution
des références d’éléments et des désignations de personnages. `noms.installer`
l’utilise aussi à l’installation, à l’adoption et à la recharge. Les deux
fabriques de propositions l’appellent immédiatement après l’ajout de l’entité :
`enrichissement.preparer_complements` et `faits_locaux.preparer_faits`
(détail, inscription, objet, matérialisation G12/G14). Les qualifications
conservent l’entité et son numéro. Les lectures de références restent sans
mutation ; aucun registre d’esprit, changement de prompt ou de MJ.

**Vérification.** La capture R58 est rejouée avec fournisseur simulé, sans
modifier la proposition des mains : `element_47` résout le détail avant les
attestations, la description est affichée et le même lien subsiste après
recharge. Même chaîne sur les yeux d’Aubin. La capture ne prend toujours
aucune planche : la fidélité de cet enrichissement reste hors périmètre.

G14 : pierre mouillée du Relais et éclat de bois de l’atelier, chacun créé
puis pris dans la même proposition ; inscription vérifiée avant adoption,
objet unique, référence stable, état et vue identiques après recharge.
Autres contrôles : plusieurs compléments sans renumérotation, détail et
inscription, qualification puis prise, idempotence, refus hors de vue,
rejet après un premier ajout et rejet sémantique sans fuite du registre.

**Mesures.** **19/19 tests verts** sur les quatre fichiers modifiés (152,5 s,
priorité réduite, un processus). Avec les huit autres fichiers voisins déjà
joués : **103 tests uniques, 102 méthodes vertes**, une méthode préexistante
en erreur sur deux sous-cas (ci-dessous). La sélection comprend rendu 432, ciblage d’ambiance, création
interactive, qualification, enrichissement, noms, désignations, attendus
désignables, matérialisation, faits locaux et non-perception.
Deux workers au plus, priorité réduite. Aucun appel Luna, banc ou suite complète.

**Limites.** Le test de noms
`test_frontiere_mj_refuse_l_id_devine_puis_accepte_la_reference_publique`
reste en erreur sur ses deux sous-cas Aubin/Gorm (`RefusDeForme` de reprise,
puis `StopIteration` du fournisseur simulé). Même erreur reproduite sur
copie isolée de la base `1c7df834` : non corrigée dans ce lot.
Les gardes de perception et de non-fuite restent actives ; connaître une
référence ne rend pas sa cible visible ou manipulable.

Bruts : `C:/Users/msics/donjon/artifacts/reference-neuve-433/` :
`tests-voisins.json`, `preexistants-base.json`, `tests-cibles-finaux.json`,
`tests-cibles-finaux.log`, `rejeux.json` et états `rejeu-*-monde.json`.
