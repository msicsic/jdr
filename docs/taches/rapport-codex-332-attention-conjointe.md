# Lot 332 — Attention conjointe

Branche `codex-attention-conjointe`, **non fusionnée**, base `integration 7e65907`.
29 octobre 2026. Ni Luna, ni suite complète, ni modification de scénario.

**Invariant.** Un regard réellement perçu donne sa direction, sans donner sa cible
imperceptible. Un PNJ disponible peut suivre ce regard s'il se fie à son auteur ou
si leur affection atteint le seuil commun de familiarité. Il tourne avec
`spatial.QUART * quarts`, puis la perception commune révise ses seules croyances.
La direction choisie par `signes.regarder` reste dans l'attitude : déplacer le
tiers caché ne déplace plus secrètement ce regard. Les épisodes physiques de signes
et `esprits.regards_suivis` dédupliquent le suivi sans échéance, après recharge aussi.
Un changement de direction ou une nouvelle émission physique peut ouvrir un autre
suivi ; perdre puis retrouver la vue du même regard ne le renouvelle pas.

**Fonctions et contrat.** `signes._percus`, `publics` et `impressions` projettent
la direction et retirent la cible inaccessible, même dans une impression historique.
`regard_a_suivre` et `suivre_regard` n'utilisent que ce signal et le lien propre de
l'observateur. `pnj.agir` exécute la rotation ; l'ordonnanceur accepte aussi un PNJ
sans intention. Le guet et les plans autres que les gestes de séjour déjà admis par
la surveillance conservent leur priorité. Aucun accès nouveau dans la recherche :
`planification.py` et `_entrees` sont inchangés. Les nouveaux états sont sauvegardés
et validés par `esprits`/`signes`. Recouvrement possible avec 330 : **`esprits.py`,
`pnj.py`, `signes.py`** ; conserver la perception et les preuves communes à la fusion.

**Tests ciblés : 94 tests distincts verts, huit fichiers**, deux travailleurs
réduits au plus. Neuf nouveaux tests : deux scènes Relais/auberge, vrais coups de
la rixe (Brune/Aubin, Ilse suit), noir/dos/inconscience/non-proche, obstacle opaque,
cible partie, délai sans répétition, nouvelle direction, ancienne impression,
monde/rendu/scène rechargés. Deux scénarios avancés sur le même laps de huit secondes,
entier ou découpé avec recharges : états complets et projections identiques.
Les premiers échecs de prémisses (cases, visibilité et inconscience) sont conservés
dans les bruts ; aucun oracle existant affaibli. Dernière reprise : neuf tests,
8,319 s ; les sept autres fichiers verts ne sont pas relancés.

**Banc détaché lancé sur `0b60a91` :** vingt nuits de 4 h, cinq scénarios × 1985/7/42/2024,
deux travailleurs réduits, référence puis branche. Le cache local ne contient
aucune nuit compatible de la base 7e65907 ; les références manquantes sont calculées
une seule fois par le comparateur commun, rangées puis réutilisables. La sonde 219
reste celle de l'intégration (`101c6af25b`). Le lanceur versionné
`tools/banc_attention_conjointe.py` écrit un verdict par nuit : aucun surplus de
suspects, aucun plantage ou usurpation ; regards suivis, dixièmes de rotation, CPU
de la branche, appels et CPU inclusif des signes perçus et du choix d'attention.
Ces deux derniers temps se recouvrent et ne s'additionnent pas ; le CPU inclut
l'instrumentation. Aucun résultat de banc ni gain de performance revendiqué ici.
Processus initial **43552**, interpréteur enfant **33816**, tous deux constatés
actifs en `BelowNormal`, le 29 octobre à 22 h 05 (Paris), sans erreur de démarrage.
`demarrage.json` conserve le lancement ; reprendre sur **`fin.json`**.

**Limites.** Le joueur voit la direction mais la suit manuellement : aucune
rotation automatique de Corvus. Suivre une direction parallèle au regard du proche
ne vise pas sa cible depuis une autre position et ne garantit pas de la découvrir.
Les intentions anciennes sans direction restent lisibles selon leur ancien contrat
jusqu'au prochain regard décidé ; aucun historique d'orientation n'est inventé.
Le suivi ne remplace ni la fuite, ni un geste engagé, ni une garantie générale
d'absence de boucle. Bruts attendus : `C:/Users/msics/donjon/artifacts/regard-332/` ;
le fichier `fin.json` est écrit en dernier, y compris en cas d'échec.
