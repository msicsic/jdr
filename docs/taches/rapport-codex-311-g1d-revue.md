# Lot 311 — G1 d, dernière reprise : mesure Luna à analyser

29 octobre 2026 — branche `codex-g1-compilateur`, **non fusionnée** ;
intégration `d58b343` fusionnée sans rebase (`1b16cdd`). Dernière reprise
décidée par l'utilisateur : aucune G1 e programmée. **Pas de verdict de fusion
avant la passe.**

`MJ._echanger_prepare` utilise un pipeline commun : préparation pure du dossier
(sans effet ni décision publiée), fidélité, puis admission. Une erreur calculée
pendant la préparation reste interne jusqu'à la décision de sens. Un obstacle
du monde rend ensuite son refus public directement, sans recompilation ni seconde
fidélité. Les corrections de forme et admissions de propriétés restent distinctes.
`couverture_action` porte le périmètre typé `sens/admission` : seul un écart de
sens peut refuser. Le dossier ne qualifie plus le candidat de « non admis » et
expose la proposition hypothétique sans sa justification. **Le périmètre reste
un jugement du modèle ; une mauvaise classification en `sens` reste possible.**

| Famille d'intention | Cause et contrat commun corrigé | Preuve hors réseau ; Luna en attente |
|---|---|---|
| Écoute | Confusion admission/sens, dossier à double statut | Objection `admission` ignorée ; écoute exécutée, état et rendu après recharge. |
| Passage, coup, prise hors de portée | Non-admission assimilée à absence de geste, puis boucle de correction | Une revue puis refus moteur, sans autre compilation ; deux gestes et deux sources de portée. |
| Expression sonore | Champs incompatibles, jet arbitraire pour expression | Une variante par effet dans le schéma commun ; expression/observation hors approches à jet. Deux sons émis, sans jet, enregistrés et rechargés. |
| Ambiance sensorielle | Règle de liberté déjà présente dans narration, omise par le compilateur | `REGLE_AMBIANCE` commune au récit et au compilateur ; deux sensations admises sans effet mécanique et persistantes. Le cas d'odeur est **relais/1**, pas crypte/1 (lumière). |
| Question au MJ / parole | Audience possible présentée comme parole déjà prévue | `parole_possible`, conditionnée au mode choisi, pour les saisies non explicitement parlées ; citations gardent `parole_prevue`. Deux questions ne créent aucune parole. |
| Mémoire, description, geste outillé | Garanties 296/304 à conserver | Tests ciblés conservés ; comparaison par famille attendue. |
| PNJ, avis, ressources, marché | Adresse et effets moteur à conserver | Simulations adaptées au périmètre et au catalogue conditionnel ; mêmes mots, auditeurs, état et rendu. |
| Mission et prix | Consultation distincte de proposition | Contrat 304 conservé ; prix et absence d'engagement restent à contrôler dans la passe. |

| Famille de refus | Situation locale ; aucune disparition Luna déclarée |
|---|---|
| Faux refus de fidélité pour non-admission | Ancien rapport sans périmètre illisible ; rapport annoté `admission` ne refuse plus le sens. |
| Paramètres du son, forme acoustique | Grammaire corrélée : cible, destination, catégorie et bornes de l'effet. |
| Issue improvisée / jet d'expression | Variantes avec/sans jet et approches autorisées ; ancien CHA/expression exclu. |
| Opération incompatible | Sens de `franchir` partagé avec le schéma d'action simple ; admission mécanique conservée. |
| Cible manquante, avis sur lieu inconnu, parole omise | Gardes conservées ; absence de nouvelles familles à mesurer sur les fils réels. |

**Vérification** : 211 tests distincts / 21 fichiers, **207 réussis, quatre
ignorés** (dépendances facultatives), sans suite complète. Résultats consolidés
par dernier passage de chaque fichier, sans compter les répétitions. Rejeu des
sept tours ciblés du 304 : quatre anciens verdicts faux (écoute comprise), trois
charges sonores exactes et témoins. Les anciens rapports n'ont pas le champ
de périmètre ; leurs annotations de test sont séparées, jamais présentées comme
de nouveaux verdicts Luna. Les archives n'ont pas de sauvegarde intégrale par
tour ; le rejeu des charges ne prouve pas une nouvelle réponse du modèle.
`Test-Json` confirme six charges contre les schémas anciens, nouveaux et
mutualisés : trois charges sonores anciennes et un témoin négatif exclus,
deux témoins positifs admis. Aucun appel au modèle pendant ces vérifications.

**Taille** : 80 466 / 81 874 caractères complets contre 90 759 / 93 305
(88,7 / 87,8 %), prompt 3 945, schéma brut 62 921. Aucun retour à l'ancien
interprète ni normalisation de sens ; les effets ne sont pas appliqués par le
texte. Narration, qualifications/faits et voies PNJ gardent leurs contrôles.

**Passe unique** : six scripts, copies, un travailleur réduit, référence
`230e7b3` précontrôlée et exclusivement en cache ; absence d'une référence =
arrêt, jamais rejeu. Admission, fidélité par famille (refus public fidèle
compris), abandons, familles de refus, prix, appels **≤ 3,30/tour**, secondes,
jetons et préfixe sont **à analyser**, sans extrapolation des tests simulés.

Bruts : `C:/Users/msics/donjon/artifacts/g1d-311/`, `tests-consolides.json`,
`rejeu-exact.json`, `grammaire-rejeu.json`, `taille-avant-luna.json`,
`precontrole-cache.json` et scripts ; fin attendue `fin-luna.json`.
