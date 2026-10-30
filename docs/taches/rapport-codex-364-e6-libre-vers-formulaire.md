# Lot 364 — E6 reprise, le libre ouvre le formulaire E5

Branche `codex-e6-libre-date`, base `origin/integration e6555c51` fusionnée
sans rebase (`284f9d38`). Code final `197c0600`, sources finales stables.
**Lot clos, E6 non validé : ne pas fusionner cette réalisation comme E6 acquis.**

Décision ultérieure de l'utilisateur : **fusion partielle autorisée avec ces
limites conservées**. Le [correctif d'intégration 362](rapport-codex-364-integration-362.md)
traite séparément la dépendance du harnais TUI à la connexion du poste.

**Raccord.** `accords_libres` produit un brouillon sans parole, paiement ou
engagement. Destinataire, prestation et prix passent les choix publics E5 ;
les champs non admissibles restent vides. Seule une durée explicite retrouvée
dans les mots préremplit la date, résolue une fois par le moteur. Un repère
inconnu reste à préciser. Un obstacle signalé par Luna reçoit un refus moteur.
Console/TUI et web réemploient leurs formulaires E5 ; validation puis U-C.
Les anciennes compilations datées sont interceptées et leur rejeu sans choix
direct refusé. Le schéma final du MJ n'expose plus de limite calculée.
Effets E4 et contrôles transitoires inchangés. Recouvrements : `mj.py`,
`paroles.py`, `transactions.py` ; `propositions.py` du 363 reste inchangé.

**Tests : 139 méthodes distinctes vertes, 15 fichiers**, zéro échec, erreur
ou saut, 583,898 s avec deux travailleurs réduits. Les 17 tests E6/schéma,
inclus dans les 139, sont rejoués verts sur le code final en 60,273 s.
Huile/verrou : formulaire, correction, refus, annulation, parité E5 des
comptes/paroles/état, date figée, revalidation et rendu après recharge ;
Node et vraie TUI. Un échec de lecture de « vingt et une minutes » a été
corrigé ; une découverte accidentelle de classe importée a été interrompue.
Aucun oracle affaibli. Pendant les voisins, seuls `accords_libres.py`,
`mj.py` et le test E6 ont changé pour resserrer le schéma ; E6/schéma et
la dernière Luna vérifient les empreintes finales. Aucune suite complète.

**Luna : les critères réels ne sont pas tous satisfaits.** Première passe :
14 scripts/23 appels : huit refus publics pour les clauses non portées,
mais aussi des faux refus et des prestations datées ou mal typées. Schéma
resserré, reprise de trois scripts/9 appels, sans seconde campagne complète.
Aucun arrêt, erreur technique ou échec de recharge signalé.

- L'huile dans dix minutes ouvre le formulaire correctement prérempli :
  un appel, accord réel après `valider` puis `tenter`, sans autre appel.
- « Huile demain » est encore faussement classé `paiement_differe` et
  refusé. Le formulaire au délai vide n'arrive qu'après une nouvelle saisie :
  la poursuite automatique du script ne valide pas le critère.
- Le verrou subit aussi des faux refus `paiement_differe` et une tâche
  `lieu:cellier` au lieu du verrouillage ; un formulaire incomplet arrive
  tardivement, sans accord ni parole d'accord.

**Alertes du catalogue.** Seize entités sont signalées lors de l'affichage
des choix, pour chacun des deux scénarios concernés. Sur les copies de
départ, elles ne sont ni visibles, ni dans `connus`, ni dans les souvenirs
visuels ; `_connu_du_joueur` les admet néanmoins. Attribution reproduite
avec les références publiques ; `accords_publics` est identique par AST à
`e6555c51`. Ces alertes préexistantes ne sont pas neutralisées : le fondement
lexical de cette admission et l'absence de fuite restent à examiner.

**Conclusion.** Le raccord et les barrières d'exécution sont éprouvés ;
l'orientation de la phrase et le motif de refus restent incorrects dans les
cas requis. E6 n'est donc pas acquis. Aucun ajustement de prompt, mot-clé ou
cas particulier supplémentaire n'est ajouté pour masquer ces résultats.
Bruts `C:/Users/msics/donjon/artifacts/e6-364/` : tests, deux dossiers Luna,
commandes exactes, `sources-finales.json` et `analyse-cloture.json`.
**`fin-cloture.json` : valide=false**, aucun calcul actif. Branche poussée.
