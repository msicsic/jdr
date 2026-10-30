# Lot 383 — S1c, approches, avertissements et secours

30 octobre 2026 · `codex-s1c-approches-secours` · base exacte `integration 1da5b943`.
`origin/integration` vérifiée avant les calculs : encore à cette base.

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

**Tests et mesures.** Les neuf tests de porte/AST ciblés passent après correction
d'une fixture de croyance qui omettait sa confiance. L'exécution initiale dans la
restriction Windows ne pouvait pas écrire les sauvegardes temporaires ; la reprise
hors restriction passe. Les quatre nouveaux tests de porte contrôlent copie/pureté,
identité des occurrences, ordre, absence de crochets, premier avertissement tenu,
constat strictement postérieur et réentrance du service. Les chaînes existantes
sont renforcées : captures réelles crue 223-22/26 puis rixe avec Gorm/Ilse ; postes
du Relais et de l'auberge ; état complet, ordre JSON, rendu, scène et paroles après
recharge, même laps entier/découpé. Vérification élargie ciblée puis **empreintes
2 h × quatre graines × Relais/mine/auberge/crue contre `1da5b943`** lancées détachées,
deux processus au plus et priorité réduite. Résultats encore attendus : ne pas
considérer l'identité des seize nuits comme acquise avant lecture de `fin.json`.
Pas de suite complète, ni Luna, ni conclusion de coût sur des temps issus du cache.

**Bruts et limites.** `C:/Users/msics/donjon/artifacts/s1c-383/` : `tests.json`,
`tests.log`, `empreintes-base.json`, `empreintes-base.log`, `fin.json` écrit en dernier.
Recouvrement potentiel 374 : `planification.reagir`, bloc des secours uniquement,
et imports voisins dans `pnj`/`deliberation` ; aucune localisation ni recherche modifiée.
Aucun fichier de 380/381 touché. Les lectures générales de violences, les croyances
et l'oubli par âge/importance restent hors lot. La validation finale des calculs
et la dernière vérification d'intégration restent à faire à leur réception.
