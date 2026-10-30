# Lot 371 — évaluation du noyau de l’échéance

Branche `codex-evaluation-echeance`, base `origin/integration d8567324`, PC fixe
`MSI-DESKTOP`. **Mesure seule : aucune règle, aucun prompt ni test modifié.**
Le script reproductible est `tools/evaluation_echeance_371.py` ; les bruts sont dans
`C:/Users/msics/donjon/artifacts/evaluation-echeance-371/`.

**Parcours joueur.** Copies contrôlées du cas 347/1.2 (huile d’Odile) et des planches
d’Aubin au Relais, supports existants, jet d’accord fixé à 20 ; aucune reprise
de la nuit historique à la minute 619. Dans les deux scènes :
**7 saisies terminal ou 9 clics web**, confirmation comprise, zéro appel modèle.
Le catalogue contient respectivement **57 et 17 prestations** sur cette base.
Le libre simulé ouvre le formulaire en un appel, puis `valider` et `tenter`
concluent le même accord que le direct ; **ceci ne mesure pas Luna**.

Livraison et retard : état/rendu comparés après recharge, en bloc et par laps découpés.
Huile livrée à **2,6 s**, planches à **3,6 s**, avant la limite de dix minutes ;
or 50 → 47. La lanterne s’épuise ensuite : alimenter puis allumer consomme la
part livrée et laisse 119 minutes de combustible, sans nouvel achat.
Prestataires suspendus : clôture à **6001 dixièmes**, remboursement unique 47 → 50,
aucune dette restante malgré deux soldes. Une remise volontaire ultérieure ne
change ni ce solde ni le verdict historique. État en bloc/découpé identique ;
**messages différents à l’auberge**, notamment « quitte la pièce »/« aperçois un
instant » pour Odile autour de l’extinction. Livraison, verdict et rendu final
rechargé identiques ; parité générale des messages non garantie : anomalie non
attribuée (`jeu.json`). Relais et expirations : mêmes messages.

**Banc autonome.** 4 h, graines 1985/7/42/2024, départ tiré, Corvus passif dans les
salles du banc usuel. Sondes sur les opérations réelles `demander`/`proposer`/`engager` ;
photographies des prestations promises, puis devis E3 à dix minutes sur copies.
Une occasion **ne prouve pas qu’un délai améliorerait l’issue**. Seules les
prestations payées relèvent actuellement d’E4.
**12/12 nuits sans plantage ni usurpation**, états relus identiques. Fréquences :

| Scénario, 16 h observées chacun | Prestations | Dont payées | Nuits concernées |
|---|---:|---:|---:|
| Auberge | 13 | 6 | 4/4 |
| Relais | 18 | 7 | 4/4 |
| Mine | 13 | 6 | 4/4 |

**44 occasions sur 48 h**, dont **19 payées** ; les 44 devis sont crédibles dans
dix minutes, durées **0,22–2,23 min**, dont **17 > 1 min**. Exemple transférable :
Bram → Josse, biscuits à la mine ; marchand → Aubin, vivres au Relais.
`analyse-banc.json` conserve chaque cas. Aucun délai négocié spontané observé.
Auberge, graine 7, minute 187, Mireille promet de remettre
`marmite_2` à Tilo, puis vend le service de cette même part à Mathurine pour une
pièce ; remboursement 233 dixièmes après le paiement. Ce conflit de prestations
ne démontre pas qu’un délai plus long serait utile (`auberge-7.json.gz`).

**Vérifications et limites.** **91 tests verts**, neuf fichiers E1–E6 et voisins
(parts, lampes, tâches), zéro échec, erreur ou saut, **586,3 s** (`tests.json`).
Assertions inchangées ; deux travailleurs au plus, priorité réduite. Incidents
d’écriture temporaire sous bac à sable conservés, puis reprise réussie.
Ni suite complète, nuit longue, référence rejouée ou comparaison CPU.
Le brief demande une passe Luna puis dit « ni Luna » dans sa vérification :
cette dernière consigne est retenue. Douze scripts ciblés et la commande d’une
seule passe sont déposés dans `luna-a-jouer.ps1`, **non exécutée** : accord sans/avec
correction, annulation, demain, paiement futur, maintien. Les faux refus du
[lot 364](rapport-codex-364-e6-libre-vers-formulaire.md) restent non revalidés.

**Recommandation.** Stabiliser d’abord E6, le catalogue (recouvrement avec **365**)
et qualifier la différence de messages ; puis **E7, suivi d’un E9 borné à une
alternative sur sollicitation/refus de délai**, à arrêter sans choix utile nouveau.
Les 17 devis > 1 minute motivent cet essai, sans gain autonome démontré.
**Reporter E8** : aucun besoin de révision d’un accord daté démontré ici.
Aucun recouvrement de code avec 369/370/372, non inclus dans cette base.
Questions à l’utilisateur : jouer Luna malgré la contradiction du brief ?
Autoriser l’ordre E7 → essai E9, E8 différé, après stabilisation, ou arrêter ici ?
Calculs terminés (`fin-lot.json`) ; branche poussée, fusion au superviseur.
