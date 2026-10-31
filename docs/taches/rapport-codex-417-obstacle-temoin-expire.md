# Lot 417 — renoncement et position expirée du témoin

31 octobre 2026, PC fixe · branche `codex-obstacle-temoin-expire` · base
`origin/integration 19b711bf` · moteur final **`bb5dfc5e`**.
**Code livré ; banc final en cours. Aucune fusion.**

**Invariant.** Une position expirée n'est pas un démenti de présence. Le juge
`deliberation.obstacle_patience` consulte la dernière preuve enregistrée, sans
en faire une position actuelle utilisable pour agir. Une consommation de piste
ne suffit pas non plus ; une absence apprise, une nouvelle localisation ou un
état constaté peuvent lever la cause. Aucun délai de réessai, aucune lecture de
la position cachée, aucun registre supplémentaire d'esprit.

**Chaîne commune.** `planification._normaliser_suites` conserve les gestes
préparés dans `contenu.suite_conditionnelle` des préfixes de contact ; `_couper`
y conserve aussi le suffixe arrêté après un geste incertain. Cette provenance
reste descriptive : seul le préfixe est exécutable, puis il faut replanifier
sur le constat. `renoncement_tient` parcourt ces gestes conditionnels ; un moyen
qui évite l'obstacle reste permis. `esprits.verifier` valide aussi cette suite
imbriquée à la sauvegarde et au chargement. `pnj._agir` partage la provenance
pour les plans sauvegardés qui vieillissent. Un guet engagé n'est plus remplacé
par la recherche d'un autre témoin alors qu'un témoin perçu bloque déjà le
geste ; avant un nouveau guet, le contrôle de position du 374 est conservé.

**Preuves et contrôles.** Les cinq oracles historiques de réessai restent
intacts. Les nouvelles preuves fonctionnelles passent :
Odon 31, expiration/consommation et départ caché distincts d'une absence apprise ;
préfixe réel rechargé, autre moyen et suffixe conservé ; Brune au guet, 34 minutes
entières ou deux laps de 17 minutes, état complet/rendu/scène identiques après
recharges. Le quatrième test vérifie le rejet d'une provenance corrompue par
l'`ErreurMonde` publique. **79 méthodes distinctes exercées : 78 vertes aux
derniers passages ciblés, une rouge préexistante ci-dessous**. Les résultats
sont répartis dans `tests-cibles.json`, `tests-complements.json` et
`tests-guet-final2.log` (six contrôles finaux verts, 18,4 s) et
`reessai-final.json` (7/7 verts sur le moteur définitif, 102,6 s).
Sur les sept méthodes du brief : six vertes, Gorm seul reste rouge.
Les premiers rouges sont conservés dans les bruts, dont deux ajustements
successifs de l'ordre du contrôle de position. Ni suite complète ni Luna.

**Limite distincte conservée.** `test_recours_agenda...capture_317_constat_et_laps_apres_recharge`
reste rouge dans les premières passes : déplacement de Gorm à 171 vers la galerie,
identique aux bruts du 414 sur `d54d15ae`. La capture et ses quinze minutes de
rejeu ne contiennent **aucun renoncement** pour Gorm : il termine une ronde,
cherche Ilse puis revient vers sa localisation apprise. Ce cas ne prouve donc
pas une reprise de renoncement ; son oracle n'est pas modifié et son trajet
reste à traiter séparément. Aucune absence générale de boucles n'est certifiée.

**Banc détaché.** Mine et auberge × 1985/7/42/2024 × 4 h, un travailleur réduit,
référence puis branche, cache partagé. La mesure préliminaire de `9418aba6`
avait commencé avant l'ajustement du contrôle de position ; elle est conservée
à part. Le banc final de `bb5dfc5e` attend sa fin et réemploie la référence,
sans rejouer les nuits déjà rangées. Suspects, appels, plantages et usurpations
restent à lire dans `banc-final.json` ; bilan final écrit en dernier dans
**`C:/Users/msics/donjon/artifacts/obstacle-temoin-417/fin-banc-final.json`**.
Deux travailleurs de tests/simulation au plus pour ce lot ; les coordinateurs
en attente ne simulent pas. Deux essais de tests ont été bloqués par les droits
des répertoires temporaires du bac à sable ; le lancement hors bac à sable a
fonctionné. Un premier lanceur de banc s'est arrêté avant simulation sur son
chemin d'import, corrigé avant le lancement effectif. Tous les résultats
conclusifs et diagnostics sont dans `C:/Users/msics/donjon/artifacts/obstacle-temoin-417/`.
