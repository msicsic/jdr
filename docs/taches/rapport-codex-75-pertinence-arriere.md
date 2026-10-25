# Lot 75 — pertinence arrière : arrêt au diagnostic (2026-10-25)

Branche `codex-pertinence-arriere`, **non fusionnée**, brief **313c458**.
Après `git fetch`, `origin/integration` **1171fc3** est déjà ancêtre de la branche
(base annoncée **6be0b80**, puis accord des lots 71/72) : aucune fusion requise.
**Aucun filtre livré : la cause annoncée n'est pas présente dans la capture prescrite.**
La tâche prévoit explicitement : « Si la cause n'est pas là, dis-la, chiffres
à l'appui, et arrête-toi au diagnostic. » Aucun moteur, coût, plafond, scénario
ou modèle modifié ; aucun appel à Luna ni intervention sur `main`.

**Mesure préalable**, capture `tests/data/cout-12h/auberge-1985-480.json.gz`,
réellement sauvée puis rechargée avant recherche. Les compteurs observent les
développements du générateur `gestes`, sans rappeler les buts ni modifier les suites.

| Faim à 480 min | Joss | Tilo |
|---|---:|---:|
| Nœuds examinés / états développés | 149 / 148 | 169 / 168 |
| États avec acquisition / acquisitions offertes | 0 / 0 | 0 / 0 |
| États avec fait `cherche` (Odile) | 133 | 153 |
| États avec faits de portes `ouvert` / `verrou` | 72 / 72 | 80 / 80 |
| Gestes `aller` offerts | 1 038 | 1 176 |
| Coût, identique à la complète `REFERENCE` | 15,3565909091 | 8,7004448622 |

Les deux résultats sont un plan en trois étapes : aller au cellier, y chercher
Odile, puis lui demander les vivres. Les seuls biens portables pertinents sont
`marmite` et `vivres`, par la clause `repas`. Aucun objet non visé n'est acquis :
la liste à expliquer est vide. `verrous` est bien vrai, mais aucun des deux PNJ
ne connaît de clé ou de crochet, ils n'ont pas la capacité de crochetage, et
**l'auberge ne contient aucun outil de choc ou de coupe**. La clause globale
ne peut donc pas y créer les acquisitions de hache/pioche décrites dans le brief.
Les portes franchies et la recherche projetée d'Odile, puis les promesses,
distinguent les états observés ; ils ne prouvent aucune acquisition inutile.

**Reprise effective 480–505**, cinq attentes du moteur, caches de recherche
initialement vides : **440 appels, 42 646 nœuds, zéro borne**. Aucun appel de
faim de Joss/Tilo, dont les intentions en cours persistent. Lucien totalise
**34 539 nœuds (81,0 %)**, surtout `garder:grenier` (14 798), `placer:ballot`
(12 260) et `garder:etable` (7 414). Anselme : 6 079 ; Joss : 1 759, sur
d'autres buts ; autres : 269. Cette reprise situe le calcul de cette fenêtre,
**pas la cause du surcoût général de 12 h**. Les chiffres du lot 62 décrivent
une autre version et une autre fenêtre ; ils ne se transposent pas à cette capture.

**Livraison et validation.** Outil `tools/mesurer_pertinence_arriere.py` :
clauses de pertinence, objets acquis/offerts, faits, gestes et diagnostics.
Commande : `python tools/mesurer_pertinence_arriere.py --minutes 25 --sortie
artifacts/pertinence-75/reprise.json`. Deux nouveaux tests verts (18,83 s) :
Joss/Tilo contre la complète ; avec/sans observation, attente réelle sur les
captures auberge **et mine**, mêmes plans, monde complet, texte, perception et
rendu après sauvegarde/rechargement. Suite complète unique à trois processus,
priorité réduite : **1 876 tests, 16 ignorés, 189 fichiers, aucun échec ni erreur**,
**1 726,02 s**. Le lot dépasse les 45 minutes en incluant cette vérification.

**Limites et suite.** P2 reste ouvert : aucune clôture ni preuve de conservation
des plans optimaux, aucun gain revendiqué. Il faut d'abord une capture issue
de la nuit lente mesurée, au moment d'une recherche plafonnée, et y distinguer
acquisitions, prix des moyens et autres faits projetés. Le plan documente le
contrat de clôture attendu, y compris les outils qui réduisent un prix sans
ouvrir de serrure. Les campagnes de validation d'une optimisation (empreintes
2 h, trois versions simultanées 12 h, `VERIFIER` continu) ne sont pas lancées
après cet arrêt au diagnostic, comme aux lots 62/63.
Bruts locaux : `artifacts/pertinence-75/` ; aucun résultat de référence rejoué.
