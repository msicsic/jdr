# Lot 383 — S1c, approches, avertissements et secours

30 octobre 2026 · `codex-s1c-approches-secours` · base exacte `integration 1da5b943`.
Code mesuré `739e27eb`. `origin/integration` revérifiée à la conclusion : encore à
cette base, aucune fusion supplémentaire nécessaire. Branche poussée vers `origin`.

**Invariant et code.** Les approches observées, mises en garde, avertissements dus
et secours passent par les requêtes nommées de `donjon/memoire.py`. Les lectures
renvoient des copies profondes ou un booléen, sans créer d'esprit. Les opérations
`acquitter_avertissement`, `examiner_secours_constates` et `examiner_secours_du_lieu`
modifient les occurrences stockées, sans ajout, déplacement, remplacement ni crochet.
La première alerte reste sélectionnée même déjà tenue ; les cris sont examinés dans
l'ordre historique, doublons compris. Le constat garde la vue actuelle ou la date
d'état vu strictement postérieure au cri ; l'inspection garde son lieu effectif.
Les événements d'intervention et de service restent publiés par les appelants, après
l'acquittement. Le crochet réentrant du service voit donc l'alerte déjà tenue.
`defense`, `deliberation`, `relations`, `planification.reagir` et l'inspection de `pnj`
sont portés. Liste, plafond 40, clés, preuves, ordre JSON et crochets d'insertion
restent inchangés ; aucune nouvelle politique sociale ni intervention du MJ.

**Contrôle AST.** Douze accès retirés de la fixture S1a (**90 → 78**), sans nouvel
accès brut admis. Le contrôle des mutations de champs couvre les quatre familles
portées, leurs alias locaux, champs imbriqués, méthodes détachées et sélection par
`next` d'un générateur sur le stock. Il ne prouve pas tous les flux interprocéduraux
possibles de Python. Les autres familles de mémoire restent dans l'inventaire fermé.

**Tests.** **177/177 passent dans les quatorze fichiers ciblés**, sans échec, erreur
ni test ignoré (389,5 s écoulées, deux processus et priorité réduite). Les quatre
nouveaux tests de porte contrôlent copie/pureté,
identité des occurrences, ordre, absence de crochets, premier avertissement tenu,
constat strictement postérieur et réentrance du service. Les chaînes existantes
sont renforcées : captures réelles crue 223-22/26 puis rixe avec Gorm/Ilse ; postes
du Relais et de l'auberge ; état complet, ordre JSON, rendu, scène et paroles après
recharge, même laps entier/découpé. La première vérification isolée a nécessité de
sortir de la restriction Windows sur les fichiers temporaires et de compléter la
confiance d'une fixture de croyance ; aucun contournement dans le moteur.

**Empreintes.** **16/16 nuits identiques** : 2 h × graines 1985/7/42/2024 ×
Relais/mine/auberge/crue, chronique, mesures et empreinte de l'état final complet,
sans exclusion ni plantage, contre la base exacte `1da5b943`. Les seize références
manquantes ont été calculées une fois, puis rangées dans le cache partagé, comme
les nuits de la branche. Les avis auxiliaires restent identiques (neuf « à expliquer »,
aucun « non justifié ») ; aucune correction de ces avis n'est revendiquée. Calculs
séquentiels référence puis branche, détachés, deux processus au plus et priorité
réduite. Aucune conclusion de coût, aucune suite complète ni Luna.

**Bruts et limites.** `C:/Users/msics/donjon/artifacts/s1c-383/` : `tests.json`,
`tests.log`, `empreintes-base.json`, `empreintes-base.log`, `fin.json` écrit en dernier,
et `conclusion.json` (synthèse vérifiée).
Recouvrement potentiel 374 : `planification.reagir`, bloc des secours uniquement,
et imports voisins dans `pnj`/`deliberation` ; aucune localisation ni recherche modifiée.
Aucun fichier de 380/381 touché. Les lectures générales de violences, les croyances
et l'oubli par âge/importance restent hors lot. Tous les contrôles requis du lot
sont terminés ; aucune validation ciblée en attente.
