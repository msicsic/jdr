# Lot 156 — Ordre des paroles entendues

27 octobre 2026. Branche `codex-rappel-ordre`, non fusionnée ; base `7cc0d16`
(avance rapide demandée depuis `e492272`). **Correction du dossier livrée ;
critère Luna du rappel au tour 5 non atteint.** Aucun fichier réservé ni `main`
modifié, aucun comportement autonome changé.

**Cause exacte.** Le fil `cdaf371`, `soir-noir` p2 n°5 contient bien les mots
« Je suis Ilse » à la révision 2, avant la révision courante 5. Les deux
projections historiques sont cohérentes. L'extraction du lot 112 juge même
le rappel `etablie`, mais la portée mécanique est `contradictoire` : son motif
affirme que 2 survient après 5, puis se contredit lui-même (« en fait l'échange
est antérieur »). Ce n'est ni une perte du texte ni une absence d'extraction.

**Invariant et fonctions.** `narration.echanges_passes` trie les enregistrements
par révision puis minute (ordre stable à égalité), numérote leur ordre
chronologique et donne pour chacun l'antériorité explicite : déjà prononcé et
entendu par Corvus par rapport à la réponse en cours, non encore prononcée,
avec la révision courante. Une parole déjà enregistrée à cette même révision
reste antérieure à la réponse proposée. Aucun lexique de rappels, exception de
nom ou consigne ajoutée. Les preuves exactes du lot 135 et les refus communs
restent actifs ; une paraphrase au discours rapporté ne permet pas une preuve
textuelle exacte, notamment avec changement de personne grammaticale.

**Tests.** 14 ciblés verts, 5,48 s : vraie console et MJ simulé, nom d'Ilse
puis rappel rapporté, autre PNJ et autre parole (« La lune est verte »), faux
rappel refusé puis correction, sauvegarde et recharge. Conversation et parole
finale persistées, positions/possessions/ressources et jets contrôlés ; l'ancien
contenu n'est pas établi comme vérité. Ordre inversé en entrée, même minute et
parole de la révision courante vérifiés sans mutation du monde. Les premiers
essais ont corrigé deux préparations de test (destinataire et référence vocale) ;
l'orientation vers le destinataire est une conséquence normale de la parole.
Le bac à sable refusant les temporaires Python, exécutions autorisées hors bac.
Suite complète unique : **2 179 tests, 246 fichiers, 1 273,205 s**, deux
processus réduits, **deux échecs MiMo historiques `6 != 5`, zéro erreur/ignoré** :
`test_fournisseurs_jeu.test_mimo_correction_avant_action_sur_deux_scenes`
(atelier), `test_restes_fusions.test_mimo_rejets_et_actions_sur_deux_scenes_apres_reprise`.
Mêmes assertions déjà documentées aux lots 135/146 b/152, aucune référence
relancée ni seconde suite. Le bilan global reste non entièrement vert.
Empreintes Relais, 2 h × quatre graines, base `7cc0d16` : **4/4 identiques**,
chronique, mesures et état final complet. Références absentes calculées une
fois et rangées ; aucun rejeu. Un seul calcul réduit, pendant le dernier
fichier actif de la suite, puis seul ; temps non comparés.

**Luna, une passe.** ChatGPT `gpt-6-luna`, medium/libre, copies temporaires,
coffre principal, une exécution réduite. **55 appels / 13 tours MJ**, aucun
repli ni erreur technique/recharge. `soir-noir` : 24/5 = **4,80** appels/tour
(référence p1/p2 : 4,60/4,80), n°5 **7** contre 4/6 ; `soir-voix` : 18/4 =
**4,50**, référence absente du cache `cdaf371` (non rejouée) ; `noms-dialogue` :
13/4 = **3,25**, identique aux deux références. Références relues du cache,
SHA-256 archivés ; charges différentes, aucune conclusion causale de latence.

**Limite observée.** Le nom est donné au n°2 et proposé en rappel au n°5.
L'audit ne rejette plus ce rappel pour sa chronologie ; il extrait en revanche
la décision actuelle « je ne te dirai pas qui je suis » comme un passé jamais
dit et la refuse. Le rappel disparaît de la réponse finale. **N7 n'est donc pas
clos** : l'ordre du dossier est explicite, mais l'extraction et le jugement des
reformulations restent sémantiques. Aucun contournement par mots-clés ou
exemption globale d'une nouvelle parole ; aucune seconde passe Luna.

Bruts : `artifacts/rappel-156/` (fils Luna, références et mesures, preuves,
suite), cause historique également dans `artifacts/cause-156.txt`.
Deux calculs au plus, priorité réduite ; suite à deux processus après Luna.
Aucune clé Git de signature configurée : commit non signé, branche seule poussée.
