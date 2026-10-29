# Lot 336 — Offrir sa protection contre paiement

29 octobre 2026 — `codex-occasion-protection`, **non fusionnée, vérification en cours**.
Base fournie `origin/integration d8769d8`. PC fixe `msi-desktop`.

**Invariant et fonctions.** La table `agendas.NAISSANCES` reçoit l'occasion de
protection. `occasion_protection` lit une détresse retenue ou une cause crue,
des pièces connues, la force estimée, le courage, l'ambition et la disponibilité
du proposant. Celui-ci ne lit aucun profil, besoin ni fonds privés du client.
Le projet `offrir` présente une proposition ordinaire, au tarif commun des
tâches. `offre_sensee` et l'évaluation commune comparent le prix et la valeur
du secours ; un ancien plan revalide peur et solvabilité crues à l'exécution.
La naissance reste différée, avec le plafond commun des agendas.

Le service typé `{objet, proteger:true, echeance}` passe par `proposer` puis
`engager` : avance, tâche et agenda `protéger` d'origine `contrat` sont admis
dans la même transaction. L'engagement utilise la proximité commune ; les
secours et la défense lisent la responsabilité existante. Le commencement
est enregistré au geste, hors mémoire courte. Un calme perçu après l'accord
ou l'échéance clôt le service commencé ; mort ou départ crus l'abandonnent
avec la dette de remboursement commune. Un refus reste dans le mécanisme
commun des propositions, sans nouvel essai par le seul délai.

Le joueur reçoit une offre sauvegardée, visible dans ses interlocuteurs,
et choisit `accepter offre` ou `refuser offre`. Ni paiement ni réplique ne
lui sont prêtés. Une acceptation revalide contact, moyens, prix et échéance.
Les identités inconnues restent désignées par leur référence perceptible.
Les nouvelles obligations et responsabilités entrent dans `_entrees`.

**Preuves acquises et calcul demandé.** Consolidation : **210 tests / 21 fichiers,
209 verts, un échec antérieur**, 216,920 s ; aucune erreur ni saut.
Les huit nouveaux tests sont verts. Auberge
Hugues/Anselme et Relais Aubin/Ilse : offre autonome, accord, paiement,
service commencé, fin sur calme, monde/rendu/scène rechargés et même laps
entier/découpé. Négatifs : peur, fonds, intérêt, courage, disponibilité,
refus conservé ; fins sur échéance, mort et départ crus, plan périmé,
acceptation/refus du joueur sans parole ni paiement implicites.
Les scènes sont des épreuves de mécanisme avec
placements et savoirs explicites en données de tests, sans donnée de scénario
ajoutée au jeu. Aucun gain en nuit naturelle encore mesuré.

L'échec `test_appel_reconnu_et_course_reels_sur_agenda_seul` donne Gorm
en `chambre_cloche` à six minutes, contre `echoppe` attendu. Même échec
sur la copie exacte de `d8769d8`, au même hachage 0 ; son fichier donne
5/6 verts sur la base (5,350 s). Deux captures monde/rendu/scène rechargées :
mêmes positions, lignes et observations au joueur. Différences complètes
consignées : empreintes `agendas[].croyances` et libellé d'une réponse de
service dans le registre des paroles. **Le test reste rouge**, non modifié.
Moteur et tests `5219a86` inchangés, empreintes contrôlées avant reprise.

`tools/valider_occasion_336.py` consolide **21 fichiers ciblés**, puis compare
4 h × cinq scénarios × quatre graines à la base exacte : références déjà
cachées relues, absentes calculées une fois ; suspects 219 par nuit,
plantages/usurpations, offres, accords et protections nées/commencées.
Deux travailleurs réduits au plus ; ni Luna ni suite complète.
Bruts `C:/Users/msics/donjon/artifacts/occasion-336/`, calcul final sous
`verification-1/fin.json` conserve l'échec initial avant tout banc ; reprise
sous `verification-2/`, fin attendue `verification-2/fin.json`, écrite en
dernier même en cas d'échec. Les tests acquis ne sont pas rejoués : le
lanceur exige sources inchangées et traces identiques au témoin de base,
hors chemins absolus, sans exception par nom de test.
**Banc à relire avant clôture ; réserve du test antérieur conservée.**

**Limites et recouvrements.** Le projet conserve une seule occasion par
client ; la renaissance après un contrat terminé n'est pas livrée. La peur
perdue de vue n'est pas un danger passé : il faut un calme constaté ou la
fin explicite. Le remboursement est une dette commune, pas une remise
automatique de pièces. Le suivi vocal du lot 335 reste distinct : ce lot
utilise la proximité existante du 266 pour le service. Pas de garantie
universelle sur les boucles. Fichiers communs au 333 : `agendas.py`, `pnj.py` ;
au 335 : `agendas.py`, `planification.py`, `pnj.py` ; documentation commune
`docs/etat-dev.md`. Aucun code des branches voisines importé.
