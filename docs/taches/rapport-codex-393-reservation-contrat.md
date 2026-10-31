# Lot 393 — Réservation et livraison du même contrat

31 octobre 2026, PC fixe. Branche `codex-reservation-contrat`, base
`origin/integration ca0fc1f0`. Bruts :
`C:/Users/msics/donjon/artifacts/reservation-contrat-393/`. Code `89547197`,
branche poussée, fusion au superviseur. Vérification close, aucun calcul attendu.

**Invariant et cause.** La commission d'Ilse pour livrer les crochets à Brune
était acceptée. Leur acquisition auprès de Gorm créait ensuite le prêt et son
obligation de restitution. `agendas.moyens_promis` excluait bien la commission
revalidée, mais réservait le même bien entier pour cette restitution accessoire :
le devis devenait impossible, Ilse abandonnait et rendait les crochets à Gorm.
Reproduction avant correction : `diagnostic-avant.txt`, un échec et une erreur
sur les deux fichiers du brief (`tests-avant.json`).

**Correction commune.** `moyens_promis` identifie l'engagement revalidé dans le
registre actif. Pour son transport typé (`remettre` ou `lieu`), la restitution
du même bien inscrite ensuite ne constitue pas une deuxième charge. L'ordre
d'inscription, conservé à la sauvegarde et ajouté en fin par `agendas.prendre`,
exclut un prêt préexistant : un nouveau transport ne peut pas se l'attribuer.
Toute autre réservation continue de compter. L'obligation de retour, la
propriété et les permissions restent enregistrées selon leurs contrats usuels.
Aucun nouveau registre, prompt ni format de sauvegarde.

**Placement du test de pureté.** Le destinataire caché est placé sur
`min(geometrie.cases(salle))`, sans rafraîchir les croyances. Preuve :
[`cases`](../../donjon/geometrie.py) dérive exactement les cases « . » du sol ;
[`spatial.verifier`](../../donjon/spatial.py) exige l'appartenance à cet ensemble,
également lors de `Monde.copier`. L'ancienne case constante `(1, 1)` n'y
appartenait pas dans toutes les salles. Les assertions de devis identique et
d'absence d'empêchement restent intactes ; recharge, rendu et absence de mutation
après devis sont aussi contrôlés dans chaque salle des deux scènes.

**Cas réel et contre-épreuves.** Crochets puis marteau : commission, acquisition,
livraison et journal moteur, état complet, scène perçue et rendu après recharge ;
le contrat est tenu, le retour reste unique, aucune permission d'usage du
destinataire n'est inventée. Remise et transport vers un lieu : devis revalidé
possible après emprunt, nouvelle commission concurrente impossible, même après
recharge. Supprimer le transport initial ne permet pas à un nouveau devis de
s'approprier son prêt. Les tests du 377 gardent la part de Mireille pour Tilo,
les parts libres des stocks et le refus des doubles promesses.

**Mesures.** **68/70 verts**, six fichiers prescrits, 94,2 s (`tests-final.json`) ;
les deux rouges restants sont attribués ci-dessous, aucun nouvel échec.
**Banc rapide terminé : 8/8 nuits**, Relais/crue, quatre heures, graines
1985/7/42/2024 : aucun plantage, zéro usurpation et zéro bascule contradictoire.
Maximum de passages par PNJ et heure : Relais 11, crue 43 (Gorm, graine 42,
première heure) ; avertissements redits : respectivement 5 et 1. Les déplacements
de Gorm traversent cinq salles, avec évacuation, fourniture et réactions aux bruits ;
ces compteurs ne prouvent pas l'absence générale de boucles. Aucun prêt ni commission
dans ces nuits : la preuve de livraison vient des tests ciblés. Pas de comparaison
de référence ni de conclusion de coût. Bruts `banc-relais.json`, `banc-crue.json` ;
`analyse-cloture.json` synthétise les observations. `fin-verification.json` garde
les codes bruts : tests=1 (seuls rouges de base), bancs=0, erreur=null, succès=true ;
237,2 s pour le lanceur entier, deux travailleurs réduits au plus. Ni suite complète
ni Luna. Premier début de banc arrêté avant résultat pour renforcer la contre-épreuve ;
seul le banc final est retenu.

**Limites attribuées.** Deux méthodes de `test_promesses.DonLocalTests` restent
rouges : `test_le_don_de_la_cloche_aboutit_sans_appel_au_modele` (clé propriétaire
absente) et `test_un_autre_objet_a_un_autre_personnage` (couteau encore au joueur).
Les mêmes erreurs et assertions sont reproduites en restaurant en mémoire la
fonction `moyens_promis` de `ca0fc1f0`, seul code du jeu modifié
(`promesses-base.json`, 12/14). Leurs tests ne sont pas modifiés. Le lot ne
garantit pas la planification temporelle globale des prêts ou engagements ; une
restitution déjà inscrite avant un nouveau transport reste une charge opposable.
