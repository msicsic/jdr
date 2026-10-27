# Lot 224 — Ne pas défaire le résultat d'une parole de service

28 octobre 2026 — Branche `codex-service-non-defait`, **non fusionnée**.
Base `a22f92e` vérifiée ; intégration du 213 `bd45f65` fusionnée par `0192bb3`
à la demande du superviseur. Code 224 `456ff6a`, puis `e4ba54e` ; aucune clé
de signature configurée. Aucun Luna.

**Contrat.** `echanges.tenu` conserve qui a promis quel état à qui, au constat
qui clôt la parole. `biens.retenir_service/services_proteges` gardent cette trace
dans `services_rendus`, sauvegardé et validé, indépendamment du souvenir borné.
Les engagements ouverts couvrent aussi l'intervalle avant ce constat.
`planification._normaliser_suites` filtre les transitions qui défont un résultat
obtenu, après les approches et les portes franchies, suites différées comprises.
`_entrees_communes` inclut les entrées de ce filtre dans les caches ;
`deliberation.menager_flamme` emploie la même protection. Les gestes pour obtenir
le résultat restent offerts. Le patch contre `bd45f65` ne change que les quatre
modules permis et un fichier de tests ; les fonctions du 213 restent intactes.

**Lecture du besoin autorisée.** Présence crue du bénéficiaire auprès de l'état,
ou portage cru de l'objet ; aucune lecture de ses buts privés. Un départ cru
ou un état constaté défait termine la protection, sans délai ni obligation
d'entretien. Un bénéficiaire présent qui n'en a plus besoin reste protégé ;
une croyance de lieu fausse peut libérer à tort. Aucune parole typée existante
ne libère spécifiquement ces états. Les anciennes paroles déjà clôturées sans
trace ne sont pas reconstruites rétroactivement.

**Preuves.** Sur la base initiale, cas réel 217 reproduit : Brune allume à
**4584 (7 min)** et éteint à **4824 (8 min)**. Reprise corrigée de la capture à
4584 : flamme conservée jusqu'à 10 min, monde, `regarder` et `scene_percue`
identiques après recharge, même laps en bloc/découpé. Six nouveaux tests :
ce cas, départ réel ignoré puis départ cru libérant l'extinction, serrure
d'auberge promise ou payée par le joueur, porte franchie, clé posée, éviction
du souvenir, état défait et combustible épuisé sans dette ni entretien.
Ces six tests passent après fusion du 213.

**Banc final : vingt paires de 4 h contre `bd45f65`**, cinq scénarios, quatre
graines, compteur 219. Référence calculée une fois puis rangée en cache.

| Compteur | Référence | Branche |
|---|---:|---:|
| État payé perdu, brut | 6 | 6 |
| Cycles accomplis | 468 | 456 |
| Préemptions légitimes | 53 | 51 |
| Retours suspects | 5 | 5 |
| À expliquer | 61 | 56 |
| Dérives ouvertes | 196 | 193 |

**Le critère de baisse du compteur brut n'est pas atteint.** Quatre extinctions
précoces du Relais sont évitées ; le compteur relève ensuite l'épuisement naturel
du combustible, ce qui conserve leur nombre. Les deux extinctions du hameau
restent permises : Brune croit Ilse/Maël dans l'échoppe, torche dans l'antichambre
(captures des croyances dans les bruts). Aucun compteur de retour n'augmente
globalement ; zéro plantage, aucune usurpation détectée. Aucune absence générale de boucle garantie.

**Coût mine, 4 h, 1985, départ fixe :** tous les compteurs déterministes identiques,
**567 recherches, 8 383 nœuds** ; CPU indicatif 18,12 / 18,42 s, calculs successifs.
**Suite complète après fusion : 2 459 tests / 285 fichiers, 2 314,709 s,
deux travailleurs réduits, deux échecs MiMo, zéro erreur.** Les deux assertions
`6 != 5` sont reproduites sur `bd45f65` (deux méthodes seulement, 2,192 s).
La passe commencée avant l'annonce du 213 a été arrêtée sans bilan final ; les
mesures antérieures restent exploratoires. Aucun code changé depuis le banc final.

Bruts exclusivement `C:/Users/msics/donjon/artifacts/service-224/` :
`comparaison-apres-213.json`, `cout-mine-apres-213.json`, `suite-apres-213.json`
et `protocole.json`. Vérification au-delà du créneau du lot.
