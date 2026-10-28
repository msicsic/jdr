# Lot 243 — recherches de garde sous plafond

28 octobre 2026, PC fixe. Branche `codex-bornes-garde`, non fusionnée,
base d’intégration **c870c8b**. **Diagnostic seul : aucun code du jeu ni plafond
modifié, aucun Luna.** Deux calculs simultanés au plus, priorité réduite.

**Conclusion.** Limite reconnue, pas de violation silencieuse du contrat 48 :
les recherches jouées et uniformes plafonnent à 4 000 ; `_verifier` consigne
les absences dans `BORNES`. L’obligation d’égaler la complète concerne une
divergence optimisée/ancienne recherche. Ici leurs résultats sont identiques,
même sans H ni devis différés. Aucun certificat d’impossibilité n’est établi.

**Reproduction.** Rejeu historique depuis un worktree détaché de `4306c14`,
arrêté après les captures utiles de 435 et leur contrôle à 436 ; puis rejeu de
l’intégration jusqu’à 480. Départ tiré, auberge 42, joueur au dortoir ; spatial 0,2.
Contrôle du planificateur ciblé sur Lucien (430–436 historiquement,
435 sur l’intégration), sans changer ses décisions.

| État / garde | Recherche jouée | Complète uniforme, nœuds | Coût / résultat complet |
|---|---:|---:|---|
| Historique 435:0, grenier | 4 000, aucun plan | 7 071 | 126,36 ; rester |
| Historique 435:35, grenier | 4 000, aucun plan | 6 574 | 127,289407 ; revenir |
| Intégration 435:0, grenier | 4 000, aucun plan | 7 091 | 125,64 ; rester |
| Intégration 435:0, chambre chaude | 4 000, aucun plan | 11 139 | 108,316985 ; y aller |
| Intégration 435:292, chambre chaude | 4 000, aucun plan | 11 898 | 106,56 ; rester |

Les deux valeurs historiques du 231 sont retrouvées exactement. Sur
l’intégration, la première absence subsiste ; Lucien choisit ensuite une ronde
et arrive à la chambre à 435:292. Le retour au grenier demande alors
6 517 nœuds, coût 127,208105, mais `endurer=0` rejette aussi le plan complet :
ce `None` n’est pas une réponse perdue. Trois absences sont reconnues à 435.

**Cause générale.** La lecture de la lanterne d’Hugues passe à `faible=True`
à 435. Elle déclenche la découverte des moyens de lumière et multiplie les
états de recherche de porteur/lieu, ouverture/verrou et effets combinés.
Les recherches bornées historiques découvrent 5 164 / 4 999 états dans huit
salles. Les entrées périmées sont ignorées avant le compteur ; aucune
dominance sémantique entre clés différentes n’est prouvée ici. H=81,36,
constant, reste inférieur au séjour terminal à 126,36 : atteindre le grenier
ne suffit pas à conclure. H=80,64 sur l’intégration. Contre-épreuve sur
copies : la seule lecture « non faible » ramène la première recherche à
**336 nœuds**, historiquement et actuellement ; les deux recherches actuelles
de chambre à **656 / 663**. Aucun traitement particulier ajouté au moteur.

**Conséquences et vérification.** Historiquement, Lucien choisit immédiatement
la chambre (87,316659 puis 86,641187, moins que le grenier), qu’il atteint
à 435:136 : **zéro temps sans but imputable aux deux absences**. Il garde
ensuite jusqu’à 444:324 puis entreprend le service de Mireille.
Sur l’intégration, deux rondes de sécurité occupent 29,2 et 13 secondes :
**44 min 17,8 s sans intention entre 435 et 480**, dont 29 min 30,8 s
avant la seconde ronde à 465. À 440:292, la recharge confirme le besoin
`biens` en attente depuis 435 et aucune intention. Cette durée est observée,
sans prétendre avoir rejoué une trajectoire contrefactuelle sans plafond.
Cinq couples état/but recalculés après recharge ; une attente réelle produit
les mêmes monde, lignes, `regarder` et `scene_percue` depuis copie et fichier,
puis après sauvegarde/recharge. Autre cas : Joss, nourriture, attente persistée
et réveil par nouveaux moyens. **15 ciblés verts, 163,033 s**
(`test_borne_rester`, `test_attente_bornee`), aucun oracle modifié.

**Limites.** Aucune garantie générale de trouver un recours sous plafond.
Pas de suite complète, empreintes, coût mine ni contrôle exhaustif du
planificateur 8 h, conditionnés à un changement de code. Le contrôle ciblé
ne remplace pas le 231 ; ses 73 `ancienne_borne` ne sont pas recomptés.
Bruts : `C:/Users/msics/donjon/artifacts/bornes-243/` (sondes, captures,
analyses, rendus et tests) ; archive 231 conservée sans modification.
