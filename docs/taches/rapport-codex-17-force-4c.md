# Rapport Codex 17 — se défendre, fuir, protéger, se rendre (4c)

Branche `codex-force-4c`, non fusionnée, issue de `main` **9520f77**, tâche initiale
**6cce67d**. Worktree demandé : `tmp-worktrees/codex-force-4c`. Le commit d'implémentation
**c0f1593** porte une signature SSH. Aucun changement de `main`, des scénarios ou des profils.
Luna reste `gpt-6-luna`, sans comparaison de modèles. Tous les essais de partie utilisent
des sauvegardes temporaires ; le coffre partagé est `C:\Users\msics\donjon\.seuil-auth`.

## Contrat et fonctions

- `defense.auteurs`, `retenir`, `dangers` : la violence attribuée devient une croyance
  `violence`, par auteur et victime, datée, avec source perceptive. Elle ne dépend pas des
  quarante lignes de mémoire narrative. Les positions et états de l'autre viennent des
  croyances ; aucun accès à sa FOR privée ni à une identité donnée par un bruit anonyme.
  Une riposte dont on a perçu la cause ne devient pas une agression nouvelle contre tous
  les témoins. Sans cette cause connue, le moteur ne devine pas l'intention privée.
- `defense.constater_fin`, `corps.endormir` : neutralisation ou reddition constatée clôt
  l'atteinte connue ; le réveil seul ne la rouvre pas. Un nouveau geste peut la rouvrir.
  Celui qui perd connaissance abandonne son plan par le renoncement existant. Cela évite
  la boucle ranimer/frapper entre un protecteur et les victimes de son protégé.
- `combat.prix_violence`, `facteur_violence`, `Vue.violence` : une seule règle pour
  l'agression, la défense au quart, douceur 100 en défense et le double prix sur un rendu.
  L'admissibilité de la violence et les prix lus par une réaction entrent dans `_entrees`,
  donc dans les deux graphes `sombre`/`lumiere` et dans le certificat `_sans_plan`.
  L'agression ne réécrit plus `2 * degat <= ENJEU` ni son facteur 2 dans la recherche.
- `planification.reagir`, `_gestes_defense` : un même graphe compare trajets, fermeture,
  verrouillage avec clé portée et riposte, aux coûts de risque, de douceur et d'exposition.
  Les étapes physiques sont revalidées ; un coup ne suppose pas une victoire réelle.
  Le recours à une reddition exige une blessure grave et aucun plan de fuite/riposte.
  Le dégagement emploie FOR/DEX contre FOR, sans faute. Cette étape ne crée pas de prise.
- `defense.protection`, `ouie.entendre` : un cri reconnu du protégé garde un secours à
  examiner, même si la vue explique le bruit entre-temps. Le protecteur rejoint le lieu
  réellement entendu ; le cri ne lui donne pas le nom d'un agresseur. Une violence connue
  peut lui faire intervenir. Les secours examinés sont soldés ensemble, une intervention
  par examen, et les témoins passent par le registre existant.
- `combat.interrompre`, `corps.reprise`, `pnj.agir` : le mouvement d'un coup reste à finir
  quand un autre coup l'interrompt. Recevoir un coup ne crée pas un tour supplémentaire
  gratuit au même instant. La date de fin est sauvegardée et validée pour tous.
- `Moteur` et `defense.preparer_joueur` : actions typées `fuir`, `riposter`, `se_rendre`,
  `degager`, fiche avant tentative, une cause par refus et `attendu` en identifiants.
  La fuite du joueur suit les pas communs, revalidés un par un pendant la vie des autres ;
  elle s'arrête si un pas devient impossible ou si le joueur perd connaissance. La riposte
  emploie le coup commun. La reddition enregistre puis fait entendre « Je me rends ! ».
  L'issue d'un dégagement ou d'une fuite interrompue est aussi celle du journal de l'action.
  Le danger identifié figure dans la fiche et dans `joueur.dangers_percus` du contexte du
  MJ ; le coup qu'on ne voit pas ne donne aucun nom. La projection habituelle des noms
  s'applique. L'arrêt d'une fuite par inconscience lit l'événement physique enregistré,
  indépendamment de la formulation du récit ; le réveil ne reprend pas le trajet.
- `corps.visible`, `corps.etat`, `rendu` : la cessation de résistance apparaît dans l'état
  visible et la fiche. Le journal physique, le récit et le rejeu conservent les réactions ;
  les mesures ajoutent fuites, ripostes, interventions et redditions quand elles existent.

## Vérifications de chaîne

Seize tests dans `tests/test_defense.py`, en plus des dix-sept tests de coup de 4b :

- Brune frappe Aubin, puis Ilse comme deuxième victime ; Ilse témoin, Gorm à l'échoppe.
  La victime quitte le danger, Gorm reconnaît le cri, rejoint et examine le lieu. État et
  rendu après rechargement ; le même laps de cinq minutes, d'un bloc ou découpé/rechargé,
  donne exactement les mêmes `data` et le même rendu.
- Coup par surprise sur Aubin et Gorm : pas de nom fabriqué chez la victime inconsciente.
  Refus du joueur sans danger perçu, sans prise ou avec des champs incompatibles : `attendu`.
- Deux victimes acculées dans une fixture de lieu sans passage : riposte réelle à douceur
  100 ; puis reddition autonome, blessure grave et douceur 99 dont le prix exclut la riposte.
  La reddition se voit après recharge, et un nouveau coup la rompt.
- Deux protégés frappés sous les yeux de Gorm : intervention physique à douceur 100.
  Joueur attaqué par Brune, puis par Gorm : fiche sans mutation, fuite/riposte/reddition
  exécutées et rechargées ; dégagement réel de chacun des deux auteurs d'une prise déclarée.
- Contexte du MJ et fiche du joueur : agresseur identifié présent, jamais le nom d'un
  auteur non vu. Une fuite assommée en route attend le réveil puis s'arrête, avec échec
  dans le journal ; elle ne franchit pas ensuite la sortie automatiquement. Les deux
  agresseurs sont éprouvés et le rendu de la salle est contrôlé après rechargement.
- Soixante souvenirs intermédiaires ne font pas oublier la cause vue d'une riposte ; la
  neutralisation vue puis le réveil ne relancent pas les coups. Un mouvement interrompu
  refuse un second coup du même auteur avant sa fin, après rechargement également.
- Recherches répétées sous `VERIFIER` et vérification spatiale exhaustive, puis changement
  de l'état cru de l'adversaire : aucun résultat périmé repris.

Deux fichiers de tests hérités ont été accordés au comportement nouveau, sans supprimer leur preuve :
`test_passage` contrôle le recul dans le journal physique, car la victime peut déjà marcher
pendant les trois secondes de la poussée ; le passage peut donc être de nouveau occupé.
Le Gorm qui pousse Aubin peut aussi abandonner sa destination après une riposte ; la poussée
et son épreuve de relation restent contrôlées. `test_combat` sépare deux jets indépendants
sur deux états, au lieu de donner deux coups à la même date en contournant leur durée.

## Mesures

Suite complète finale : **1 482 tests, aucun échec ni erreur, 14 ignorés**, en **483,7 s**, via
`tools/tests.py --processus 4`. Les tests de terminal et de page nécessitent leurs sockets
locaux : une première passe dans le bac à sable ne pouvait pas les ouvrir ; elle a été
arrêtée puis remplacée par cette passe complète. Les tests ciblés de force et de passage
sont verts. Les seize tests 4c sont également rejoués sur le dernier code, y compris
l'assommement pendant une ouverture de porte avant le pas de fuite. La signature SSH de
`c0f1593` est vérifiée avec la clé publique locale ; les commits de livraison sont signés.

Empreintes **2 h et 8 h**, quatre scénarios × graines 1985, 7, 42, 2024 : **16 paires
identiques à chaque durée** à `9520f77`, sans normalisation : chronique, mesures et état
final complet. Référence puis branche, quatre processus au plus. Le partage du prix de
violence dans une vue et la lecture moins coûteuse des croyances ont aussi leur contrôle
propre contre `c0f1593` : **16 paires de 2 h identiques**. La passe finale de 8 h contre
`9520f77` reste identique. Jamais deux lots de banc moteur en même temps.

Le premier relevé de temps dépassait la marge visée à l'auberge et à la crue. Le prix de
violence, pourtant constant par motif/défense/reddition dans une recherche, était recalculé
pour chaque cible. Il est désormais partagé dans la vue. Aucun terme ni ordre du graphe
ne change ; les empreintes le vérifient. Dernière passe de 8 h, temps CPU moyen par nuit,
machine partagée, référence puis branche :

| Scénario | 9520f77 (s) | Branche (s) | Écart |
|---|---:|---:|---:|
| Relais | 11,30 | 11,02 | −2,4 % |
| Mine | 35,45 | 35,53 | +0,2 % |
| Auberge | 35,00 | 35,89 | +2,5 % |
| Crue | 20,68 | 20,99 | +1,5 % |

La moyenne reste dans la marge de 10 % sur cette passe. Le partage du poste et des
fréquences du processeur interdit d'en déduire une borne pour toute exécution future.

### Rixe et Relais, huit graines, 8 h

Graines 1985, 7, 42, 2024, 3, 11, 99, 500 ; départ tiré ; **joueur dans `chambre_cloche`
dans les deux scénarios**. Minutes urgentes sans recours moyennes : **68,75 à rixe**, contre
**64,375 au Relais**, soit **+6,80 %**, sous la borne de 10 %.

| Graine | Rixe | Relais |
|---|---:|---:|
| 1985 | 35 | 0 |
| 7 | 150 | 150 |
| 42 | 130 | 130 |
| 2024 | 120 | 120 |
| 3 | 0 | 0 |
| 11 | 0 | 0 |
| 99 | 0 | 0 |
| 500 | 115 | 115 |

Les huit nuits de `rixe` sont **identiques à 9520f77**, chronique, mesures et état final
complet compris. Aucun coup spontané, mort, usurpation ni violation constatée. Le CPU moyen
de `rixe` passe de 10,17 à 10,03 s (−1,3 %). Une première comparaison où `rixe` gardait le
placement par défaut en antichambre était biaisée et a été écartée : elle n'est pas le
relevé comparable à celui du Relais avec joueur dans la chambre de la cloche.

### Épreuves physiques

Deux copies sur dix minutes, `VERIFIER=True` et spatial à 1, sauvegardées et rechargées,
avec rendu et rejeu :

| Victime initiale | Fuites constatées | Intervention de Gorm | Coups / PV perdus | Morts |
|---|---|---:|---:|---:|
| Aubin | Aubin à 8,3 s ; Ilse à 9,7 s | 22,2 s | 1 / 3 | 0 |
| Ilse | Ilse à 9,7 s | 23,7 s | 1 / 3 | 0 |

Le danger initial cesse par le départ et le protecteur examine le lieu entendu. Ces
épreuves n'inventent ni une riposte d'Aubin ni un coup du protecteur après le départ du
protégé. Les tests avec danger présent vérifient séparément la riposte et l'intervention
physique. Les scènes de nuit libres, sans coup, ne suffisent pas à prouver ces réactions.

### Contrôles croisés

`planification.VERIFIER=True` sur toute la durée ; `spatial.VERIFICATION=1` sur 2 h puis
0,2 sur 8 h ; graine 42 ; Relais, mine, auberge, crue et `rixe`. Les dix nuits passent
avant et après le partage du calcul : aucun écart, aucune usurpation ni violation
constatée. À 8 h, l'auberge a les mêmes **66 recherches bornées** que la base ; les
autres contrôles en ont zéro. Une recherche jouée bornée n'est pas un écart de sa
reprise ou de la mémoire ; `VERIFIER` reste entièrement actif.

### Luna et connexion réelle

Trois scènes versionnées : `tests/data/bancs/force-4c-fuir.json`, `force-4c-riposter.json`,
`force-4c-reddition.json`. Un coup réel de Brune sur le joueur est établi à la préparation
par `combat.frapper`, avec ses témoins et souvenirs ; le joueur connaît le seuil de fuite.
Saisies exactes : « je m'enfuis », « je me défends », « je me rends », puis « tenter ».
Le banc garde le fil et recharge chaque copie. Aucune sauvegarde utilisateur n'est lue.

**Validation de typage Luna non aboutie.** La session partagée est lisible et non expirée.
Le catalogue authentifié a répondu (7 modèles, `gpt-6-luna` disponible, une réponse en
43,4 s), mais ses consultations ont également expiré à plusieurs reprises. Dix essais
de scène se sont arrêtés avant la proposition, au catalogue ; un essai avec ce catalogue
réel acquis une seule fois est allé jusqu'au transport puis a échoué. Une ouverture
WebSocket directe, sans afficher d'en-tête ni de secret, donne `TimeoutError`, sans statut
HTTP. Aucun texte ni action de Luna n'a donc été obtenu ; aucun succès de typage, temps
par tour validé ni absence de contradiction narrative ne sont revendiqués.

Les préparations et les trois actions sont vérifiées localement par les tests de chaîne ;
elles restent à rejouer avec le transport fonctionnel. Aucun changement de fournisseur,
modèle, auth, transport ou règle narrative n'a été ajouté pour contourner ce blocage.

## Critères et limites

Les règles mécaniques et leur persistance sont réalisées ; **le critère 4c complet ne
doit pas être annoncé atteint**. Dans l'épreuve aux valeurs actuelles, Aubin peut choisir
la fuite comme Ilse. Lui imposer une riposte par son nom, un scénario, une formulation ou
une consigne à Luna aurait contredit la règle prioritaire du dépôt.

Le risque reste l'estimation de `force.force_crue`, pas une simulation de duel complet.
Le graphe compare un coup revalidé à la fuite ; il ne prédit ni les pas adverses ni toutes
les issues des jets suivants. Aux longueurs des trajets s'ajoute un surcoût d'exposition
forfaitaire, sans pondération fine de chaque pas près de l'adversaire. Une fuite ne
garantit donc pas d'avance. Les poursuites
assommer-pour-prendre gardent rejoindre/chercher/appeler et la patience existants : aucune
preuve universelle de fin en moins de dix minutes n'est fournie. Un protecteur qui arrive
après le départ de la victime examine le lieu sans inventer l'auteur d'un coup.

Le joueur ne ferme ni ne verrouille automatiquement sa fuite ; il conserve ces choix
par les actions disponibles. `degager` fonctionne pour une prise déclarée, mais saisir,
liens, contrainte prolongée et issues différées restent en 4d. Aucun `tuer`, mort nouvelle,
étape 5 ou migration garantie d'anciennes sauvegardes. Le contrôle sémantique de la
narration garde ses limites ; aucune exception lexicale ni nouveau mode ne les masque.

## Reproduire

Depuis ce worktree, avec le Python du dépôt principal :

```powershell
$py = 'C:/Users/msics/donjon/.venv/Scripts/python.exe'
$env:PYTHONIOENCODING = 'utf-8'
$env:SEUIL_AUTH = 'C:/Users/msics/donjon/.seuil-auth'
& $py tools/tests.py --processus 4
& $py tools/comparer_bancs.py --reference 9520f77 --scenarios relais mine auberge crue --empreintes --heures 2 --processus 4 --sortie artifacts/force-4c/empreintes-2h.json
& $py tools/comparer_bancs.py --reference 9520f77 --scenarios relais mine auberge crue --empreintes --heures 8 --processus 4 --sortie artifacts/force-4c/empreintes-8h.json
& $py -m donjon.banc_pnj --scenario rixe --heures 8 --graines 1985 7 42 2024 3 11 99 500 --joueur chambre_cloche --processus 4 --diagnostic
& $py -m donjon.banc_pnj --scenario relais --heures 8 --graines 1985 7 42 2024 3 11 99 500 --joueur chambre_cloche --processus 4 --diagnostic
& $py tools/banc_parties.py tests/data/bancs/force-4c-fuir.json tests/data/bancs/force-4c-riposter.json tests/data/bancs/force-4c-reddition.json --fil --max-appels 50 --sortie artifacts/force-4c/luna
```

Traces locales non versionnées : `artifacts/force-4c/`, empreintes, comparaison de `rixe`,
contrôles, diagnostics, états avant/après des deux épreuves, rendus, rejeux HTML et fils
Luna. Les chiffres et les limitations utiles sont recopiés dans ce rapport.
