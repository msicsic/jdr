# Lot 179 — garde, remise et possession constatées

Branche `codex-garde-rendue-perdue`, **non fusionnée**, base `integration
dd815f4`. Élargissement à `echanges.py`, `social.py` et leurs tests autorisé
par l'orchestrateur ; livraison partielle autorisée. Aucun fichier réservé
au lot 178, scénario historique ou instruction du MJ modifié ; aucun Luna.
Au plus deux travailleurs en priorité réduite. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/garde-179/`.

**Invariant livré.** `esprits.constater_possession` conserve avec le lieu cru
le porteur, le propriétaire, la permission et l'auteur éventuel d'une remise
autorisée. Ces droits sont constatés alors, pas relus à la décision. La vue
et les deux participants de `echanges.remettre`, joueur compris, utilisent
ce contrat. Le mandat de livraison est lu avant sa clôture ; une observation
ultérieure du même porteur ne perd pas cette autorisation de remise.
`agendas._fin_garde` termine sur bien cru remis, rendu à son propriétaire
autre que le gardien, ou perdu aux mains d'un autre sans permission. État et
cause sont sauvegardés ; publication à la sortie du choix, aucune renaissance.
Prêt, garde confiée, position inconnue et révocation distante non apprise ne
terminent rien. Les preuves sont des détails du lieu connu : pas d'entité,
de réveil ni de moyen de recherche supplémentaires ; prix de garde dédupliqué.

**Périmètre livré : remise propre et vue.** L'extension des nouvelles a été
retirée : une ancienne accusation de portage partage l'identité du nouveau
constat et peut masquer sa preuve de droits. La corriger exige de reprendre
le contrat commun des propriétés transmises, pas d'ajouter une exception à
une accusation. Son brouillon brut reste dans `oui-dire-non-livre.patch` ;
`social.py` est inchangé, aucune nouvelle parole automatique n'est ajoutée.

**Épreuves.** Deux biens par cause ; retour vu, remise au propriétaire et
remise mandatée, perte observée, prêt et garde confiée,
ignorance et droits révoqués à distance, preuve hors mémoire, choix interrompu,
laps entier/découpé, prix unique avec pulsion, agenda terminal irréactivable.
Anselme/ballot et clé du coffre éprouvés dans l'auberge en données de tests.
Monde, besace et cause dans la chronique contrôlés après recharge.
**91 ciblés verts au terme des reprises** (les trois tests de projection
repris après correction). Suite complète unique : **2 280 tests, 262 fichiers,
1 242,806 s**, quatre échecs et une erreur bruts. Deux écarts d'oracle de monde
étaient les nouvelles preuves : projection historique enrichie, comparaison
intégrale après recharge conservée. L'erreur de `tenir`, produite pendant
l'ébauche d'ouï-dire, disparaît après retrait, reprise verte. Restent les
deux échecs MiMo historiques `6 != 5`. Aucune seconde suite complète.

**Empreintes, 2 h, quatre scénarios × quatre graines.** Référence
du lot 175 exclusivement relue (`fins-175/empreintes.json` et mondes associés),
aucune nuit de référence rejouée. Du code `101f770` à `dd815f4`, seuls les
dossiers/consignes du joueur et la résolution du sol ont changé, sans effet
sur ces nuits passives (diff conservé dans les bruts). La passe finale sur
`70bf000` donne **16/16** chroniques, mesures, récits, souvenirs et empreintes
physiques identiques, aucun plantage ; **16/16** mondes et rendus identiques
après recharge. Les états complets contiennent les nouvelles preuves : hors
ces ajouts et les empreintes internes des croyances d'agendas, **16/16** sont
identiques. Le premier banc avec l'extension retirée avait trois divergences,
toutes expliquées par trois contrôles neutralisant seulement les nouveaux
constats ; ces essais ne décrivent pas le code livré. Aucun gain de vitesse
revendiqué, aucun temps de référence du cache comparé.

**Limites.** Livraison partielle : l'ouï-dire ne termine pas la garde,
pour les PNJ comme pour le joueur. Celui-ci ne dispose pas non plus de
relations subjectives pour le jet d'adoption des PNJ. Une
mutation hors `echanges.remettre` n'ajoute pas de preuve de remise propre
dans le noir : la possession peut ensuite être constatée par la vue. Ces
voies empêchent de garantir l'invariant intégral. Les anciennes sauvegardes
acquièrent les preuves lors de nouveaux constats, sans reconstruction
omnisciente de transferts passés. A4b garde ses autres limites (suivi vocal,
interposition d'un lieu, départ définitif à décider).

Aucune clé Git de signature configurée : commits non signés. Livraison sur la
branche seule ; ni fusion ni modification de `main`.
