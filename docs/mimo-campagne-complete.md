# MiMo — campagne complète avec l’adaptateur final

Le 21 octobre 2026, les quatre scripts existants ont terminé avec **90 saisies, 38 tours MJ,
113 appels MJ et 120 requêtes Xiaomi réelles**. Aucun tour n’a fini en erreur technique.
Les sept premières réponses rejetées ont toutes été corrigées par l’unique relance autorisée.
Un défaut de fidélité à la parole du joueur reste présent : ce succès technique ne valide pas
la qualité générale du MJ.

La campagne utilise `mimo-v2.6-flash`, réflexion désactivée, JSON natif, IPv4 et les vraies
instructions du jeu. Elle passe par le fournisseur MiMo final et les boucles ordinaires du MJ,
du moteur, du rendu console et de la sauvegarde. Les scripts ne sont pas modifiés.
Base : `4af828bbdf845129c8920589d63448cccab0c9a5`, branche `refactor/adaptateurs-fournisseurs`.
Aucune modification ni fusion dans `main` n’a été faite pour cette campagne.

## Résultats

| Script | Saisies | Tours MJ | Appels MJ | Requêtes physiques | Erreurs de tour | Temps moyen cumulé des appels par tour MJ |
|---|---:|---:|---:|---:|---:|---:|
| Relais | 23 | 11 | 35 | 36 | 0 | 25,4 s |
| Crypte | 42 | 9 | 29 | 31 | 0 | 24,6 s |
| Atelier | 15 | 11 | 27 | 31 | 0 | 14,6 s |
| Échanges | 10 | 7 | 22 | 22 | 0 | 20,1 s |
| Total | 90 | 38 | 113 | 120 | 0 | 21,1 s |

Les 90 saisies comprennent des déplacements, des commandes natives, des questions, des actions,
des préparations de tentative et des refus. Ce ne sont pas 90 actions exécutées par le modèle.
Les appels MJ comprennent aussi les audits et la narration des résultats.

- Durée totale de la campagne : **818,69 s**, soit environ **13 min 39 s**.
- TTFT par requête physique : médiane **2,177 s**, moyenne 2,540 s, minimum 0,734 s, maximum 12,619 s.
- Réponse complète par requête physique : médiane **6,316 s**, moyenne 6,655 s.
- Durée cumulée des appels par tour MJ : médiane **20,19 s**, moyenne 21,09 s, maximum 60,07 s.
- Aucun token de réflexion déclaré, aucun contenu de réflexion reçu.
- Aucun échec réseau/protocole, aucun garde-fou numérique déclenché, aucun repli narratif signalé.

Le TTFT attend le **premier contenu JSON généré non vide**, depuis le début de l’envoi HTTP.
Il ne mesure ni le premier octet SSE, ni la réponse finale affichée au joueur. Les 120 requêtes,
y compris les sorties rejetées et leurs corrections, entrent dans ces statistiques. Les durées
par tour sont des sommes de durées d’appels, pas une mesure directe du délai complet de l’interface.

## Les corrections réellement observées

106 des 113 premières réponses respectent le contrat, soit 93,8 %. Les sept autres nécessitent
une relance : 7/7 réussissent, pour 113 résultats finalement admis par l’adaptateur.
Sur les 120 réponses physiques, 113 sont donc conformes et sept sont rejetées.

| Rejet → correction | Fonction | Défaut initial |
|---|---|---|
| 20 → 21 | repondre_au_joueur | Enveloppe `fonction` / `arguments` au lieu des arguments à la racine |
| 38 → 39 | auditer_narration | Données supplémentaires après le JSON |
| 62 → 63 | repondre_au_joueur | Proposition `patienter` hors du schéma autorisé à cet endroit |
| 71 → 72 | repondre_au_joueur | Mode `improviser` inexistant |
| 73 → 74 | repondre_au_joueur | Champ `valuee` supplémentaire dans un effet |
| 75 → 76 | auditer_action | Données supplémentaires après le JSON |
| 85 → 86 | repondre_au_joueur | Référence `perche_3` au lieu de la clé de fait autorisée |

Les sept réponses de correction représentent 30,99 s supplémentaires de temps de requête,
hors petits coûts locaux. L’effet contrefactuel sans relance n’est pas mesuré : une erreur
aurait aussi modifié les échanges ultérieurs.

Les réponses rejetées ne sont pas remises au moteur. La correction reste une génération du
modèle, avec risque de changement de sens : à l’appel 63, la simple attente devient une
composition attendre puis prendre les crochets. Le moteur refuse ensuite cette composition
car les crochets sont trop loin. Aucune conversion locale des arguments n’a masqué ce changement.

## Audit du sens et de l’état

**Défaut confirmé — parole du joueur enrichie.** Échanges, tour 5 :

- Saisie : `je chuchote à Brune que je me méfie d'Aubin`.
- Réplique produite : `À voix basse : je me méfie d'Aubin. Il veille sur l'eau, dit-il, mais je le trouve trop pressé de parler à ma place. Garde ça pour toi.`

Le modèle ajoute une raison et une demande de discrétion absentes de l’intention. Le jeu accepte
la proposition valide en JSON, l’affiche et l’enregistre dans `paroles_joueur` pour Brune seule.
Cette même réplique subsiste dans la conversation et après reprise. Les contrôles actuels
ne garantissent donc pas la fidélité sémantique de la reformulation du joueur. Aucun correctif
du jeu ni ajout de consigne n’a été introduit pendant cette mesure.

**Ancien défaut non reproduit — saut à la perche.** Atelier, tour 14 : la manœuvre est refusée
à distance et la réponse invite à s’approcher, sans raconter un élan ou un déplacement exécuté.
Avant et après : position `[3, 2]`, minutes `2`, révision `7`. Ce résultat est compatible avec
l’état, sans prouver que toute narration après refus est fiable.

**Contrôles efficaces.** Crypte, tour 2 : les contrôles font retirer un lieu non connu puis une
affirmation injustifiée sur l’obscurité derrière une porte fermée. La réponse finale conserve
l’inconnue. L’unique alerte lexicale finale, au Relais, est une mention négative du pied-de-biche
demandé par le joueur ; elle ne révèle ni sa position ni son existence comme objet caché.

**Point à examiner.** Relais, tour 6 : deux propositions `observer/contexte` reçoivent des
verdicts de couverture différents. La seconde observation est exécutée ; le récit conclut à
l’absence d’empreintes plus précisément que le résultat moteur explicite. L’absence de coût
temporel d’une observation ne suffit pas à qualifier ce cas d’action fictivement exécutée.

Les 38 sorties des tours MJ ont été lues, en plus des indicateurs automatiques. Cela ne constitue
pas un audit sémantique exhaustif de toutes les affirmations. Une parole de PNJ atteste qu’elle
a été prononcée, sans rendre son contenu vrai.

## Sauvegardes et preuves

Les quatre sauvegardes finales sont chargées exactement avant les commandes de reprise.
Après `inventaire`, `regarder`, `quitter`, Échanges actualise uniquement `exploration`,
`murs_memorises` et `souvenirs_visuels`. Les objets, le joueur, les minutes, le journal,
les engagements et les finances ne changent dans aucune partie.

L’audit hors réseau recharge et vérifie **87 instantanés**, revalide les **113 réponses admises**
avec leur schéma exact, contrôle les liens des rapports et compare le code capturé au commit.
Les trois premiers `regarder` de Relais/Crypte/Atelier précèdent la création de leur sauvegarde :
ils n’ont pas d’instantané disque. Dans ces parties, `initial.json` désigne la première sauvegarde
disponible, pas nécessairement le monde avant toute saisie. Les réponses et prompts restent conservés.

[Métriques](verification-mimo-complete/metriques.json) ·
[Vérifications](verification-mimo-complete/verification.json) ·
[Observations avec références aux captures](verification-mimo-complete/observations.json) ·
archive intégrale : `artifacts/mimo/campagne-complete.zip`, non versionnée (20 Mo ; poste de
l’auteur seulement, voir `archive.json` pour son empreinte)

Décompresser l’archive puis ouvrir `index.html`. Elle contient les 120 requêtes et réponses complètes,
les octets SSE exacts, les événements horodatés, les diagnostics, les propositions transmises au jeu,
les fils complets des parties, les sauvegardes et le code capturé avant le lancement. Un manifeste
SHA-256 permet de vérifier ses fichiers. La clé et les en-têtes d’authentification ne sont pas inclus.

## Reproduction et limites

Depuis le worktree disposant des dépendances MiMo :

```powershell
python tools/valider_mimo_parties.py --cle-fichier '<fichier local de clé Xiaomi>' --sortie artifacts/mimo-campagne-complete --max-appels 300 --effort none --relances-format 1
python tools/rapport_validation_mimo.py artifacts/mimo-campagne-complete --observations artifacts/mimo-campagne-complete/observations.json
```

La deuxième commande enrichit le rapport avec les observations de cette passe ; pour une nouvelle
campagne, fournir son propre fichier d’observations ou omettre cette option. La sortie doit être
un nouveau dossier. L’archive inclut aussi `audit-hors-reseau.py`, qui refait les vérifications
de cette capture depuis le checkout du jeu, sans réseau.

Une seule passe a été réalisée, sans comparaison simultanée à Luna. La première campagne MiMo
utilisait un moteur antérieur et aucune correction de format : les différences globales de
qualité, de durée ou de nombre d’appels ne peuvent pas être attribuées uniquement à l’adaptateur.
Les 998 tests de la finition précédente n’ont pas été relancés : aucun code du jeu n’a changé
pendant ce jalon, consacré à la campagne et à ses preuves.
