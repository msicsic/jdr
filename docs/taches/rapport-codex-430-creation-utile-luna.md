# Lot 430 — Création utile avec Luna : diagnostic

31 octobre 2026 — `codex-creation-utile-luna`, base `origin/integration` / `3ce68e2e`.
**L’admission confond le préalable interactif avec le résultat du geste.**
Diagnostic seul ; aucun code du jeu, scénario ou prompt modifié.

**Mesure.** Quatre archives présentes, dont le 421 copié : **14 fils lus,
13 dossiers de portée rejoués à l’identique sans modèle**, plus l’exception du 423
reproduite sur copie. Zéro appel Luna, originaux intacts. Les références `R…`
renvoient à `preuves.md` / `refus.json` : **57 occurrences et une exception**,
avec saisie, fichier, tour, événement, contrôle et `attendu` intégral. Le tableau
regroupe les refus centraux ; l’inventaire conserve aussi les refus périphériques.

| Lot, saisie ; preuve | Contrôle, champ et `attendu` résumé | Jugement et effet |
|---|---|---|
| 421, « je cherche une pierre pour caler une échelle » ; atelier T13, R06 | Moteur : `reperer.cible='pierre'` ; accepté : identifiant public (`cour_sol`, etc.) | **Juste pour ce candidat** ; aucun objet proposé. Correction en dialogue : aucune admission testée. |
| 422, « est-ce que je peux fabriquer une échelle… » ; atelier T3, dossier 03, R17 | Forme de portée : `usages` **2 pour 1 ajout** ; attendu : même réponse ou autre, aucun texte incriminé | **Rapport illisible**, rejet prudent justifié. Luna proposait bobine + `suite: assembler` ; une ficelle existe déjà. |
| 422, « et la torche, elle mesure combien ? » ; **materiaux** T4, dossier 05, R25–26 | Portée : `usages[0].perception_requise=true`, refus sur `proposition.ajouts[0]` ; attendu : perception sur `torche`, sans ajout. Puis `descriptions` **1 pour 0** | **Faux refus sémantique**, rapport également illisible. L’examen substitué ne donne aucune longueur. Ce cas est au Relais, pas dans le script atelier. |
| 423, « elles font quelle taille, ces planches de bac ? » ; avant/branche T3, dossiers 07/09, R29–30, R36–38 | Masse : 22 kg proposés contre 8 établis → ajuster dimensions/pièces ; puis même attendu perceptif sur `planches`, `descriptions` **1 pour 0** | Masse **justement refusée**, qualification corrigée **faussement refusée**. Même confusion descriptive sur le nombre restant (avant T8, R34–35). |
| 422, « je prends discrètement une planche… » ; lots T4, R23–24 | A4 : « vol ajouté », mais `etapes.0.operation=deplacer` déclaré conforme ; A5 impose ensuite `deplacer` contre `prelever` | Motif A4 **faux**, mauvaise attestation figée par A5 ; quantité finale fausse. Défaut historique déjà traité par 423, distinct de l’admission. |
| 423, même prise ; branche T4, R58 | Enrichissement des mains de `personne_1` préparé, puis `narration.attestations → rendu.decrire` : « Cet objet n’est pas visible » ; **`attendu` vide** | **Erreur du rendu**, pas refus d’admission pour PNJ invisible. Proposition hors sujet ; aucun prélèvement ni complément enregistré. |
| 427, « mj je ramasse pierre mouillée » ; Relais T1, dossier 10, R41–42 | Portée : perception requise malgré `suite: prendre` → action sur `antichambre_sol` ; `descriptions[1].capacites=['tranchable']` contre `[]` → déclarer/retirer | **Deux faux jugements** : matérialisation préalable prise pour découverte ; « tenir dans la main » pris pour coupe possible. Substitution : toucher le sol. |
| 427, « mj je ramasse éclat de bois » ; atelier T1, dossiers 11/12, R43–49 | Même portée ; rapports **1 description pour 2**, puis textes inversés. Moteur : `etablir_faits` sur `ambiance_afd028b799d6cf2f5e396678` ; A5 : conserver `prendre`, pas `examiner` | Portée **fausse** ; forme, matérialisation et fidélité **justes**. Les attendus de portée et du moteur se contredisent. Même blocage au préalable d’« examiner » (T3, R50–51). |
| 427, « mj je ramasse cette odeur de terre » ; atelier T4, R52–53 | Audit narratif : éclat manipulable sans matérialisation ; moteur : odeur non manipulable, attendu objet existant | Audit **faux** ; refus moteur **juste**. Référence cosmétique et objet moteur sont confondus. |

**Cause commune.** `compilation.schema_reponse` expose déjà `suite` ; les consignes
demandent qualification et matérialisation. Luna propose effectivement le paquet.
La portée reçoit demande, proposition avec suite, monde public et mutations
autorisées des objets, mais `usages` juge globalement demande et ajout : la
création devient une « recherche implicite ». Pour une qualification,
`descriptions=[]` sans dossier des champs à établir ; les cardinalités du rapport
ne sont pas fixées à l’entrée. Les erreurs repartent au compilateur, qui abandonne
le geste. La contre-revue physique n’est appelée qu’après une portée sans obstacle.

**Petit lot proposé, non réalisé.** Unifier l’admission préalable dans
`portee_narrative` (`contexte_admission`, schéma, `controler_usages`) et
`mj._appeler` / `_echanger_prepare` : dossier dérivé de la mutation autorisée,
propriétés établies/manquantes, suite non exécutée, correspondance exacte des
jugements. Contrôler les affirmations dépassant cette mutation, sans exiger sa
propriété nouvelle comme preuve préalable. Garder budgets, physique, fidélité et
consentement ; aucune exception d’objet ni consigne ajoutée à Luna. Vérifier
pierre/éclat et torche/planches dans la vraie boucle, sans ressaisie, état et rendu
après recharge ; contre-épreuves indice, absence inventée, capacité non déclarée,
masse incompatible et odeur ; une passe Luna ciblée.

**Limites.** Les 421/422 admettent déjà des qualifications : toutes les admissions
n’échouent pas. Les 13 rapports disent `indice=false` ; aucun vrai refus d’indice
n’y est éprouvé. Le classement du français reste sémantique ; l’invariant demeure
non garanti. R58 relève d’un défaut séparé. Bruts complets :
`C:/Users/msics/donjon/artifacts/creation-utile-430/` ; `fin.json`, aucun calcul restant.
