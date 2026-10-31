# Lot 432 — Refus du rendu avec attendu

31 octobre 2026 — `codex-refus-rendu-attendu`, base `origin/integration` / `e05e2b5b`.

**Invariant.** Un refus de cible ou de publication sur la voie rendu/attestations
porte le champ, la valeur reçue et la correction admise ; les candidats restent
publics. Aucun refus n'autorise la publication d'une description non perçue.

**Cause de R58.** Sur la capture réelle `branche-04-monde.json` du 423,
`personne_1` désigne correctement Aubin. Aubin et les mains proposées sont
visibles. `preparer_complements` ajoute `detail_aubin_mains` sur sa copie ;
`noms.reference` lui calcule `element_47`, mais ce nouvel objet n'a pas encore
d'entrée dans `references_personnes`. `voix.reel(element_47)` renvoie donc `None`.
Ce n'est ni un personnage hors de vue, ni une résolution vers un autre personnage :
les attestations perdaient la référence reçue avant d'appeler `decrire(None)`.

**Changement commun.** `refus.attendu_rendu` projette la valeur reçue et borne
les corrections aux entités désignables, admises par la perception requise et
dont la référence publique se résout effectivement. Un identifiant interne
d'entité non désignable est masqué. `rendu.decrire` et `toucher` résolvent eux-mêmes
la référence, conservée pour leur refus ; `position` emploie le même attendu.
`narration.attestations` transmet la référence publique intacte. R58 devient
`decrire.cible : reçu 'element_47' ; acceptés : …`, sans proposer à nouveau cette
référence indécodable. Les refus sans attendu de `consigner` sont complétés et
ses gardes de publication conservent chacun leur première cause. Les erreurs
de forme `AuditIllisible` portent également leur champ, reçu et schéma admis.
Ni `mj.py`, ni prompt, scénario, registre d'esprit ou contrôle de non-fuite modifié.

**Vérification.** Six nouveaux tests passent : capture R58 avec fournisseur
simulé, autre facette (`yeux`), contexte périmé pour un objet devenu invisible,
parcours des trois rendus sur toutes les entités de deux mondes, publication et
audits illisibles, garde AST de toutes les levées explicites `ErreurMonde` et
`AuditIllisible` de ces deux modules. Les deux rejeux console contrôlent le
refus, l'absence de mutation et de prose rejetée, puis un examen moteur accepté,
l'état et la vue après recharge. La capture ne permet pas encore le prélèvement
des planches sans qualification : ce lot ne prétend pas l'exécuter.

Tests voisins : **120 tests**, **115 méthodes vertes**, **3 échecs et 4 erreurs
sur cinq méthodes préexistantes**, tous reproduits sur copie isolée de la base
`e05e2b5b` (4 méthodes de `test_refus_moteur`, 1 de `test_narration`).
Sélection : rendu 432, narration, refus, attendus désignables, audits d'attendu,
enrichissement, non-perception, perception, localisation, refus moteur ; deux
workers, priorité réduite. Aucun appel Luna, aucune suite complète ni banc.

**Limites.** Le lot garantit l'attendu des refus de cette voie ; il ne répare pas
l'inscription des références neuves et n'ajoute pas de recadrage automatique au
MJ après un refus terminal des attestations. La correction console est une
nouvelle demande d'examen. La fidélité de l'enrichissement hors sujet reste hors
périmètre. Les défauts voisins préexistants ne sont pas corrigés ici.

Bruts : `C:/Users/msics/donjon/artifacts/refus-rendu-432/` : `rejeux.json`,
états après correction, `tests-voisins.log`, `preexistants-base.log`,
`inventaire-refus.json`, `tests-cibles-finaux.log`, `fin.json`.
La capture de régression compressée est versionnée dans `tests/data/` ;
l'archive d'origine reste intacte (SHA-256 contrôlé).
