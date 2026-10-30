# Lot 350 — E2, réalisation datée

Branche `codex-e2-realisation-datee`, base d'intégration `59e65f8`, PC fixe (`msi-desktop`).

**Invariant.** Pour une prestation ponctuelle portant la référence E1, le moteur conserve
une issue unique : obligation/version, titulaire, réalisation éventuelle en dixièmes absolus,
verdict et clôture. Une réalisation à T est à temps ; sans réalisation, la prestation est
close à T+1 dixième. Un geste volontaire ultérieur ne réécrit pas cette histoire. La limite
remplace le maximum générique, sans délai de grâce ni sanction supplémentaire.

`agendas` photographie les propriétés physiques autour des effets joueur et PNJ ; la
photographie ne vaut pas perception. Les remises et services utilisent leur événement
explicite dans `echanges`, les autres tâches un changement réel du résultat promis.
Le suivi inclut les déplacements de `pnj.agir`, les gestes élémentaires et le raccord
joueur existant. Un état seulement trouvé vrai ne reçoit aucune date rétroactive.
L'ordonnanceur traite l'expiration au dixième, indépendamment du découpage du laps,
et arrête le plan adopté lorsque sa prestation n'est plus due. La référence et l'issue
sont validées à la recharge, avec un `attendu` précis ; leur stockage reste privé à `agendas`.

**Comptes et connaissance.** Une clôture tardive déclenche une seule fois le remboursement
existant. `biens.rembourser(..., informer=False)` permet d'inscrire la dette réelle sans
créer de créance connue, de réclamation autonome ni d'affichage comptable chez un bénéficiaire
non informé. Une remise effective ou une réponse locale à sa réclamation fournit la preuve.
Les souvenirs sociaux suivent les constats et les suites parlées existants ; l'archive
mécanique n'applique aucune réaction relationnelle au bénéficiaire distant.

**Épreuves.** 104 tests distincts verts dans 14 fichiers ciblés/voisins : première passe finale
88 tests (88,142 s), complément 17 tests (15,969 s), puis connaissance et propositions ordinaires
25 tests (37,868 s), en dédupliquant les reprises. Douze tests E2 couvrent
l'huile d'Odile remise à Joss et le verrouillage payé du garde-manger à T−1/T/T+1, remboursement
unique, constat tardif d'un effet de tiers, état trouvé vrai sans preuve d'effet, arrêt d'un plan
périmé, délai supérieur au maximum générique, promesse du joueur, silence sans preuve et corruption de sauvegarde.
Le parcours réel des planches d'Aubin passe par entrée, jugement et paiement, puis réalisation
et recharge ; les parcours comparent monde, scène perçue, rendu, comptes et mots. L'expiration
en bloc/découpée clôt au même instant 101 ; la livraison du Relais donne le même monde complet
et les mêmes paroles en bloc/découpée. Priorité réduite, deux processus au plus.

**Neutralité.** Empreintes 2 h, quatre graines (1985/7/42/2024), Relais/auberge/mine :
**12/12 nuits identiques** à la base exacte `59e65f8` (chroniques, mesures, état final complet),
zéro plantage. Les audits sont identiques : zéro avis non justifié, dix avis à expliquer déjà
sur la base. Références manquantes calculées une fois et rangées au cache commun ; aucune
référence rejouée. Lanceur détaché terminé avec code 0 (`fin-empreintes.json`). Le dernier
resserrement du constat négatif du joueur ne lit que les issues datées, absentes de ces scénarios.
Bruts : `C:\Users\msics\donjon\artifacts\e2-350\` (`tests.json`, `tests-complements.json`
et journaux, `tests-connaissance.json`, empreintes). Aucune comparaison de temps CPU entre cache et calcul courant.

**Limites.** Socle interne : aucun appelant de jeu ne crée encore une limite ; aucun schéma,
prompt ou rendu nouveau. Seules les prestations ponctuelles du périmètre sont datables ;
prêt, protection durable, mandat et paiement différé restent hors de cette clause.
Une clôture sans réalisation porte `realisation=None` : une remise volontaire postérieure
est un autre acte, pas une réalisation historique du contrat clos. Les mutations brutes de
fixtures ne sont pas des effets moteur et ne fournissent pas une date. Ni suite complète,
ni Luna, ni banc long lancés. Les lots E3 à E6 restent nécessaires au contrat jouable.
Les croyances restent datées à la minute : un constat négatif du joueur dans la minute
de la limite attend une preuve ultérieure suffisamment datée ; il n'est pas antidaté.
