# Lot 180 — Comptes écrits par le moteur

27 octobre 2026 — Branche `codex-comptes-ecrits-moteur`, **non fusionnée**,
base `integration e61cf08`. **Livraison partielle : l'invariant général
de non-reformulation n'est pas garanti.** Les essais 117/117 b/117 c et 168
sont abandonnés selon la décision du brief.

**Ce qui change.** Le récit ne reconstruit plus les comptes depuis une extraction
sémantique. `comptes_narratifs.phrases` écrit chaque compte public `du`, `rendu`
ou `absent` de l'issue, dans les deux sens, sans créer aucun effet. `mj._appeler`
complète le dialogue avant ses contrôles ; le repli après trois refus emploie
également ces phrases. Le catalogue de `narration.textes_etablis` les recalcule
depuis les données moteur, sans drapeau fourni par Luna. Leur présence exacte
est obligatoire et `consigner` refait la preuve avant enregistrement. Les
références et noms viennent exclusivement du dossier public ; un nom ou un bien
non décrit garde une désignation générique. Aucun fichier de comptes ni de
comportement PNJ n'a été modifié.

Le schéma d'audit perd `comptes`, sans nouvelle rubrique. Les anciennes
extractions sont ignorées. La règle de narration réserve ces comptes au moteur ;
la prose libre de Luna garde les réactions et l'ambiance. Une garde lexicale
commune refuse les reformulations reconnues, justes ou fausses, avant l'audit,
avec un `attendu`. Le contrôle est répété à l'enregistrement. Les assertions
physiques des tests existants sont conservées ; leurs répliques financières
simulées sont remplacées par des réactions sans compte.

**Vérification sans Luna.** **160 ciblés finaux verts**, 20 fichiers, 80,702 s.
Suite complète unique intermédiaire : **2 271 tests, 261 fichiers, 1 282,166 s**,
sept échecs et 25 erreurs bruts. Tous les fichiers concernés sont repris verts,
sauf les deux MiMo historiques `6 != 5` laissés ; aucune seconde suite complète.
Les trois nouveaux tests ajoutés pendant la suite font partie des 160 repris.
Les cas console Gorm/Aubin reprennent le remboursement réel et l'inversion ;
deux biens exercent paiement et livraison promise. Les contrôles portent sur
les soldes, les dettes et engagements, le texte affiché, les conversations et
le monde/rendu rechargés. Les phrases comptables exactes n'entrent pas dans
les segments envoyés à l'auditeur. La voie de repli est également exercée sans
aucune réponse d'auditeur.
Rejeu de 177 audits archivés : gardes voix/parole identiques ; six fonctions de
garde communes inchangées par comparaison AST (noms et entités inclus).
155 audits sans compte extrait ni issue : 152 décisions identiques, trois
reformulations financières désormais refusées. Les archives ne contiennent pas
les mondes complets nécessaires pour rejouer les gardes de noms sur leur état.

**Limites et suite.** Le rendu des comptes typés de l'issue est déterministe ;
l'exclusion de toute paraphrase libre ne l'est pas. Une phrase implicite comme
« Entre nous, nous sommes quittes » peut échapper à la garde, et des homonymes
ou emplois non comptables peuvent produire de faux refus. Les transferts d'objet
sans vocabulaire financier restent aussi hors de sa garantie. La détection par
les verbes de transfert a été retirée après le rejeu des archives : elle refusait
une reddition ; aucune exception de phrase n'a été ajoutée. Cette garde ne
constitue donc pas une solution générale aux inversions et ne doit pas être
présentée comme telle. Les consultations et offres hors `comptes.issue` ne
reçoivent pas de nouveau rendu automatique ; les panneaux existants demeurent.
La sémantique des autres affirmations reste celle de l'audit actuel.

**Livraison.** Aucun Luna joué, aucun gain de latence revendiqué. La commande
exacte figure dans
`C:/Users/msics/donjon/artifacts/comptes-180/luna-a-jouer.txt` : deux passes
comptes/soir-appel/ressources/echanges et une passe relais/crypte/atelier/echanges,
référence `cdaf371`, deux exécutions réduites au plus. Bruts exclusivement
dans ce dossier ; `artifacts/` du worktree est une jonction vers lui. Aucun
fichier réservé au lot 179 ni `main` modifié. Aucune clé de signature Git
configurée : commit non signé ; statut de poussée à compléter après livraison.
