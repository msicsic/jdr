# Lot 328 — G6, repères de position

29 octobre 2026 — Branche `codex-g6-reperes`, **non fusionnée**, base
`origin/codex-g5-perception c4cd83f` (lot 323). Aucune fusion d'intégration.

**Invariant porté.** La requête typée `reperer` consulte le repère public
courant ou mémorisé et fait écrire sa réponse par le moteur. Elle emploie
l'enveloppe d'action existante, disponible aussi en commande locale, sans
outil, jet, temps écoulé, effet physique ni rotation vers la cible.
`Moteur.executer` recompile le plan depuis sa proposition : ni une justification
inventée ni un texte de plan modifié ne fournissent une position.

`localisation.phrases_positions` formule les axes métriques et les demi-plans
du regard courant, avec une distance euclidienne approximative au décimètre.
Le capteur calcule `distance_metres` comme les axes, depuis la position perçue
ou mémorisée. Le souvenir est explicitement une dernière observation, jamais
une présence actuelle ; dans un autre lieu, seule sa salle connue est donnée.
Sans cases, aucune métrique n'est inventée. `rendu.position` lit la projection
publique, qui masque les noms inconnus ; faute de repère, la non-perception G5
ou un refus moteur répond, sans lecture de la position privée de la cible.

La voie des perceptions canoniques G5 exécute la requête sans contre-revue
d'action ni narration. Les phrases moteur rejoignent les attestations communes :
leur reprise exacte évite l'audit sémantique et est recalculée à l'enregistrement,
y compris si seule la distance a changé. Toute reformulation libre conserve
ses contrôles antérieurs. Publication et conversation utilisent la sauvegarde
existante avant affichage ; aucun registre de positions supplémentaire.

**Vérification locale : 162 tests distincts verts, quinze fichiers.** Le premier
passage (64,665 s) avait un seul échec : l'attendu exact d'un souvenir du test
d'orientation omettait le nouveau champ `distance_metres`. Ajout de la valeur
attendue 1,0, sans changement d'assertion ; les deux fichiers concernés repassent
ensuite **18/18**, 7,809 s. Dix nouveaux tests couvrent le mur du cas 171
(2 m nord, 3 m ouest), Aubin à 1 m, rotation, souvenirs d'objet et de personne
déplacés hors de vue, cible sans repère, identité inconnue, texte de plan
falsifié, reprise exacte périmée, mode sans cases et affaire portée dans le noir.
La vraie console, un MJ simulé sans réseau, l'état du monde, le texte, la scène
et la carte après recharge sont vérifiés ; le disque est relu pendant l'affichage.
Les premiers essais en bac Windows ont échoué sur l'accès aux dossiers temporaires ;
la validation ci-dessus est exécutée hors bac, deux travailleurs réduits au plus.

**Luna : passe unique préparée, validation en attente.** `atelier` et
`noms-dialogue`, `gpt-6-luna`, ChatGPT, effort medium, réflexion libre ; références
historiques `c9459ce` déjà archivées par le 323, lues sans les rejouer. Aucun
gain d'appels ni absence de relance de position revendiqués avant lecture du bilan.
Bruts `C:/Users/msics/donjon/artifacts/g6-328/` : `tests-cibles.json`,
`tests-reprise-contrat.json`, puis `fin-luna-passe.json` attendu, écrit en dernier
même en cas d'échec ; commande exacte dans `luna-a-jouer.txt`.

**Limites et intégration.** Le moteur garantit les réponses typées et les reprises
exactes, pas le routage de toute question libre ni toute position implicitement
exprimée dans une prose française. Aucun audit de cette prose n'est retiré.
Recouvrement avec 326/G17 et 327/G19 : `narration.py`, attestations et rappels à
conserver ensemble à la fusion. La base G5 reste non fusionnée. Ni suite complète
ni banc PNJ ; aucun changement de modèle ou de décision des PNJ.
