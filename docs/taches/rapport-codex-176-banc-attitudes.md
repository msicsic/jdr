# Lot 176 — les attitudes racontées ont un appui perçu

Branche `codex-banc-attitudes`, non fusionnée, base intégration `3842aef`.

Le contrat de la section 8 de `plan-relations.md` n'était pas entièrement
implémenté : le rapport narratif ne relevait aucune attribution d'attitude et
ne contrôlait aucun identifiant de signe ou d'impression. Une réponse classée
comme ambiance pouvait donc passer sans appui. Ce constat porte sur le
contrat du rapport, sans mesure du comportement réel de Luna. Le diagnostic
comparé sur Ilse et Gorm avec auditeur simulé est conservé dans
`diagnostic-contrat.json` : acceptation par la base, refus par le lot, puis
admission du signe fourni.

`narration.schema_audit` demande désormais `attitudes` pour chaque segment
y compris dans les récits de résultat au dossier réduit sans signes. Chaque attribution porte son
personnage, sa cible, son affirmation, l'identifiant de son appui et un jugement
de compatibilité. `controler_attitudes` vérifie les références exactes et la
concordance personnage/cible, indépendamment du verdict du segment. Un appui
absent ou un sens jugé non établi produit un refus avec les signes et impressions
disponibles dans `attendu`. `consigner` revérifie les appuis dans le contexte
actuel avant toute écriture. Une réplique de PNJ n'établit toujours que sa parole,
jamais la vérité de son émotion.

Le banc `attitudes.json` prépare la crue du Relais : Ilse à l'écart de Brune,
Gorm qui surveille Brune, une dispute récente et une proposition du joueur.
Les options de préparation de `banc_parties.preparer` appellent les règles
communes de prévision, parole, place, surveillance et lecture ; aucun signe
ni aucune impression n'est injecté directement. Les autres scripts gardent
leur préparation. Aucun fichier moteur réservé au lot 175 n'est modifié.

Vérification : **40 tests ciblés finaux verts**, dont six nouveaux tests avec
sous-cas ; console/MJ simulé pour Ilse et Gorm, refus puis admission,
personnage/cible/identifiant/sens, parole distincte d'émotion, perception
périmée avant enregistrement, état complet et texte après recharge.
**4/4 empreintes Relais 2 h identiques à `3842aef`** : chronique, mesures et
état complet. Pas de comparaison des temps. Suite complète unique :
**2 262 tests, 261 fichiers, 1 308,136 s**, deux échecs MiMo historiques
`6 != 5`, zéro erreur ou ignoré. Le dernier renforcement (extraction également
dans les dossiers réduits) a été repris en ciblé ; aucune seconde suite complète.

**Limites et suite.** Aucun appel Luna : coffre illisible, conformément au
brief. La commande exacte `banc_multi.py`, référence `cdaf371`, deux passes
sur relais/crypte/atelier/echanges/attitudes, figure dans
`C:/Users/msics/donjon/artifacts/attitudes-176/luna-a-jouer.txt`.
Appels/tour, secondes/tour, replis et absence d'attribution sans appui en
partie réelle ne sont donc pas certifiés ; aucune copie de sauvegarde réelle
n'a été fournie ou modifiée. Détecter une attribution, juger son sens et garder
la nuance d'une impression restent sémantiques. Les rapports historiques sans
extraction restent lisibles ; une extraction omise ou faussement vide par
l'auditeur ne reçoit pas de garantie déterministe. Le moteur garantit les
références des attributions effectivement extraites, pas toute prose libre.

Au plus deux travailleurs de calcul en priorité réduite, sur poste partagé.
Bruts : `C:/Users/msics/donjon/artifacts/attitudes-176/` ; jonction temporaire
pour les traces automatiques du worktree. Les quatre nouvelles références du
comparateur ont été déplacées du cache partagé sous ce même dossier ; les
chemins de provenance du JSON indiquent leur emplacement initial.
Aucune clé de signature Git configurée ;
livraison non signée, branche seule proposée à la poussée, `main` intacte.
