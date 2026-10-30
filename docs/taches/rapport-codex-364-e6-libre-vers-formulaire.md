# Lot 364 — E6 reprise, le libre ouvre le formulaire E5

Branche `codex-e6-libre-date`, base `origin/integration e6555c51` fusionnée
sans rebase (`284f9d38`). Seul conflit : `etat-dev.md`, version d'intégration
retenue. **Vérification finale en cours, non fusionné, validation à conclure.**

**Invariant porté.** `accords_libres` distingue l'orientation vers le choix
direct d'une parole exécutable. Son brouillon ne parle, ne paie, ne promet et
ne modifie rien. Destinataire, prestation et prix ne sont préremplis que s'ils
appartiennent aux choix publics E5 et aux fonds disponibles. Les autres
champs restent vides. Le joueur corrige et soumet le formulaire, puis U-C
demande `tenter` et revalide l'accord direct, avec sa date absolue conservée.

Le schéma de brouillon ne comporte aucun instant calculé : un fragment
temporel doit être présent dans la saisie et appartenir à une grammaire de
durées explicites. Les minutes entières sont résolues une fois par le moteur.
« Demain », un nombre inventé ou une durée non reconnue laisse le délai vide,
avec la consigne publique de le préciser. Un obstacle typé refuse l'accord
entier avec une raison moteur : paiement différé, prêt daté, maintien continu
ou alternative. Aucune réplique PNJ ne peut être produite sur cette voie.
Le schéma de parole fourni au MJ n'expose plus les termes à limite ; une
ancienne réponse datée ouvre un formulaire sans reprendre sa date. Le rejeu
transactionnel d'une parole datée sans choix direct est refusé avant effet.
Le contrat E4 d'exécution reste disponible au formulaire E5.

**Interfaces.** Console et TUI réemploient `AccordTerminal`, désormais
initialisable avec un sous-ensemble de champs admissibles. Le web reçoit
le même brouillon avec l'état public et ouvre son formulaire existant ; sa
date se fige sur l'instant du brouillon. Fermer, corriger, quitter ou annuler
avant U-C n'émet aucune parole. Les scripts de banc utilisent le même
formulaire terminal ; ils contrôlent prestation et délai avant validation.
Recouvrements avec 360/362 : `mj.py`, `paroles.py`, `transactions.py` ;
`propositions.py` du 363 est conservé, sans changement dans cette reprise.

**Épreuves.** Dix méthodes ciblent huile et verrou : vraie boucle libre →
formulaire → consentement, parité de l'état avec E5 et des comptes/paroles,
recharge du monde et du rendu, annulation aux deux étapes, correction de
« demain », champs inconnus, date figée à instant non entier, refus des quatre
clauses, interception et rejet au rejeu d'une ancienne compilation. La page
réelle est exécutée sous Node ; deux parcours de la vraie TUI sont éprouvés.
La première reprise (9 méthodes) n'avait qu'un échec : lecture de « vingt et
une minutes », corrigée dans la grammaire commune. Un lancement antérieur
a été interrompu après découverte accidentelle d'une classe de tests importée.
Les oracles de monde, de parole et de recharge restent inchangés.

Quinze fichiers ciblés/voisins E1–E5, compréhension, consentement, schéma,
paroles/comptes et interfaces sont en vérification, deux travailleurs réduits
au plus. Le schéma a ensuite été resserré pour ne plus annoncer de variante
datée ; E6 et l'invariance du schéma sont vérifiés de nouveau sur ce code final.
Pas de suite complète ni de banc autonome : aucun effet moteur n'est modifié.

**Luna et limites.** Une première passe de 14 scripts, 23 appels, sans erreur
technique ou de recharge, a exercé le raccord. Les huit saisies avec clauses
non portées ont reçu des refus publics sans parole ni contrat. Mais des offres
admissibles ont aussi reçu de faux motifs, et les prestations proposées étaient
souvent datées ou mal typées : ces champs ont été laissés vides. Cette passe
ne valide donc pas l'exactitude de l'orientation et du préremplissage. Le schéma
exposait encore des variantes datées héritées d'E4 ; elles sont maintenant
retirées du brouillon et du protocole de parole libre. Une reprise ciblée de
trois scripts (huile, « demain », verrou) doit vérifier ce schéma final, sans
seconde campagne des quatorze cas. Les signalements lexicaux du banc sur les
listes de choix publics restent à attribuer. L'orientation sémantique peut
rester faillible ; aucune prétention de compréhension universelle du français.

Bruts `C:/Users/msics/donjon/artifacts/e6-364/` : `luna/`, `luna-a-jouer.txt`,
`tests-finaux.json`, puis `tests-schema-final.json`, `luna-schema-final/` et
`sources-finales.json`. Le gardien écrit **`fin-verification-364.json` en
dernier** ; analyser ces résultats avant de conclure la validation. Commande
exacte de la reprise ciblée dans `luna-schema-final-a-jouer.txt`.
