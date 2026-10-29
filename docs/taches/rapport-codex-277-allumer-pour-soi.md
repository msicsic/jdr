# Lot 277 — demander l'allumage d'un foyer fixe pour soi

29 octobre 2026, branche `codex-allumer-pour-soi`, **non fusionnée**, base
`1852d6e` (intégration avec 275). **Vérification en cours : ne pas fusionner
avant lecture de `artifacts/allumer-277/fin.json` du dépôt principal.**

**Diagnostic préalable, sans modification du moteur.** Captures 269
`choix-369211` et `choix-391200` : la condition `allume` est admise pour
le brasero et le poêle du guet ; aucune offre `confier`/`engager` n'est
produite dans les recherches chaleur, aucun refus de cette tâche n'est
retenu. Aubin n'a pas de poste gardé : l'aide gratuite existante ne s'ouvre
pas ; les tâches payées ne sont offertes que pour une pulsion explicitement
visée. Gorm est cru porter la torche allumée. **Son devis est néanmoins
impossible sur les deux captures et pour les deux foyers**, même avec un
jet de 20 : le recours manquant ne garantit donc pas d'éviter le coup.
Monde, rendu et scène des deux captures identiques après recharge.

**Invariant et raccord.** Un foyer fixe cru éteint et chargé, hors de l'eau
attendue, utilisable sans faute, peut ouvrir une demande à qui est cru
porter une flamme, lorsque le demandeur n'en porte aucune. Les lieux des
tiers et les flammes proviennent des croyances. `confier` et `engager`
conservent leurs devis, jugement, coût, refus et exécution ordinaires.
La projection sert à comparer les moyens ; le plan exécutable s'arrête
à la demande et attend ensuite le travail accepté. L'accord ne change ni
le feu ni la position du destinataire. La parole du joueur emploie la voie
de service déjà existante, sans changement de prompt ni appel à Luna.

Fonctions touchées : `planification.Vue.__init__` (une aide acceptée prime
un refus antérieur), `gestes` (raccord du recours), `_aide_sur_place`
(extraction sans changer ses conditions d'ouverture), `_confier_tache`
(demande et attente communes), `_allumer_pour_soi` (admission sur les
croyances), `_engager` (filtre facultatif des interlocuteurs).
`echanges.engager` et `confier` partagent `_retenir_aide` : l'attente du
bénéficiaire et sa durée physique sont enregistrées pour le travail gratuit
comme payé. Aucun changement à `agendas.py`, `signes.py` ou `deliberation.py`.

**Épreuves préparées.** Capture historique 615 conservée en fixture ;
scènes d'auteur au hameau pour le brasero et le poêle du guet, torche prêtée
par un tiers, accord sans effet immédiat, déplacement/allumage/chauffage
réels ; comparaison de huit minutes en bloc et découpées, monde/rendu/scène
après recharge. Contre-épreuves : flamme crue éteinte, charge absente,
lieu cru sous l'eau, position réelle cachée, refus d'impossibilité retenu
sans redemande par délai, travail payé après refus gratuit, parole du joueur.

**Mesures en attente.** Première sélection de vingt fichiers lancée à
priorité réduite, deux travailleurs ; reprise détachée avec sélection des
appelants directs et fichiers concernés sur le code final, puis banc
4 h, cinq scénarios × quatre graines, référence `1852d6e` réutilisée en
cache ou calculée une fois. Le lanceur s'arrête avant le banc si les tests
échouent ; `fin.json` est écrit en dernier. Il relève les suspects 219 par
nuit, les violences et S/F/D avec `cats` du lot 183, sans comparer de temps
issus de campagnes distinctes. Ni suite complète ni Luna.

**Limites.** Validation finale et absence de hausse des suspects non encore
établies ; aucune réussite universelle du service annoncée. Les captures
historiques restent impossibles pour Gorm ; les scènes de réussite sont
des scènes d'auteur avec combustible disponible. Bruts et lanceur dans
`C:/Users/msics/donjon/artifacts/allumer-277/`.
