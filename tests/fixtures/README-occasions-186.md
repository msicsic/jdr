# Entrées des scènes contractuelles du lot 186

La variante finale n'ajoute aucune nourriture : les lots de galettes et leurs
connaissances sont retirés. Les assertions qui les visaient ont retrouvé leur
source d'avant 186 (`test_besoins`, `test_recit_pnj`, `test_scene`, etc.).
`test_occasions_scenarios.py` contrôle désormais le stock alimentaire exact de
`12a936d`, par une référence déclarée indépendante de la fabrique courante,
et sept variantes après cinq minutes de jeu puis sauvegarde/rechargement
(état, description, besace et sons).

`avant_occasions_186.json` n'inverse plus que les **54 changements restants**,
avant construction du monde : bois propre, liens/connaissances et positions.
Au lot 200, ses inverses sont appliqués à la base actuelle `23aba63` : ils
conservent les ajouts ultérieurs, notamment les projets 184/192. Le test des
sept empreintes structurelles indépendantes vérifie cette conservation.
Les fabriques contractuelles sont conservées uniquement dans ces scènes :

| Fichier | Précondition d'auteur conservée |
|---|---|
| `test_constater_rumeurs.py` | Constats, interlocuteurs et fournitures de bois explicitement préparés. |
| `test_eau.py` | Ilse et Aubin commencent aux positions de la scène de montée de l'eau. |
| `test_echanges_suite.py` | Identité du bois appris, enquêté, acheté ou prêté. |
| `test_entretenir.py` | Fournitures et propriétaires du combustible nécessaire au travail étudié. |
| `test_lumiere.py` | Le bois déclaré épuisé l'est entièrement ; la lampe est le recours étudié. |
| `test_lumiere_garde.py` | Les moyens dont on compare la garde restent ceux de la scène. |
| `test_ouie.py` | Le geste étudié ne cède pas la place à un nouveau marché de bois. |
| `test_ouie_temoins.py` | Le cambrioleur inconnu ne se fait pas identifier en proposant son bois avant l'interprétation du bruit. |
| `test_proposer_recours.py` | La scène de marché conserve ses contreparties et liens déclarés. |
| `test_tache_promise_recours.py` | L'autonomie de la tâche dépend de ses seules fournitures déclarées. |
| `test_engagement_deplacement.py` | Ilse commence avant la destination de l'agenda étudié ; le projet n'est pas déjà atteint à l'installation. |

Dans les autres fichiers, la fabrique courante est rétablie. Les rares scènes
qui ont besoin d'absence de bois le disent localement, sans affaiblir leurs
assertions :

- `test_besoins.py`, `test_constater_rumeurs.py` : pas de contrepartie propre
  qui évite la recherche des crochets ou la constatation du verrou.
- `test_combat.py` : pas de bois propre à échanger avant l'embuscade.
- `test_recit_pnj.py` : Brune doit prendre les planches d'autrui ; son bois
  propre est épuisé dans cette scène de témoignage du vol.
- `test_refus_retenus.py` : les copeaux de Joss sont aussi brûlés dans la scène
  où plus aucun combustible ne peut rendre le travail possible.
- `test_deliberation_evenements.py` : pas d'autre fournisseur de bois dans
  la scène de relance directe du brasero à la torche.
- `test_marche.py` : les enquêtes « rien » correspondent à un stock absent ;
  le gardien reste près du foyer après l'avoir éteint.

`test_parts_achetees.py` garde les données courantes : Joss annonce aussi ses
copeaux, dont la connaissance est vérifiée après rechargement. Aucun moteur
ancien ni nouvelle règle du jeu n'est introduit par ces mises en scène.

## Reprise 200 sur les projets de pièces

Les fabriques `relais` de `test_tensions`, `test_social`, `test_esprits` et
`test_paroles` déclarent désormais les données sans ces occasions. Leurs scènes
étudient respectivement les fournitures précises d'un recours, la circulation
d'une rumeur, un obstacle visuel et un mensonge. Le bois propre de Brune permet
sinon une vente pour sa dette : déplacements, paroles, jets consommés et témoins
changent légitimement. Les contrats de leurs utilisateurs (écoute, sécurité,
protection, réclamation, crochetage, délibération) conservent ainsi leur intention.

Même isolation dans `test_combat.scene` (coups, prise et garde), `test_signes.scene`
(impressions avant toute vente), la scène du bureau noir de
`test_dynamique_besoins`, l'épuisement du camp de `test_mine` et les deux scènes
de crue du test du poêle dans `test_ressources` : Odon/Brune ne possèdent pas le
combustible ajouté. Aucun projet n'est désactivé, aucun jet supplémentaire
n'est inventé, aucune assertion n'est remplacée par une tolérance.
