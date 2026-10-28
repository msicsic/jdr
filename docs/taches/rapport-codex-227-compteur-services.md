# Lot 227 — Causes des pertes d'états payés

28 octobre 2026 — Branche `codex-compteur-services`, **non fusionnée**.
Départ `b8e433d` vérifié ; moteur identique à `881db69`. Outils et tests
seulement, aucun fichier de `donjon/` modifié, aucun Luna.

**Invariant.** Une perte n'est fautive que si le prestataire défait lui-même
le résultat, sans départ cru du bénéficiaire. `SondeAvis` observe `agir`,
l'exécution des gestes et les transitions physiques, relève l'état avant/après
et conserve les lieux/porteur crus **avant** le geste. Ce critère de départ
est celui de `biens.services_proteges`, lu sans appeler cette fonction qui
peut modifier les traces. Les quatre classes sont séparées ; une transition
non observée reste explicitement inconnue. Aucun délai ni entretien ajouté.
`audit_nuits` publie les compteurs par classe et réserve le niveau `violation`
à la première ; `comparer_bancs` affiche ces causes. Le total brut reste
disponible. Les archives anciennes sans cause ne deviennent pas des preuves.

**Six cas 224.** Rejeu des deux moteurs exacts `bd45f65` et `e4ba54e`, mêmes
graines, départs et placements que `comparaison-apres-213.json`, jusqu'après
chaque perte :

| Cas | Avant 224 | Après 224 |
|---|---|---|
| Relais 1985, 7, 42, 2024 | 4 gestes fautifs | 4 cessations physiques |
| Hameau 1985, 42 | 2 gestes permis, bénéficiaire cru parti | 2 gestes permis |

Les quatre pertes fautives deviennent donc **4 → 0**, bien que le total brut
reste **6 → 6**. Le cas 217, moteur `8177959`, joueur à son emplacement
initial, retrouve le geste fautif à 4824 après réussite à 4584.
Reprise de cette capture à 4584 : perte à 4875 sur l'ancien moteur
(ordonnancement repris), flamme conservée après 224 et sur le moteur courant ;
monde et rendus rechargés identiques avec/sans sonde dans les trois cas.

**Banc courant `881db69`, 4 h × quatre graines.**

| Scénario | Fautif | Prestataire, départ cru | Bénéficiaire/tiers | Physique | Inconnue |
|---|---:|---:|---:|---:|---:|
| Relais | 0 | 0 | 0 | 4 | 0 |
| Mine | 0 | 0 | 0 | 0 | 0 |
| Auberge | 0 | 0 | 0 | 0 | 0 |
| Crue | 0 | 0 | 0 | 0 | 0 |
| Hameau | 0 | 0 | 0 | 4 | 0 |
| **Total** | **0** | **0** | **0** | **8** | **0** |

**Vérifications.** **43 tests verts / trois fichiers, 104,740 s**, sans suite complète.
Reprise ciblée verte après contrôle de compatibilité des appels nommés.
Toutes les nuits rejouées comparent avec/sans sonde : monde complet,
empreintes, chronique, récit, souvenirs et mesures moteur. Les tests couvrent
les classes sur lumière, serrure et position ; la torche réelle et une serrure
d'auberge, ainsi que la marche hors exécuteur, contrôlent aussi monde,
`regarder` et `scene_percue` après recharge.
Un seul calcul à la fois, priorité réduite ; aucune suite complète du jeu.
Premiers bruts conservés dans `exploratoire/` ; cas historiques et nuits
antérieurs à la couverture de la marche repris après cette extension.

**Limites.** Le suivi garde les conditions d'état déjà reconnues par le
détecteur et sa première perte après réussite, même après oubli du paiement.
Un paiement ou une réussite jamais observés ne sont pas reconstruits.
La causalité est celle d'une transition sondée, pas une reconstruction de
toutes les causes antérieures. Une voie hors sondes reste `cause_non_observee`.
Comme le moteur, l'absence d'information de départ conserve la protection :
« présent » signifie ici « départ non établi », sans preuve de présence réelle.
Les autres limites du détecteur 219 demeurent ; aucune garantie générale sur
les boucles. Aucune clé Git de signature configurée.

Bruts et protocole : `C:/Users/msics/donjon/artifacts/compteur-227/`.
