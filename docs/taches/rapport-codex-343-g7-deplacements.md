# Lot 343 — G7, déplacements résolus

30 octobre 2026. Branche `codex-g7-deplacements`, base exacte `dc6da62`,
**non fusionnée ; code et tests ciblés validés, mesures détachées en cours**.

Le moteur conserve maintenant chaque mouvement réellement accompli du joueur :
acteur, opération, quantité, unité, direction et bornes en dixièmes de seconde.
`deplacements.clore` construit le cumul depuis cette trace, sans analyser les
lignes de texte. Les directions successives restent ordonnées ; un changement
de direction ne devient pas une marche droite. Les passages sans métrique
restent des passages, sans distance inventée. Les sons conservent leurs lignes,
leur ordre et leur multiplicité. Le journal reçoit la trace et le rendu avant
la sauvegarde et l'affichage par la boucle commune G4.

`Moteur._appliquer` relève les mutations physiques réussies ; la fin d'étape
borne leur durée. Le traînage différé est relevé à son échéance dans
`tenir.finir_trajet`, avec sa durée commune, sans changer le contrat des gestes
sauvegardés. Le clic transmet un identifiant de trajet et les directions encore
choisies. Chaque pas reste indépendant et revalidé ; le moteur ne cumule deux
commandes que si elles continuent immédiatement le même trajet. Une arrivée de
personne, un refus, Échap ou une autre commande gardent leurs interruptions.
Le dernier état publié indique les étapes encore non exécutées. La fuite
conserve aussi son reliquat. Les attestations du lot 95 utilisent exactement
`deplacements.phrases` ; les reformulations libres gardent leurs audits.

**Vérification : 234 tests distincts, 17 fichiers, tous verts**, sans saut,
453,652 s cumulées des fichiers retenus. G4, U-D, U-T, vraie sonde JavaScript du
clic, ponts web/TUI, moteur, opérations, temps, repères et narration. Les scènes
contrôlent monde complet, texte enregistré, scène et carte après recharge ;
publication après sauvegarde et reprise exacte sans audit. Cas négatifs : mur
avant le premier pas, trajet mal formé, faisabilité sans exécution, faux total,
nouveau clic et trois pas arrêtés au deuxième. Traînage Relais/auberge et passage
sous obstacle couverts. Les premiers essais rouges sont conservés ; un ajout
initial au dossier de traînage, incompatible avec son schéma, a été retiré.

Le script réel `force-4c-fuir` accomplit **trois pas sur cette base**, contre
les deux du diagnostic historique 171 : nord, nord-ouest, ouest. Le test vérifie
la route réellement calculée ; un départ voisin accomplit deux pas. Les sons à
l'ouest ne comptent jamais comme mouvements du joueur. Aucun changement des
choix, positions ou durées des PNJ n'est recherché ou revendiqué.

**Mesures en cours** : empreintes 2 h, Relais/auberge, graines 1985/7/42/2024,
référence exacte `dc6da62` avec cache commun ; les références absentes sont
calculées et rangées une fois par l'outil. Puis Luna, une passe seulement,
`force-4c-fuir` et `force-4f-trainer`. Les deux parties historiques `cdaf371`
ont été trouvées dans le cache avant lancement ; aucune relance de cette
référence n'est nécessaire. Aucune conclusion chiffrée sur ces mesures avant
lecture de leur fin. Deux travailleurs au plus, priorité réduite, ni suite
complète ni banc long d'intégration.

Bruts : `C:/Users/msics/donjon/artifacts/g7-343/` ; résultats de tests conservés,
`empreintes.json`, `empreintes.log`, `luna.log`, dossier `luna/` et
**`fin-validation.json` écrit en dernier**. Rapport à clore après analyse de ce
fichier. Recouvrements : `narration.py` avec 341 ; documentation avec tous les
lots. Aucun fichier moteur commun identifié avec les correctifs annoncés de
338/342 ; `jeu.py` (325) et `transactions.py` intacts. Le lot n'étend pas la
preuve exacte aux paraphrases de nombres ou aux cumuls des PNJ.
