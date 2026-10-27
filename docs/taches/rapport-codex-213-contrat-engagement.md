# Lot 213 (196 c) — contrat partiel, non fusionnable

**Branche `codex-contrat-engagement`, non fusionnée.** `cca5f50` vérifié ;
211 puis **`3aa16f7` (219)** fusionnés avant le dernier banc. Moteur figé après
217 (`b215938`). Aucun Luna ; deux travailleurs au plus, priorité réduite.
Commits non signés : aucune clé configurée. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/engagement-213/`.

**Contrat implémenté.** `choisir` revalide avant d'arbitrer, même à plan vide.
Une intention revalidée cède à un palier supérieur ou à la marge commune
`INERTIE + VOL/4`. Naissance et poursuite des demandes de condition/agendas sont
séparées ; le secours peut continuer hors de vue sur sa détresse crue. Un geste
manqué libère l'ancien engagement avant la nouvelle planification. La façade
`agendas.py` conserve, liée à l'intention exacte, identité/parent, fin, raison crue,
phases et dernière sortie attestée avec faits. Aucun agenda de secours ajouté.
Une évaluation indéterminée reste distincte d'une fin. **217 appliqué** : aucun
coût passé ni minutes ajoutées aux points d'urgence ; le coût futur de bascule
n'a pas encore de raccord explicite, les coûts des moyens restent au planificateur.

**Preuves.** Huit tests du contrat : captures réelles 209 Rémy/Mireille, Relais
1985 de 211, secours hors de vue, froid dans un autre scénario, ronde préemptée,
démenti, plan vide, VOL et sorties persistées ; monde/rendu après recharge et
laps entiers/découpés identiques. 35 ciblés distincts avant fusion, **40 verts
après 219/214**, puis trois de projection historique verts. Seuls
`deliberation.py`/`agendas.py` diffèrent de l'intégration en production ; AST de
`_lieu_cru`/`salle_crue` inchangés. Le retour d'Aubin au Relais 2024 n'est plus relevé.

**Banc final : 20 paires de 4 h**, cinq scénarios × 1985/7/42/2024, compteur 219.
Référence exacte absente du nouveau cache : calculée une fois puis rangée.
Classes : **suspects 13 → 5**, cycles accomplis **486 → 484**, préemptions par
palier supérieur **57 → 52** (légitimes), satisfaction/démenti par autrui **1 → 0**,
progression observée **0 → 0**, à expliquer **97 → 63**. À part : dérives ouvertes
**185 → 192**, états payés perdus **7 → 6**, sans durée contractuelle inférée.
Zéro plantage/usurpation. Attente/sans recours/eau : moyennes PNJ·min ; S/F/D : 183.

| Scénario | Suspects | Attente / sans recours | Eau | S/F/D avant → après |
|---|---:|---|---:|---|
| Relais | 3 → 0 | 0/0 → 0/0 | 0 → 0 | 11,25/3,75/1,5 → 9,75/3,5/1,438 |
| Mine | 1 → 1 | 0/0 → 0/0 | 0 → 0 | 22/4,25/1,607 → 25,5/4,5/1,964 |
| Auberge | 2 → 2 | 0/20 → 0/20 | 0 → 0 | 12/4,25/1,063 → 11/4,25/1 |
| Crue | 2 → 2 | 178,75/0 → 170/0 | 2,5 → 3,75 | 14/6,75/2 → 17/6,75/2,375 |
| Hameau | 5 → 0 | 128,75/0 → 178,75/0 | 10 → 31,25 | 31/8/2,542 → 31,25/7,75/2,5 |

**Suite complète finale : 2 433 tests, 11 échecs, zéro erreur.** Reprise ciblée des
mêmes méthodes sur `3aa16f7` et la branche : deux échecs Mimo préexistants ; deux
empreintes historiques corrigées pour exclure le registre ajouté (plans/vues et
recharge intégrale restent contrôlés, trois tests verts) ; **sept écarts propres
à la branche non résolus** : flamme, distribution des vivres (deux), réponse
d'Odile, bois de la mine, prix refusé, finances. Six mondes d'incident rechargés
avec monde/rendu/scène identiques. Aucune suite verte revendiquée. Les passages
antérieurs sont archivés ; après 219/214, aucun fichier de production commun
avec 213 depuis la base : ciblés supplémentaires, aucune nouvelle suite complète.

**Limites bloquantes.** Les cinq suspects restants : trois après `MANQUE` et deux
retours d'a1 en crue (42/2024), dont la trace montre une sortie indéterminée puis
renaissance. `None` du planificateur ne distingue pas borne/coût/impossibilité ;
les sources sans demande persistante doivent réémettre leur cible. **La liste
fermée des sorties n'est pas garantie.** Brune hameau 42 reste 110 min dans l'eau :
préparatif reproposé après refus d'exécution « séjour en péril d'eau » ; accord
planification/exécution à corriger, pas de cas particulier ajouté. Nouvelle
répétition de lectures en mine 7, alternance d'observation au Relais 2024 ; aucune
absence générale de boucle/entêtement validée. A1 hameau 2024 : activations/sommeils
5/6 → 4/3 ; Gorm hameau 1985 sans but 165 min, classées confiées/attente, ne prouve
pas seul une intention perdue. **218** reprend la suspension temporaire non portée
ici (Gorm ouvre sa réserve pour Aubin, hameau 1985 min 6). Ne pas fusionner :
arbitrage requis pour élargir l'admissibilité commune à l'exécution (`pnj.py`,
interdit par le brief), puis résoudre les écarts et fermer les sorties indéterminées.
