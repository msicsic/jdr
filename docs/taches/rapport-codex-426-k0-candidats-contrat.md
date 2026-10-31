# Lot 426 — K0, candidats de contrat déterministes

Branche `codex-k0-candidats-contrat`, base `integration` **`a874d646`**.

**Invariant.** Une suggestion est un brouillon public, jamais un accord, une
réplique entendue, un paiement ou un engagement. `dialogues.candidats_contrat`
parcourt les interlocuteurs perçus et les prestations publiques d'E5 dans un
ordre canonique ; il ne lit pas leurs besoins, pulsions ou préférences pour
choisir les termes ou le prix. Les parts proposées portent sur des ressources
actuellement visibles et à une possession constatée ou déjà mémorisée ; les
tâches sur un défaut visible de flamme ou de verrouillage. Un objet vu au sol
sans preuve de possession ne révèle donc pas son propriétaire par suggestion.

**Admission commune.** `echanges.candidat_proposition` travaille exclusivement
sur copie : forme et connaissances (`propositions.verifier`), contact, droits,
fonds, quantité, disponibilité promise, doublon, livraison ou devis de tâche.
Les droits et ressources sont extraits sans changement de comportement dans
`moyens_proposition`, également appelé par `proposer`. Les refus d'admission
écartent le candidat. Aucun jet social ni appel au modèle dans la génération.
Le jugement du PNJ reste celui de la soumission ordinaire ; une suggestion
peut être refusée. Le prix initial est le prix typé d'une part, ou la convention
d'une pièce pour une tâche ; il n'est pas calculé sur les dispositions privées.

**Interfaces.** La projection `accords_publics` transporte les mêmes suggestions
au web, à la console et à la TUI. Dans `accord`, `suggestion N` préremplit le
formulaire terminal ; le web fournit un bouton par suggestion. Le destinataire,
la prestation, le prix et l'absence de limite restent modifiables. Seul
« valider / Préparer cet accord », puis la confirmation existante, soumettent
le descripteur U-D `accord`. Sa revalidation n'a pas besoin de régénérer les
suggestions. Le formulaire manuel et le raccord libre restent disponibles.

**Vérification.** **7/7 tests K0 finaux verts**, 181,912 s, sans ignoré
(`k0-public.json`). Tests voisins
marché, U-D, E5 et comptes en cours (`voisins.json`, écrit en dernier) ; le
fichier U-D est déjà vert (10 tests). Cas réel : planches d'Aubin au Relais ; autre
ressource : huile d'Odile à l'auberge ; autre famille : verrouillage du
garde-manger. Les parcours console et callbacks web réels comparent les termes,
l'état après accord et les vues après recharge. Couverture du refus du PNJ,
de l'annulation, des fonds perdus, de l'épuisement, des droits, du départ,
des doublons, d'une tâche sans moyen, des identités publiques, du propriétaire
inconnu et du besoin privé inconnu. Aucun banc
PNJ, aucune suite complète ni passe Luna.
Référence finale sur copies (`mesures-public.json`) : 3/2/2 suggestions au
Relais/huile/tâche ; génération seule 0,623/2,371/0,836 s sous charge,
projection E5 séparée, zéro effet et zéro modèle ; aucun gain général annoncé.

**Portée et limites.** Référence volontairement bornée au formulaire E5 : parts
contre pièces présentes, allumage/entretien d'une flamme faible et verrouillage.
Pas d'énumération exhaustive des marchés, de troc, de conversion d'un besoin
social en clause, d'offre spontanée ni de nouvelle échéance. Les objets
indivisibles et les autres tâches restent accessibles par leurs voies actuelles.
Le générateur ne garantit jamais l'accord ni la fidélité de toute saisie libre.

Bruts : `C:/Users/msics/donjon/artifacts/k0-candidats-426/`.
Clôture détachée : `fin.json` écrit après `voisins.json`, avec les deux bilans
et le journal voisin. **Vérification voisine encore en cours à la poussée** ;
reprendre ce lot à sa fin avant de le déclarer terminé.
Fusion et vérification complète laissées au superviseur.
