# Lot 308 — diagnostic des services après le 303

29 octobre 2026. Branche `codex-services-apres-303`, base `integration 36189aa`.
**Diagnostic seul : aucun code du jeu modifié.** Référence historique `79beaf1`,
archives et cache du 303 conservés ; aucun nouveau banc comparatif, Luna ou suite complète.

**Résultat.** Le solde **33 → 30** comprend quatre services disparus et un
supplémentaire. Deux disparitions évitent de nourrir Lucien déjà rassasié ;
une suit un changement de perception et de priorité. La quatrième expose deux
défauts antérieurs : devis de livraison et contact matériel.
L'alerte de Gorm n'établit aucune préemption injustifiée.

| Nuit | Premier choix divergent / première chronique divergente¹ | Portions et cause |
|---|---:|---|
| Auberge 1985 | 39 592 / 39 592 | 3 → 3 ; Mathurine cherche Tilo avant de servir. |
| Auberge 2024 | 135 926 / 135 956 | 3 → 3 ; Hugues cherche Mathurine. |
| Mine 1985 | 71 632 / 71 632 | 5 → 6 ; Rémy cherche Gaspard ; plus tard Lucien nourrit Josse avant Mathe. |
| Mine 7 | 100 800 / 100 800 | 5 → 3 ; Mathe demande Lucien à Bram, retrouve sa localisation, garde son parent puis clôt la charge satisfaite. Lucien mange son pain à 100 880 : faim **70,033 → 20,033**. Bram et Mathe ne donnent plus les deux parts de 100 976/101 005. **Attendu**, aucun bénéficiaire laissé affamé par ces deux suppressions. |
| Relais 1985 | 797 / 838 | 2 → 1 ; Aubin cherche Brune. Le service à Brune passe de 1 910 à 26 930. Seul disparaît celui d'Ilse à 141 000 : faim réelle **69,813**, contre **70,028** en référence ; Gorm ne la voit pas. Lorsqu'elle devient affamée et visible, le brasero a priorité sur le secours, puis elle sort de son champ perceptif. **Conséquence indirecte attendue** ; aucune charge de nourrir Ilse adoptée puis perdue. |
| Relais 7 | 760 / 856 | 1 → 0 ; Aubin cherche Brune. Gorm abandonne sa livraison à Aubin devenu inconnu, puis échoue à servir Brune à 856 : source hors de portée, sans case crue. **Défaut de contact matériel**. Brune achète ensuite une part à 1 300 et la mange à 1 587 : le compteur de services ne mesure pas toutes les alimentations. |

¹ Instants en dixièmes de seconde, depuis le départ. Les six autres nuits ont
des chroniques identiques. Les choix internes peuvent précéder le premier texte.

**Gorm, Relais 7.** À la minute 5, biens **69,124**, réserve verrouillée et
vivres en place : aucun rétablissement pressant à exécuter. Les deux candidats
`garder antichambre` sont des routines, palier **13**, avec plan vide ; le
secours à Aubin, palier **12**, vaut **44**, celui d'Ilse **22**. Même arbitrage
sur les deux moteurs. Le constat agrège un besoin chiffré et un motif différent,
sans vérifier qu'un recours prioritaire existe. Ses « 240 min » agrègent des
relevés, sans prouver un même but et une même case pendant toute cette durée.

**Deux petits lots proposés, sans les coder.** D'abord, un destinataire
inconnu ne rend pas une livraison impossible : sur la capture Relais 7,
`planifier_tache` renvoie `None` tandis que `_remettre` et `rejoindre`
proposent de demander Aubin à Brune. Même défaut sur la base ; la livraison
est annulée à 856 au lieu de préparer le contact. Contrat à aligner entre
`_devis_remise`, `planifier_tache`, `echanges.empeche` et l'annulation.

Ensuite, garantir qu'une position de contact
inconnue ou une cible trop loin ne vaut pas absence. Sur `servir vivres` et
`prendre vivres_2`, l'approche renvoie **0**, puis le geste **False** ; fournir
expérimentalement la case du contenant déclenche une marche (**30 / 76**
dixièmes). Ce défaut existe aussi sur la base. Fonctions :
`pnj._case_crue`, `_approcher`, `_hors_d_atteinte`, `trajet_estime.approche`
et leur contrat avec `Vue.case_objet`/`_mesurer_direct`. Préparer l'observation
ou hériter une position admissible du contenant, sans lire une position mobile
cachée ; conserver la charge jusqu'à un démenti réellement constaté.

**Questions et dérives.** Questions par nuit divergente, dans l'ordre du
tableau : **24→27, 5→32, 4→6, 0→1, 8→11, 1→3**. Dérives ouvertes :
**34→29, 9→19, 22→27, 15→15, 13→14, 4→17**. La sonde 219/271 ne classe
aucun retour `repetition_sans_entree_nouvelle` dans les douze paires ; les
trois rappels Lucien/Hugues restent justifiés par les indices/contact du 303.
La nuit Auberge 2024, rejouée sous sonde sans aucun écart aux archives,
compte **32 questions dont 16 déjà posées** : les 16 suivent une localisation
ou un repère de présence nouveau ; aucune ancienne réponse ne tient encore.
Une dérive ouverte désigne trois décisions distinctes sans retour, pas une
répétition certifiée. **Les 11 avis à expliquer et toutes les dérives ne sont
pas certifiés bénins** : aucun gain général de coût, de convergence ou de
services n'est revendiqué.

**Vérification et bruts.** Douze rejeux nécessaires, puis la sonde des questions
sur Auberge 2024 ; séquentiels, priorité
réduite : chronique, récit, souvenirs, mesures historiques et état final
identiques aux archives. **132 captures** : monde/rendu/scène identiques après
recharge. **48 reprises croisées** avant/après l'écart sur les deux moteurs, avec
comparaison de la minute suivante avant/après sauvegarde ; devis ciblés et
contre-épreuves séparés. Captures internes de diagnostic : ces reprises ne
remplacent pas une preuve universelle du découpage temporel. Bruts et scripts :
`C:/Users/msics/donjon/artifacts/services-308/` ; `fin.json` conserve le bilan
des nuits et `fin-cloture.json` celui de la clôture.
