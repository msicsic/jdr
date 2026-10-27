# Entrées des scènes contractuelles, avant le lot 186

Les nouveaux moyens sont testés sur les scénarios courants par
`test_occasions_scenarios.py`, le banc de `test_besoins.py` et les 24 nuits du lot.
Les scènes isolées ci-dessous conservent leurs hypothèses d'auteur : ajouter
une nourriture ou un combustible accessible peut légitimement remplacer le
vol, l'appel, le prêt ou le trajet dont elles vérifient les conséquences.

`avant_occasions_186.json` inverse seulement les 82 changements de données du
lot, **avant** la construction du `Monde`. Les sept dictionnaires obtenus ont
été comparés intégralement aux JSON de `12a936d`. Aucun moteur ancien, aucune
nouvelle règle et aucune assertion de contrat affaiblie. Le banc du joueur
passif conserve au contraire la fabrique courante : sa demande vise désormais
les galettes et l'état rechargé vérifie que la réserve reste verrouillée.

| Fichier de scènes | Hypothèse historique conservée et justification |
|---|---|
| `test_besoins.py` | La réserve est l'unique nourriture disponible dans les scènes de vol ; le test du banc vérifie les nouvelles données. |
| `test_tensions.py` | Identité du lot demandé, consommé et rendu, ouverture/fermeture de la réserve et stock de chauffage du jalon F. |
| `test_social.py` | Le désespoir ou l'attente d'un témoin sont étudiés sans repas alternatif. |
| `test_paroles.py` | État initial des interlocuteurs et constats disponibles pour les transmissions bornées par l'INT. |
| `test_ouie.py` | Bruit du geste étudié, sans nouveaux recours qui déplacent ses acteurs. |
| `test_voix.py` | La recherche d'une voix aboutit à la demande alimentaire déclarée par la scène. |
| `test_lumiere.py` | Le bois déclaré épuisé l'est entièrement ; la lampe reste le recours étudié. |
| `test_planif_defauts.py` | Les scènes de serrure et de passage n'ont pas de nourriture alternative immédiate. |
| `test_refus_retenus.py` | Les moyens dont l'apparition doit lever le refus restent ceux contrôlés par chaque scène. |
| `test_echanges_argent.py` | Prix, prêt et restitution étudiés avec les ressources qui fondaient leur plan. |
| `test_echanges_suite.py` | Identité du combustible appris, enquêté, acheté ou prêté, et liens initiaux de ces scènes. |
| `test_combat.py` | L'embuscade pour un bien conserve ses besoins et ses recours concurrents d'origine. |
| `test_constater_rumeurs.py` | Constats et appels sont exercés sans nouvelle ressource qui évite la recherche de l'interlocuteur. |
| `test_eau.py` | Positions initiales des scènes de montée de l'eau, notamment Ilse avant sa fuite. |
| `test_proposer_recours.py` | La nourriture et les fournitures des scènes de marché restent celles explicitement préparées ; aucun nouveau candidat n'altère le devis étudié. |
| `test_planification.py` | Les chaînes de recherche ont pour entrée une réserve verrouillée et aucun repas porté par le gardien. |
| `test_entretenir.py` | Les stocks et propriétaires de combustible et de vivres déterminent le service et les fournitures étudiés. |
| `test_lumiere_garde.py` | La lampe ou le combustible de la scène restent les moyens dont la garde est comparée. |
| `test_engagement_deplacement.py` | Le sous-but social d'évacuation conserve les positions, les liens et les ressources de son entrée d'auteur. |
| `test_tache_promise_recours.py` | La tâche promise est étudiée avec ses fournitures explicites, sans repas ou bois alternatif nouvellement porté. |
| `test_ouie_temoins.py` | Le cambrioleur inconnu n'a pas de contrepartie qui lui ferait prendre la parole et se faire identifier avant l'interprétation du bruit. |

`test_parts_achetees.py` conserve les données courantes : Joss annonce aussi
ses nouveaux copeaux, dont la connaissance est vérifiée après rechargement.
`test_recit_pnj.py` conserve le banc courant et attend la demande de galettes
que le récit raconte désormais. `test_scene.py` attend les galettes visibles
portées par Gorm, avec le pied-de-biche de sa scène ; ce contenu est également
vérifié après rechargement.
Le joueur de cette scène occupe une case libre, au lieu de partager celle
d'Aubin : la sauvegarde ajoutée contrôle aussi la validité du placement.
