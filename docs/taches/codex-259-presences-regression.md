# Tâche Codex 259 : la régression du lot 251 sur les parts promises

La suite complète lancée par le superviseur sur l'intégration `d626dec` (lots 251 à 254) donne **2 647 tests, 23 échecs,
2 erreurs** (journal : `C:\Users\msics\donjon\artifacts\regression-259\suite-d626dec.log`). La suite précédente
(`bf99943`) en avait 3, corrigés depuis par le lot 253. Le superviseur a vérifié la cause sur trois fichiers :
`test_corps`, `test_petits_correctifs`, `test_relations_graduees` sont **verts sur `39db079` (parent) et rouges sur
`e875877` (fusion du lot 251)**. Les lots 252 et 254 sont neutres (empreintes identiques) ; 253 ne touche pas ce chemin.

Le lot 251 (`docs/taches/rapport-codex-251-service-repropose.md`) a étendu à l'admission d'une étape les présences qu'elle
requiert (`pnj._a_reunir`, lu par `planification._mesurer_direct` et `pnj.refus_etape`). Les échecs montrent la dérive :
**une part demandée par quelqu'un qui n'est pas dans la salle des vivres devient « impossible »** (« Gorm ne voit pas
comment te donner les vivres du refuge »), alors que le contrat établi est que le donneur promet la part et la sert « là où
sont les vivres », le demandeur venant la prendre ; idem pour les parts payées, dettes, remboursements, intermédiaires,
voix inconnues, questions de localisation, combats et défenses qui reposent sur ce chemin.

## L'invariant
**Une présence requise par un geste se juge au moment où le geste s'exécute, sur les lieux projetés à cet instant du
plan : la venue convenue du bénéficiaire (attente d'une part promise, rendez-vous, service au lieu des vivres) la
satisfait dans le devis ; seule une présence crue impossible à cet instant rend l'étape inadmissible.** Le cas réel du 251
(Mireille sert Mathurine absente, sans aucune venue convenue, geste reproposé à l'identique) doit rester corrigé.

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le laptop** (l'utilisateur y travaille), au plus 2 processus,
priorité réduite.

**Fichiers autorisés d'avance** : `pnj.py` (`_a_reunir`, `refus_etape`), `planification.py` (`_mesurer_direct`), `echanges.py`
en raccord (devis d'une part promise ou payée) ; tous les fichiers de tests en échec du journal, **sans affaiblir aucune
assertion** : ils décrivent le contrat attendu. **Pas** : `social.py`, `esprits.py` (lot 255), `agendas.py`,
`relations.py` (lot 258), le MJ, les scénarios.

## Vérification
- Les 25 tests en échec du journal verts, plus `tests/test_service_repropose.py` (cas réel du 251) et les voisins des
  fonctions modifiées : lance **exactement la liste des fichiers en échec** plus ces voisins (pas de suite complète).
- Banc rapide 4 h, cinq scénarios × quatre graines, référence `39db079` (avant 251) et `e875877` (251) du cache si
  présentes, lancé détaché ; suspects et S/F/D rapportés contre les deux.

## Livraison
- Branche `codex-presences-regression` poussée. Rapport d'une page `docs/taches/rapport-codex-259-presences-regression.md` ;
  entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\regression-259\`.
  Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
