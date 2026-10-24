# Rapport Codex 31 — coûts exacts

Branche `codex-cout-exact`, **non fusionnée**, base **2590c4a**, brief **d4c8b66**.
Code signé SSH : **3b3b895**, **4773611**. Aucun appel Luna ; priorité réduite,
quatre travailleurs au plus. Aucune fusion ni campagne longue ajoutée.

**Invariant.** Mêmes décisions et même monde. `trajet_estime.moyenne` est gardée dans
la `Vue` figée : clé salle, cibles, sortie/contact, allure et possessions si métriques.
Géométrie, obstacles crus, corps et équipement sont propres à cette vue ; aucune reprise
entre vues. Horloge, positions réelles et faits du plan ne sont pas lus. Chaque reprise
contrôlée par `spatial.VERIFICATION` recalcule `_moyenne` et ses tables locales.
`Moteur.executer` et les opérations composées gardent `vue_memorisee` sur la transaction
jusqu'au bilan et au rendu : clés physiques/sociales existantes, retrait même sur
exception, aucune mémoire dans la sauvegarde.

**Diagnostic.** Profils cProfile propres, mine 42, 4 h : ancien, fusions Q, R, 25–27, 30.
`moyenne` : **31 284 appels**, **12,146 → 1,665 s**, **32,87 → 6,06 %** du profil.
La hausse joueur annoncée n'est **pas reproduite** : galerie, 48 transactions et
49 mémorisations par version, `_memoriser` 0,31–0,35 s. Départ natif ancien/base :
192 attributions de symboles de personnages, `_memoriser` 1,96/1,87 s. Le cache expire
avant les lectures finales du joueur dès l'ancien moteur ; aucun lot fautif attribué.
Profil final base → branche, galerie :

| Poste | Secondes cumulées | Part du profil |
|---|---:|---:|
| `_memoriser` | 0,305 → 0,329 | 0,83 → 1,20 % |
| `symbole_objet_cases` | 0,260 → 0,284 | 0,70 → 1,04 % |
| `noms.texte` | 0,076 → 0,019 | 0,21 → 0,07 % |
| `_designation_texte` | 0,060 → 0,0015 | 0,16 → 0,006 % |
| `_clore_bilan` | 0,224 → 0,099 | 0,61 → 0,36 % |
| Souvenirs de personnages | 0,229 → 0,080 | 0,62 → 0,29 % |
| `Monde.copier` | 0,579 → 0,675 | 1,57 → 2,46 % |
| `autour`, appels du banc seuls | 0,315 → 0,367 | 0,85 → 1,34 % |

Postes qui se recouvrent, temps déformés par le profileur. Départ natif : `noms.texte`
0,633 → 0,060 s ; symboles 1,79/2,06 s, toujours non réduits.

**CPU sans profileur**, trois versions lancées ensemble, sans cache de référence,
4 h, graines 42/1985 ; une exécution par version, moyenne par nuit (s) :

| Scénario | `42bb9c0` | `2590c4a` | Branche | Gain/base |
|---|---:|---:|---:|---:|
| Mine | 7,102 | 11,492 | 9,125 | −20,6 % |
| Auberge | 5,609 | 10,547 | 8,695 | −17,6 % |

**Vérification.** Empreintes 2 h, quatre scénarios × quatre graines : chronique,
mesures, état complet et traces de recherche identiques, nœuds compris, durées exclues
(agrégats rangés par PNJ/but ; ordre strict des recherches brutes). Même constat sur les
quatre nuits CPU de 4 h. `VERIFIER` + `spatial.VERIFICATION=1`, mine/auberge 42, 2 h :
aucun écart ni borne. Tests ciblés : clés, corruption, plans réels Relais/mine ; actions
simples/composées comparées au calcul pur, état/carte/texte après recharge.
Suite complète unique : **1 668 tests, quatre ignorés**, verte, **707,9 s**, trois processus.

**Limites.** CPU encore **×1,28/×1,55** contre l'ancien ; copies, symboles et lectures du
banc non réduits. Approximation du lot 30 et recherches bornées inchangées. Hausse joueur
à reproduire avec son protocole exact. Bruts/scripts du worktree : `artifacts/profil-*`,
`bilan-profils.json`, `empreintes-2h.json`, `diagnostic-*`, `verifier-2h.json`, `cpu-*`,
`tests-*.json`, `mesurer31.py`, `diagnostics31.py`, `cpu_ensemble31.py` ; références par commit.
