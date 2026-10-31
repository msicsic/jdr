# Tâche Codex 403 : les rouges nouveaux de la suite c562aa21

La suite complète de l'intégration `c562aa21` (3 359 tests) donne **37 échecs et 4 erreurs**. Une partie est déjà
corrigée par des lots fusionnés depuis : 391 (parité acoustique), 392 (scènes connues), 394 (don par U-C), 395 (avis
redits), 396 (paiement TUI). **Ce lot traite les 19 méthodes restantes**, listées dans
`C:\Users\msics\donjon\artifacts\suite-c562aa21-restants.txt` (laptop ; journal entier `suite-c562aa21.log` à côté).
Familles visibles :
- **dettes, remboursements, comptes** : `test_petits_correctifs.PartPayeeTests.test_le_joueur_est_rembourse_et_le_lit`,
  `test_realisation_datee` (trois), `test_reclamations_repetees` (trois), `test_agendas_socle.ChaineTests` (deux),
  `test_accord_date` (un). Suspects probables : 388 (remboursement volontaire), 380 (raccourcis de comptes),
  393 (réservation) ;
- **parcours de remise et consentement** : `test_inventaire_terminal` (console, TUI), `test_nom_non_relie`,
  `test_tuer.test_joueur_ligote_cri_temoin_nouvelle`. Suspect probable : 380 (remise par U-C, que le 394 a jugée
  conforme : adapter seulement si c'est la même cause, preuve citée) ;
- `test_echelle_choix` (trois méthodes, dix sous-tests) : l'échelle commune des candidats (lot A0) ;
- `test_contenus_parole.test_schema_et_validateur_partagent_tous_les_champs_sans_sens` : un contenu de parole nouveau
  (388 `rembourser` ?) absent du schéma ou du validateur ;
- `test_parole_corrections.NommerUneVoixTests.test_meme_nature_au_contact_et_par_la_parole`.

Fusions entre `663d1308` (suite précédente, où ces méthodes étaient vertes) et `c562aa21` :
`git log --first-parent 663d1308..c562aa21` (387, 388, 389, 390, 375, 380, 393). Lis `AGENTS.md`,
`docs/etat-dev.md` (court), les rapports 380, 388, 390 et 394.

## Invariant
**Chaque méthode rouge est attribuée à la fusion qui l'a fait basculer (bissection `--first-parent` entre `663d1308` et
`c562aa21`, sur ces seuls fichiers), puis corrigée dans le contrat commun si la cause est claire et locale, ou adaptée
seulement si son attente est devenue fausse par un changement voulu et documenté (preuve citée, assertions de sécurité
intactes) ; sinon listée avec la question précise.** Commence par la famille des dettes. Vérifie d'abord sur
l'intégration actuelle : une méthode déjà verte n'est pas à traiter. Si le créneau ne suffit pas, livre les familles
corrigées et liste le reste avec sa fusion fautive.

## Vérification
Les fichiers de tests concernés ; pour chaque correctif du moteur, un cas réel et un autre cas après recharge ;
empreintes 2 h Relais et scénarios touchés, quatre graines, si du code du jeu change. Pas de suite complète (une tourne
sur `4311249e`), ni Luna.

## Contraintes
**Poste : le laptop.** Lots en cours : 381 (A2 passage), 399 (rembourser depuis le menu et le terminal : `dialogues.py`,
`comptes_terminal.py`, `jeu.py`, `tui.py`), 400 (S1g) ; signale tout recouvrement. Pendant S1, n'ajoute aucun registre
d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés : vérifie qu'ils vivent avant de rendre la
main. La poussée de ta branche vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-suite-c562aa21`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-403-suite-c562aa21.md` : tableau méthode → fusion fautive → cause →
  correction ou question ; entrée « non fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme
  la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\suite-c562aa21-403\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
