# Lot 315 — réclamations et contact du débiteur

Branche `codex-reclamations-repetees`. Réaccordance du 2026-10-30 : fusion Git
**248298c**, sans rebase, du 315 **beaecc7** avec l'essai **8f410f7**.
**Livré avec une réserve supplémentaire ; validation globale non verte.**

**Invariant.** La réponse à une créance tient selon sa cause, sans délai ni
effet d'un simple déplacement. `planification.reclamer` aboutit à une demande
typée ; `echanges.executer`, `biens.regler/solder/entrees_creance` et
`deliberation` partagent cette rétention. Les remboursements spontanés restent
possibles. La fusion conserve l'ordre et la borne des remboursements du 315,
les références E1 et les réalisations datées et remboursements uniques d'E2.
`dettes(..., connues_de=...)` fournit aux trois lecteurs de décision les seules
créances apprises : une dette `a_prevenir` ne prépare aucune demande et ne
lève aucun refus. Les comptes physiques continuent à inclure toutes les dettes.
Aucune date ni issue E1/E2 réécrite ; aucun scénario ou MJ modifié.

**Épreuves de fusion.** **357 tests / 37 fichiers : 347 verts, neuf échecs,
une erreur**, 530,644 s, deux processus à priorité réduite. Les huit tests
315, neuf E1, douze E2, protections et planification sont verts. Les deux
nouveaux tests croisent chacun livraison d'huile et verrouillage payé :
dette inconnue, ancien plan silencieux, refus durable, réponse locale,
remboursement volontaire et archive unique. Ils comparent monde, rendu et
scène perçue après recharge. La capture réelle Sève/2024 contrôle deux
remboursements ordonnés, au plus tard à la minute 84, sans relance ensuite ;
laps entier/découpé et recharges sont identiques. Sources testées inchangées.
Les **neuf échecs sont identiques hors chemins sur l'essai intact 8f410f7** :
événements perçus (2), prêt de lampe (1), comptes en console (5), console du
brasero (1). Reprise des seuls cinq fichiers concernés : 68 tests, neuf
échecs, aucune erreur, 84,342 s.

**Réserve supplémentaire de la combinaison.** Le test
`test_service_repropose.ServiceReproposeTests.test_capture_laps_decoupes_et_aucune_execution_invalide`
plante dans `social.phrase` (`KeyError: None`). Le constat réel de la
`lanterne_couloir`, posée dans le couloir, porte `possession.porteur=None` ;
le rendu suppose un porteur nommé. `social.py` est identique à l'essai :
le même état et le même constat y reproduisent l'erreur, mais le rejeu
complet sans le 315 ne la déclenche pas. La chronologie du 315 révèle donc
un défaut du contrat commun des constats de biens posés. **Cette capture
complète reste non validée.** Un lot distinct doit traiter ce contrat,
sans exception pour la lanterne. Aucune absence générale de régression
n'est revendiquée.

**Mesures antérieures conservées, non rejouées.** Le bilan initial
(base `c4f6d46`, moteur `faa5967`, rapport détaillé au commit `beaecc7`)
comptait 127 tests verts. Hameau/306, quatre graines sur 4 h :
suspects 0/0/0/7 → 0/0/0/0 ; à expliquer 7/5/0/10 → 2/5/0/4.
Sur les seize empreintes 2 h, treize étaient identiques ; les trois écarts
Relais/7, auberge/1985 et crue/1985 étaient des premières demandes remboursées,
pas des relances après refus. Six courts rejeux causaux confirmaient
l'effet du contact accompli, avec remboursement unique, conservation des
pièces et recharge fidèle. **Identité stricte non atteinte** ; les effets
ultérieurs de ces nouvelles chronologies ne sont pas tous certifiés bénins.
Anciennes sauvegardes sans refus durable : aucune migration n'invente les
moyens jadis connus. Prêts et autres demandes gardent leur contrat.

**Livraison et bruts.** `docs/etat-dev.md` reprend l'essai, avec la seule entrée
du 315 ajoutée (huit lignes). Bruts historiques :
`C:/Users/msics/donjon/artifacts/reclamations-315/`.
Réaccordance : sous-dossier `fusion-e1-e2/`, `tests.json`,
`tests-reference-8f410f7.json`, `qualification.json` et
`social-crash-{monde,noyau,rendu-reference}.json`.
Ni suite complète, ni Luna, ni nouvelle campagne d'empreintes ; E3 non refusionné.
Aucun calcul actif.
