# Lot 277 — demander l'allumage d'un foyer fixe pour soi

29 octobre 2026, branche `codex-allumer-pour-soi`, **non fusionnée**, base
`1852d6e` (intégration avec 275). **Vérification en cours : ne pas fusionner
avant lecture de `artifacts/allumer-277/correction/fin.json` du dépôt principal.**

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

**Invariant et raccord.** Un foyer mécanique (`foyer=True`) fixe cru éteint et chargé, hors de l'eau
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
scènes d'auteur au hameau pour le brasero et le poêle du guet, torche de Maël
mise à disposition de Gorm, accord sans effet immédiat, déplacement/allumage/chauffage
réels ; comparaison de huit minutes en bloc et découpées, monde/rendu/scène
après recharge. Contre-épreuves : flamme crue éteinte, charge absente,
lieu cru sous l'eau, position réelle cachée, refus d'impossibilité retenu
sans redemande par délai, travail payé après refus gratuit, parole du joueur.

**Instruction des échecs de `d306370`.** La passe détachée a arrêté le banc :
314 tests, deux échecs historiques et huit erreurs de fixture. Les erreurs
proviennent de `foyer=False`, donnée interdite par le schéma : le champ
est retiré pour les autres sources de la scène. Les deux fichiers
historiques passent sur une copie exacte de `1852d6e` : **8/8, 96,496 s**.
Ils échouent donc à cause du lot, sans dette préexistante trouvée.
Le générateur visait tous les luminaires fixes au lieu des foyers mécaniques :
Rémy, faim, explore lampe/chandelle (mine/480 : 503 → 567 états,
2 383 → 2 697 successeurs) ; Bram sollicite les luminaires, grossit la
chronique bornée à 300 et en évacue son ancien appel (1 → 0), sans nouvel
appel. Le témoin conserve l'appel (1 → 1). Admission corrigée sur la
mécanique `foyer`, sans nom, scénario ou motif de besoin. **8/8 historiques
verts ensuite, 100,469 s ; les six empreintes attendues sont conservées.**
Monde/rendu/scène des rejeux de Bram identiques après recharge ; monde final
du corrigé identique au témoin `1852d6e`.

Les scènes propres au lot sont précisées sans retirer leurs assertions :
besoin de chaleur isolé en lumière naturelle, permission de Maël sans
engagement concurrent de restitution, réserve privée inconnue d'Aubin,
foyer réellement vide dans l'épreuve sans combustible ; joueur au contact,
foyer connu et contenu `proposition` existant pour sa demande de travail.
Les prêts ordinaires peuvent légitimement faire passer leur restitution
avant ce service : aucun ordre de priorité du destinataire n'est changé.
**Les huit tests propres au lot passent : 31,031 s**, accords gratuits et
payés, parole du joueur, chaleur réelle, recharges et découpage inclus.

**Mesures finales en attente.** Reprise détachée des 34 fichiers concernés,
puis banc 4 h, cinq scénarios × quatre graines ; référence `1852d6e` en
cache ou calculée une fois. Deux travailleurs réduits au plus. Le lanceur
s'arrête avant le banc si les tests échouent ; `fin.json` est écrit en dernier.
Suspects 219 par nuit, violences et S/F/D (`cats` du lot 183), sans comparaison
de temps entre campagnes. Ni suite complète ni Luna. L'ancien résultat
`fin.json` négatif reste conservé ; reprise dans `correction/`.

**Limites.** Validation finale et absence de hausse des suspects non encore
établies ; aucune réussite universelle du service annoncée. Les captures
historiques restent impossibles pour Gorm ; les scènes de réussite sont
des scènes d'auteur avec combustible disponible. Bruts et lanceur dans
`C:/Users/msics/donjon/artifacts/allumer-277/`.
