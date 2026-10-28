# Lot 259 — présence au service d'une part promise

**`codex-presences-regression`, non fusionnée**, base `integration 7e69227`,
moteur vérifié `15d18c1`. Aucun MJ, scénario, `social.py`, `esprits.py`,
`agendas.py` ou `relations.py` modifié ; aucune Luna ni suite complète relancée.

**Invariant.** La présence nécessaire se juge au moment du geste, dans ses
lieux projetés. `pnj._a_reunir` et `planification._mesurer_direct` tiennent
compte de la venue convenue par le contrat existant d'une part demandée,
gratuite ou payée. Une localisation inconnue n'est pas une preuve d'absence ;
une localisation crue incompatible reste refusée, notamment Mathurine dans
la capture 251. Une pulsion spontanée de nourrir autrui ne vaut pas accord.
Le devis ne déplace personne et ne consomme rien ; l'exécution commune vérifie
encore présence réelle et parole avant de servir. `pnj.refus_etape` garde le
contrôle des participants supplémentaires, mais laisse l'approche et
l'observation ordinaires constater la disparition d'une cible de contact.
Aucun nouveau champ de sauvegarde ni connaissance privée du bénéficiaire lu.

**Tests : 310/310 verts**, exactement les 18 fichiers du journal et six voisins,
sans assertion affaiblie : 53 tests / huit fichiers en 62,807 s, puis 257 / seize
en 236,710 s, deux processus réduits. Nouvelle chaîne joueur/Ilse : demande,
engagement et plan rechargés, devis pur, absence sans consommation, venue,
service effectif, portions, clôture, mémoire/texte et rendu après recharge.
Captures Mireille/Mathurine et Mathe/Lucien du 251 toujours vertes.

**Suite du superviseur**, PC fixe, `dc326ad` : résultat transmis **2 655 tests,
un seul échec**, les 25 échecs/erreurs hérités de 251 disparus. Le seul test AST
`test_relations_socle.AccesTests.test_aucun_acces_direct_a_l_ascendant_hors_relations`
a été exécuté ici sur **7e69227 et dc326ad** : échec identique
`donjon/agendas.py:1054` (clé du bilan d'autorité), fichier et contrôle AST
inchangés par ce lot. **Préexistant, non corrigé ici** ; journaux `ast-base.log`
et `ast-branche.log`. Journal complet du PC fixe indiqué par le superviseur :
`C:/Users/msics/donjon/artifacts/suite-l259-dc326ad/suite.log`, absent du laptop.

**Banc achevé, code 0, 1 513,801 s**, cinq scénarios × quatre graines × 4 h.
Références `39db079` (avant 251) et `e875877` (251) : vingt nuits exactes
manquantes chacune calculées et rangées une fois ; vingt nuits de branche
calculées une fois, puis intégralement réutilisées pour la seconde comparaison
(états, chroniques, mesures et audits identiques). Aucun temps comparé entre
exécution et cache. Aucun plantage, usurpation ou violation dans les trois
versions ; deux travailleurs réduits au plus, aucun calcul actif.

| Scénario | Suspects avant 251 / 251 / 259 | S/F/D avant 251 → 251 → 259 |
|---|---:|---|
| Relais | 1 / 0 / 1 | 15,25/4,25/1,750 → 13,25/4,25/1,563 → 15,25/4,25/1,750 |
| Mine | 0 / 0 / 0 | 24,25/5/1,893 → 28,50/4,75/2,036 → 25,75/5/1,964 |
| Auberge | 1 / 1 / 0 | 9,50/4/1 → 11/4,25/1,063 → 9,25/4/1 |
| Crue | 2 / 1 / 2 | 20,50/6,25/2,813 → 18,75/6,25/2,750 → 20,50/6,25/2,813 |
| Hameau | 0 / 0 / 0 | 22,75/7,25/2,167 → 21,75/7/2,083 → 22,75/7,25/2,167 |

S/F/D : fonction `cats` du lot 183 inchangée ; moyennes des quatre graines,
PNJ inactifs compris. Totaux avant 251 / 251 / 259 : suspects **4/2/3**,
cycles **498/489/495**, à expliquer **51/55/53**, dérives **216/233/212**.
Aucune hausse de suspects par nuit contre l'avant-251. Contre 251, retours
des alertes déjà anciennes d'Aubin, Relais 2024 à 195 et crue 2024 à 38–39 ;
alerte Odile auberge 2024 supprimée. Attente urgente **565/400/565 PNJ·min**,
sans recours **0/0/0** : pas d'amélioration générale revendiquée. S baisse
contre 251 à la mine (28,50 → 25,75) et à l'auberge (11 → 9,25).

**Limites.** Une venue convenue reste une hypothèse du devis, sans garantie
sur l'arrivée ou l'ouïe futures. Les trois suspects conservés ne sont pas
certifiés bénins ; ni absence universelle de boucle ni identité avec l'avant-251.
Bruts : `C:/Users/msics/donjon/artifacts/regression-259/`, `bilan-final.json`,
`banc.termine.json`. L'échec initial du lanceur (import avant le bloc de fin)
a été corrigé dans les bruts, sans changement moteur ni rejeu des tests verts.
