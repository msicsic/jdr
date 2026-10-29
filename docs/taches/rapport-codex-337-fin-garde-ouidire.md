# Lot 337 — fin de garde apprise par ouï-dire

Branche `codex-fin-garde-ouidire`, **non fusionnée**, base `integration
9bef3f6`, code/tests `e2822a1`. **Lot clos non validé : le critère du banc
219 n'est pas acquis.** Branche poussée, aucun calcul actif. Ni Luna ni
suite complète. Bruts `C:/Users/msics/donjon/artifacts/garde-337/`.

**Contrat livré et testé.** Les nouvelles communes transmettent ensemble
lieu, porteur, propriétaire, permission et remise autorisée photographiés
au constat. L'identité `[objet, lieu, possession]` diffère d'une accusation
de portage ; celle-ci ne masque plus les droits et ne peut remplacer une
preuve reçue plus récente, ou riche à date égale. Une autre date, case ou
source ne répète pas le même droit ; un changement de droits le rouvre.
`recevoir`/`_adopter` gardent date d'observation, source `dit:`, confiance
et dégradation par relais, sans lire les droits réels à la réception.
Une nouvelle devenue fausse peut être crue ; les preuves propres récentes
ou à date égale priment. Aucun nouveau geste de parole : les candidats des
confidences existantes sont enrichis, avec un effet mesuré sur leur nombre.

`social.faits_dits`, `reviser_dits`, `_constats`, `_meme_constat`,
`_lieu_dit`, `phrase`, `_apprendre_lieu` assurent ce raccord.
`esprits.constater_fin_objet` transmet aussi destruction/consommation et
leur désignation observée, conservée après retrait des restes. Une fin
`None` datée empêche une ancienne destruction racontée de revenir après
réparation. `agendas.py` et `biens.capacites_crues` lisent sa valeur.
Publication différée, interruption et irréversibilité restent communes.
Responsabilité/prix et propriétaire projeté sont déjà dans `_entrees` ;
preuve négative sans nouveau moyen normalisée dans les empreintes.

**Tests. 196/196, quinze fichiers**, zéro échec/erreur/saut, 132,735 s ;
quatorze nouveaux tests. Perte au Relais malgré une ancienne accusation,
restitution à l'auberge, destruction/consommation, retrait des restes,
doute, preuve propre, réparation, droits changés à distance, fausse
nouvelle, relais à 0,56, absence de répétition, publication différée et
interruption ; monde/rendu/scène rechargés, laps entier/découpé, y compris
confidence pendant le laps. Quatre scènes voisines déclarent l'inventaire
initial déjà partagé, assertions conservées. Le test historique de Rémy
repasse inchangé après correction du lecteur de capacités. Échecs initiaux
et reprises conservés ; aucun cumul de passes dans les 196 tests.

**Banc : 19/20 nuits conformes**, cinq scénarios × quatre graines × 4 h.
Aucun plantage ni usurpation. Suspects 219 **0 → 0 sur dix-neuf nuits,
0 → 1 sur crue/7** : Gorm vise le brasero à t=69945, rejoint Aubin à
t=70200, puis reprend le brasero à t=70426 (écart 0,38 min). Aucun delta
externe reconnu entre abandon et retour, aucune preuve admise par l'audit.
La chronique enregistre les retrouvailles à t=70426 ; le détecteur ne
certifie actuellement cette clôture que pour une décision `attendre`,
contre `rejoindre` ici. **Piste d'explication, pas un reclassement** : le
suspect brut reste conservé, aucune règle d'audit ni oracle modifié.

Constats confiés **148 → 522**, avertissements redits **8 → 27**, bascules
**0 → 2**, à expliquer **43 → 51**, dérives ouvertes **436 → 410**, vols
tentés **3 → 4**. Aucun gain général revendiqué. Aucune fin d'agenda
« bien cru … » dans ces nuits : la voie est prouvée par les tests, pas
exercée par le banc passif. Vingt références exactes absentes calculées
et rangées une fois, aucune disponible relancée. Deux travailleurs réduits,
tests réutilisés après contrôle des empreintes. `banc-final/fin.json` :
**ok=false**, 1 149,189 s, écrit en dernier ; échec conservé.

**Limites.** PNJ seulement : relations subjectives du joueur absentes.
Pas de reconstruction omnisciente d'anciens droits ; un ancien constat
sans désignation ne se formule pas après retrait des restes. La hausse des
confidences et l'alerte 219 restent à instruire avant validation/fusion.
Recouvrements 335/336 : `agendas.py`, `planification.py`, `docs/etat-dev.md`.
Pas de garantie universelle contre les boucles. Code/tests inchangés depuis
validation ; analyse conservée dans `analyse-cloture.json`.
