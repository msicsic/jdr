# Lot 213 (196 c) — examen préalable, non livré

Branche `codex-contrat-engagement`, non fusionnée. Base `cca5f50` présente
et ancêtre de HEAD ; aucun fetch ni merge nécessaire. AGENTS, état de
développement et rapports 196 (entier), 199, 201, 205, 209 et 195 (depuis
`origin/codex-pas-compagnons`) lus. Aucun fichier moteur ou test modifié,
aucun Luna. **L'invariant demandé n'est pas garanti ; ce document ne livre
pas une correction du lot 213.**

## Constat et contrat à rendre explicite

`choisir` ne conserve `courant` que si `intention["plan"]` est non vide.
Son hystérésis dépend ensuite de la réémission du même dictionnaire de but
par un candidat de même motif. `secours` ne génère ses propositions que
pour les corps actuellement perçus : la naissance et la poursuite n'ont
pas de contrats séparés. L'intention publiée ne conserve ni la provenance
du candidat ni son palier actif et sa raison. Les sous-buts d'agenda
peuvent ainsi perdre leur provenance lors d'une interposition.

La revalidation commune doit aussi distinguer l'inadmissibilité d'un
arbitrage de coût et d'une recherche incomplète. Dans `planification.chercher`,
les issues internes `borne`, `attente`, `epuise`, `impossible` et `endure`
aboutissent toutes à un résultat public `None`. `_endure` peut écarter un
trajet trouvé sans prouver sa cible impossible. Une absence de candidat ou
de plan ne constitue donc pas, à elle seule, une preuve de démenti.
Inversement, conserver le plan ancien sans revalidation ne prouverait pas
l'absence d'entêtement. Aucun de ces raccourcis n'a été implémenté.

Le raccord envisagé doit exposer une évaluation typée de **la cible adoptée**,
indépendante du choix d'une nouvelle cible : accomplissement, admissibilité,
blocage attesté, recherche indéterminée et coût d'alternative. La provenance,
la raison active et l'urgence doivent rester des données rechargeables de
l'intention ; les quatre sorties sont arbitrées dans `choisir`. Les
prédicats restent ceux des mécaniques communes, sans copie du planificateur
dans la délibération. La forme exacte de ce raccord et son étendue ne sont
pas établies dans cette tentative ; aucune nécessité de toucher les fichiers
interdits n'a été démontrée.

## Vérification et limites

Captures et scripts de 209 consultés, notamment son inventaire et ses
captures représentatives. Le classement de 209 reste une information
historique : secours/perception et stabilité des cibles relèvent du contrat ;
préemption d'une ronde par secours ou d'un secours par rendez-vous peut être
légitime ; localisation cachée et restauration des charges restent hors lot.
**Aucune reproduction exécutée sur la base actuelle n'établit encore cette
attribution**, ni la cause des activations d'a1 de Brune et de l'absence de
but de Gorm signalées par 205.

Une reproduction de vingt nuits de base a été achevée avec
`comparer_bancs.py --reference cca5f50 --branche cca5f50`, cinq scénarios,
quatre graines, 4 h, deux travailleurs à priorité réduite. La référence
exacte est désormais en cache ; le second côté relit les vingt nuits sans
les rejouer. Compteur 199 : **Relais 0, mine 1, auberge 5, crue 9,
hameau 9, total 24**, aucun plantage. L'archive et le journal sont dans
`C:/Users/msics/donjon/artifacts/engagement-213/base.json` et `base.log`.
Le banc avait terminé lorsque son arrêt a été demandé ; aucun travailleur
de cette invocation n'était encore à arrêter.
**Aucune baisse du compteur 199, aucune preuve nouvelle de
recharge ou de laps découpés n'est revendiquée.** Pas de suite complète :
aucune implémentation à valider. Aucun fichier interdit, y compris
`_lieu_cru` et `salle_crue`, modifié. Aucune clé de signature Git configurée.

La tentative s'arrête avant correction ; une reprise doit établir le contrat
de revalidation, puis exécuter toutes les preuves du brief. Elle ne doit pas
considérer ce diagnostic comme un lot 213 terminé.
