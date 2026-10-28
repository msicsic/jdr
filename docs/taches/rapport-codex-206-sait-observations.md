# Lot 206 b — Nouvelles utiles selon le locuteur

Branche **`codex-sait-observations`, non fusionnée**. Référence finale demandée
`881db69`, fusion `8178021`, moteur mesuré `26bd4d2` (même code moteur que la
fusion). Registres des réponses 221 et renoncements 225 conservés. Aucun Luna ;
deux travailleurs réduits au plus. Aucune clé configurée : commits non signés.
Bruts : `C:/Users/msics/donjon/artifacts/sait-206/`.

**Contrat livré, validation globale non acquise.** `social._auditeur` décide avec
les seules croyances du locuteur : paroles retenues, témoins perçus, corps
observé, engagements connus encore actifs, rendez-vous. `_connait_reception`
reconnaît une confirmation uniquement à la réception. `_nouveau` compare les
conséquences de l'eau (sec/mouillé/noyé, évolution), sans redire chaque centimètre.
Le point commun ne transmet pas une tendance privée ; hausse/baisse dite figure
dans les mots. `esprits` collecte les acquisitions visuelles communes et valide
`portee_a` ; `pnj._temoins` retient le geste public avant son interprétation.
Une rotation silencieuse du joueur ne publie rien. Hors fusions entrantes,
aucun changement dans `_abriter`, `deliberation.py` ou les modules interdits.

**Mesures finales.** Suite unique achevée : **2 502 tests / 290 fichiers,
15 échecs, une erreur, 16 ignorés** (`suite-881db69.json`). Les seize tests
subjectivité/utilité passent, ainsi que les avis redits, la mine 600 et l'abri
isolé. Témoins frais des quinze méthodes rouges, interpréteurs séparés : deux
échecs identiques sur la référence (voix supplémentaires, capture 219 disparue) ;
**treize échecs et une erreur introduits par la branche**. Aucun oracle réancré.

Vingt paires **4 h × cinq scénarios × quatre graines**, compteur 219
(`banc-881db69.json`, `synthese-881db69.json`) :

| Mesure, référence → branche | Résultat |
|---|---:|
| Confidences, Relais / Mine / Auberge / Crue / Hameau | 27/104/48/49/92 → 6/12/6/6/27 |
| Répétitions textuelles signalées (occurrences) | 34 → 18 |
| Demandes en boucle / avertissements redits | 0 → 0 / 6 → 0 |
| Retours suspects / entrées à expliquer | 4 → 5 / 59 → 52 |
| Cycles accomplis / préemptions / satisfaction d'autrui | 523 → 507 / 67 → 57 / 1 → 0 |
| États payés perdus / dérives ouvertes | 8 → 4 / 200 → 200 |

Zéro plantage/usurpation. **Critère « aucune nouvelle boucle » non atteint** :
Mireille, auberge 2024, 226, réessaie de servir Mathurine sans entrée nouvelle ;
Brune alterne agenda actif/sommeil neuf fois au hameau 2024 (contre huit fois
au hameau 42 sur la référence). Pas de comparaison des temps avec le cache.

**Scènes isolées, accord du superviseur, assertions conservées.** Constats :
Gorm faim 90 observée par Ilse ; verrou/réserve : tâche connue sur leur cible ;
brasero : froid cru, et froid réel 90 observé dans le découpage, auditeur occupé.
Arrivée après parole : Aubin cru affamé. Extinctions : projets connus de rallumer
les deux lampes de Lucien et la torche de Brune. Rumeur sur soi : naissance du
rachat isolée, comme la réclamation. Départ hors vue : demande connue pour
retrouver Ilse. Abri : projet financier né après l'arrivée isolé. Registre :
retour de disponibilité explicitement annoncé ; les révisions privées ne
rouvrent plus le fait dit. Recherche de phrase précisée pour distinguer une
confidence de son rappel. Deux tests de l'ancien mécanisme privé (`test_deja_dit`,
`test_avis_menace`) exigent désormais que la révision privée ne rouvre rien ;
ce changement d'assertion applique l'invariant demandé, sans réancrer les captures.

**Huit diagnostics demandés.** Mine 600 : première annonce omise à 0 sur l'ancienne
base, test maintenant vert. Avis crue 2024 : ancien grief choisi à 102 ; priorité
mécanique commune corrigée, cas 500/2024 verts. Oracle mine : décisions changées,
rouge sans réancrage. Auberge : première divergence de comportement à
**481**, lanterne d'écurie éteinte annoncée sur la référence, aucune annonce sur
la branche : Tilo est cru en cuisine éclairée, sans froid ni projet de lanterne.
La soupe du prototype était nouvelle mais inutile (pas de faim, engagement de 65
déjà tenu) ; la correction des projets clos la supprime aussi. Plans, visites
et rendus finaux identiques ; sauvegarde différente, jets **9 → 7**, quatre
paroles de moins. **Oracle gardé rouge sur instruction** : la projection des
seules preuves communes ne suffit pas. Abri : compagnon rejoint, puis vente de
torche distincte, scène isolée verte. Crue : Ilse trempée **1,025 ≠ 0**, non corrigé.
Tilo payé : clôture rétablie par 213 entrant. Capture 219 : épisode disparu,
désormais aussi sur la base finale ; détecteur synthétique vert.

L'annexe brute `diagnostic-final-881db69.md` explique chaque résultat rouge et
son témoin ; `diagnostic-auberge-881db69.json` contient le contexte exact.
Les anciens bancs `3aa16f7` et la passe `d7dbf1a` interrompue sont archivés,
pas employés comme validation finale. **Branche à examiner, pas une correction
validée à fusionner** : les conséquences sociales et les nouvelles boucles ne
sont pas toutes garanties par ce lot.
