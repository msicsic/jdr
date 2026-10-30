# Lot 315 — réclamations et constat sans porteur

Branche `codex-reclamations-repetees`, reprise de **7826c3a**.
Fusion sans rebase de `origin/integration` **07c9b62e**, E1 à E4 et correction
357 comprises. `etat-dev` et l'historique reprennent les versions d'intégration ;
seule l'entrée du 315 (huit lignes au plus) est ajoutée au point de reprise.

**Invariant conservé.** Une réclamation refusée reste retenue selon sa cause,
sans délai ni effet d'un simple déplacement. Le plan aboutit au contact parlé ;
ordre et borne des remboursements, paiement spontané, créances réellement
apprises, références temporelles et remboursement unique E2 sont conservés.

**Cause attribuée.** La réserve de 7826c3a est reproduite après fusion :
`test_service_repropose.ServiceReproposeTests.test_capture_laps_decoupes_et_aucune_execution_invalide`
plante en parlant de la lanterne posée dans le couloir. La sauvegarde admet une
preuve de localisation avec `possession.porteur=None` ; le rendu des constats
introduit au lot **337**, commit **e2822a1**, suppose pourtant un porteur nommé.
Le défaut appartient donc au contrat social antérieur, **révélé par la
chronologie du 315, pas par E2 ni par une rencontre de leurs clauses**.
Le rejeu de l'intégration intacte sans le 315 passe (quatre tests de service).
Le rejeu instrumenté avec le 315 compte **zéro obligation datée et zéro clôture
E2** : ses remboursements datés n'interviennent pas dans ce plantage.

**Correction locale, une cause.** Dans `social.phrase`, une preuve sans porteur
décrit le lieu enregistré avec le constat : salle, contenant ou porteur désigné
par cette localisation, sinon lieu inconnu. Elle n'invente ni identité, ni
propriété, ni permission. Les constats de portage gardent leurs mots et leurs
droits. `social._lieu_dit` cite la localisation effectivement formulée pour
appliquer les contrôles communs d'audition et de connaissance ; un contenant
inconnu n'est pas révélé au joueur. Aucun objet, scénario, prompt ou migration
spécifique. Les positions privées ne sont pas consultées pour raconter le constat.

**Épreuves.** Les parcours ciblés donnent 28 tests distincts verts : huit
réclamations, quatre services et seize transmissions de garde. La capture réelle
passe en quatre minutes de jeu, d'un bloc ou découpées, monde/rendu/scène
identiques après recharge. Les ajouts transmettent une ancienne preuve sans
porteur au Relais et à l'auberge, dans une salle et dans un contenant, tandis
que le bien réel est désormais ailleurs ; mots et croyance suivent la preuve,
l'objet réel reste inchangé. Un contenant privé est effectivement caché au
joueur. État complet, rendu et scène sont vérifiés après sauvegarde/recharge.
La validation groupée de **54 fichiers**, couvrant 315, E1–E4, 357 et les modules
concernés, est en cours, à deux processus à priorité réduite. Fin attendue :
`C:/Users/msics/donjon/artifacts/reclamations-315/social-07c9b62/fin.json`.

**Mesures et limites.** La passe précédente sur 8f410f7 comptait 357 tests :
347 verts, neuf échecs identiques sur cette référence et la réserve sociale
corrigée ici. Ces résultats ne sont pas présentés comme ceux de la nouvelle
intégration. Les nuits historiques du 315 ne sont pas rejouées : treize des seize
empreintes étaient identiques ; trois premières demandes remboursées changeaient
la chronologie, avec causalité et conservation des pièces établies. Les suites
ultérieures de ces chronologies ne sont pas toutes certifiées bénignes.
Ni suite complète, ni Luna, ni nouvelle campagne de bancs. Détails historiques :
rapport au commit 7826c3a et bruts `artifacts/reclamations-315/` du dépôt principal.
Reproduction, état fautif, témoin sans 315 et résultats de cette reprise :
sous-dossier `social-07c9b62/`.
