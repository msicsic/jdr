# Lot 180 / 180 b — Comptes moteur et paroles compatibles

27 octobre 2026 — Branche `codex-comptes-ecrits-moteur`, **non fusionnée** ;
base initiale `e61cf08`, reprise b sur `885b1c5`. Les essais 117/117 b/117 c
et 168 restent abandonnés. Aucun fichier réservé au lot 179 ni `main` modifié.

**Cause et contrat.** Le premier lot interdisait toute parole financière et
confondait un mot de vocabulaire avec une assertion de compte. Il laissait
également les offres sans couverture. L'invariant demandé pour b est commun :
les comptes viennent du moteur ou d'une parole compatible avec lui, sans nouveau
transfert ni promesse créés par la narration.

`comptes_narratifs.lire/compatibles` lisent une grammaire locale de prédicats,
quantités, rôles pronominaux et références publiques. Le nom « pièce » seul
ne suffit pas ; les questions ne sont pas des assertions, et une obligation
modale sans compte n'est pas une dette. Les rôles de la proposition principale
sont distincts de ceux de la condition d'offre. Les montants reconnus, les états,
les personnes et les objets cités sont comparés aux seuls comptes fournis,
avec un refus et son `attendu` en cas de divergence. L'attribution de la parole
reste celle des contrôles ordinaires. `narration.controler/consigner` refont
ces comparaisons ; aucune extraction comptable n'est ajoutée à l'audit.

`presenter_offres` conserve, dans les données du tour, les offres typées présentées,
avec leurs montants moteur. Une mauvaise réplique puis un repli ne font donc
pas disparaître l'offre déjà présentée. `phrases/completer` donnent le même
contrat de preuve exacte aux issues et aux offres : présence obligatoire,
conservation au repli, contrôle refait avant sauvegarde. Les anciens segments
moteur reconnus comme exprimant le même compte sont remplacés, sans supprimer
les paroles citées. Les contractions et les appositions utilisent l'accord
commun (`francais.groupe_nominal`), sans modifier les noms enregistrés.
La préparation du MJ et l'affichage partagent aussi le formateur des offres :
seuls les noms grammaticaux publics de leurs biens sont fournis, sans position
ni possession cachée. Le service destiné au joueur dit « pour toi », quel que
soit son nom ; les textes techniques entre PNJ ne sont plus affichés tels quels.

**Vérification b sans Luna.** Suite unique : **2 280 tests, 263 fichiers,
1 360,614 s**, deux échecs MiMo historiques `6 != 5` et deux erreurs corrigées
(fixture du prix descriptif, rendu de l'offre de service). **172 ciblés verts**,
22 fichiers, 91,646 s, puis **51 finaux verts**, huit fichiers, 25,193 s,
après le dernier raccord préparation/rendu. Aucune seconde suite complète,
deux travailleurs réduits au plus. Les tests ajoutés pendant la correction sont
dans les reprises ; aucun nouveau défaut restant reproduit hors MiMo.
Console/MJ simulé et recharge : pièce = salle et autre description, Gorm/Aubin
remboursés, Brune restant débitrice, absence de dette, offres à vingt/trente
pièces ; faux montants, sens de transfert, rôles et objet de condition refusés.
Texte affiché, narrations, paroles entendues, conversations, soldes et comptes
rechargés sont contrôlés. Le rendu ancien et le nouveau ne doublent plus
le compte d'absence, avec deux noms à élision et apposition.

**Validation de 180 a transmise par l'orchestrateur**, laptop, `885b1c5` contre
`cdaf371` en cache : quatre scripts en deux passes, appels/tour 5,08 → 4,71,
secondes/tour 19,5 → 18,0, refus 1 → 0, obstacles 11 → 9 ; relances 6,5 → 7,5,
un repli dans deux saisies. Relais/crypte/atelier, une passe : obstacles 4 → 14,
relances 3 → 9, secondes/tour 8,4 → 13,4, un repli. Comptes justes ; les faux
refus et la prime perdue justifient b. Ces mesures ne valident pas le correctif b.
Historique sans modèle de 180 a : 160 ciblés verts après l'unique suite de
2 271 tests, avec deux échecs MiMo historiques `6 != 5` laissés.

**Limite.** La comparaison est déterministe sur la grammaire reconnue, qui
n'est pas une compréhension universelle du français. Les formulations implicites
ou complexes hors de cette grammaire peuvent encore échapper à la détection
ou rester ambiguës ; l'invariant général en langue libre n'est pas garanti.
Les autres jugements mécaniques restent en partie sémantiques. Aucun gain
Luna propre à b n'est certifié.

**Livraison.** Aucun Luna joué par cet agent. Commande exacte dans
`C:/Users/msics/donjon/artifacts/comptes-180/luna-a-jouer.txt` : comptes,
soir-appel, ressources, echanges en deux passes ; relais, crypte, atelier en
une passe, référence `cdaf371`. Tous les bruts restent dans ce dossier,
auquel `artifacts/` du worktree est relié par jonction. Aucune clé de signature
Git configurée : commit non signé, livraison sur cette seule branche.
