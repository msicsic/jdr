# Lot 336 — Offrir sa protection contre paiement

29 octobre 2026 — `codex-occasion-protection`, **terminée, non fusionnée**.
Base fournie `origin/integration d8769d8`, PC fixe `msi-desktop`.
Moteur/tests `5219a86` inchangés depuis validation, empreintes vérifiées.

**Invariant et fonctions.** `agendas.NAISSANCES` reçoit l'occasion de
protection. `occasion_protection` lit détresse retenue ou cause crue,
pièces connues, force estimée, courage, ambition et disponibilité du
proposant ; celui-ci ne lit aucun besoin, profil ou fonds privés du client.
Le projet `offrir` utilise la proposition, le tarif et l'évaluation communs.
Peur et solvabilité crues sont revalidées au geste. Naissance différée,
plafond et refus retenus restent communs ; le délai seul ne relance pas.

Le service typé `{objet, proteger:true, echeance}` passe par `proposer`
puis `engager` : avance, engagement et agenda `protéger` d'origine
`contrat` dans la même transaction. Proximité du 266, secours et défense
existants ; commencement enregistré au geste hors mémoire courte. Calme
perçu après l'accord ou échéance : service commencé tenu ; mort ou départ
crus : abandon et dette de remboursement commune. Les nouvelles lectures
de responsabilités et obligations entrent dans `_entrees`. Le joueur reçoit
une offre sauvegardée et choisit `accepter offre` ou `refuser offre` ; ni
paiement ni parole implicites. L'acceptation revalide le marché.

**Preuves ciblées.** **210 tests / 21 fichiers : 209 verts, un échec
antérieur**, aucune erreur ni saut, 216,920 s. Les **huit nouveaux tests
sont verts** : Hugues/Anselme à l'auberge et Aubin/Ilse au Relais, offre
autonome, accord, avance, service commencé et fin ; négatifs de peur,
fonds, intérêt, capacité/disponibilité, refus conservé, plan périmé,
fins crues et choix du joueur. Monde, rendu et scène après recharge,
même laps entier/découpé. Placements et savoirs explicites en données
de tests ; aucune donnée de scénario ajoutée au jeu.

L'ancien `test_appel_reconnu_et_course_reels_sur_agenda_seul` attend
Gorm à l'échoppe au lieu de la chambre de la cloche. Même échec sur la
base exacte, hachage 0, fichier 5/6 (5,350 s). Deux captures rechargées :
mêmes positions, lignes, scène et rendu ; différences consignées dans
les empreintes internes et le libellé d'une réponse de service.
**Test laissé rouge, non modifié.** Reprise sans rejouer les acquis :
sources inchangées et traces identiques au témoin, hors chemins absolus.

**Banc 4 h × cinq scénarios × quatre graines : 20/20 conformes.**
Suspects 219 **0 → 0 par nuit**, zéro plantage/usurpation. **20/20
chroniques, récits et souvenirs identiques**. Offres de protection,
acceptations, protections nées et commencées : **0 partout** ; le banc
n'exerce pas le nouveau service, aucune richesse naturelle démontrée.
Marchés toutes sortes : 102 propositions, 31 accords inchangés.
À expliquer 43 → 43, dérives ouvertes 436 → 436, vols tentés 3 → 3.
Recherche : 43 762 → 43 767, neuves 22 355 → 22 360 ; aucune comparaison
de vitesse. Empreinte d'état complet identique dans 4/20 nuits ; dans
le relevé final, seuls changent seize `projets[].croyances` de Brune/Odon.
Référence exacte absente : vingt nuits calculées/rangées une fois,
aucune référence disponible rejouée. Deux travailleurs réduits, ni Luna
ni suite complète. **`verification-2/fin.json ok=true`, code 0,
885,118 s**, premier échec conservé ; aucun calcul actif, branche poussée.

**Limites et livraison.** Une occasion par client ; renaissance après
contrat terminé non livrée. Perte du signe sans calme constaté : aucune
fin inventée. Remboursement dû, sans remise automatique. Suivi vocal
335 distinct ; aucune garantie universelle sur les boucles. Fichiers
communs au 333 : `agendas.py`, `pnj.py` ; au 335 : ces deux fichiers et
`planification.py`, plus documentation commune `docs/etat-dev.md`.
Bruts `C:/Users/msics/donjon/artifacts/occasion-336/` : `verification-1/`,
`diagnostic/`, `verification-2/` et `analyse-cloture.json`.
