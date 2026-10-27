# Rapport Codex 199 — Mesure des retours de décision

Branche `codex-garantie-avis`, non fusionnée ; base `0fb5a07` (diagnostic 196).
Aucun fichier de `donjon/` modifié, aucun Luna. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/garantie-199/`.

**Invariant et fonctions.** `observer_avis` réunit la sonde du détecteur et restaure
ses fonctions même après exception. `audit_nuits.jouer_nuit` et
`comparer_bancs.jouer_nuit` observent chaque choix, sans attendre les relevés de
cinq minutes, y compris en mode empreintes. `ajouter_avis` enregistre
`avis_non_justifies`, `avis_a_expliquer`, `avis_cycles_accomplis` ; `avis` conserve
les comptes par PNJ et tous les exemples (minute, décisions, entrées changées,
classe). L'audit alerte dès le premier retour suspect ; une archive sans sonde
porte `avis_non_mesures`, jamais un zéro inventé. La sonde entre dans la clé du
cache et se charge depuis l'outil, même quand le moteur vient d'une autre branche.

**Relecture et correction.** Sélection 199 dans les bruts 196 : Gorm `crue 7`
(t=114600, garde/verrouillage et fermeture refusée sans récit), Brune `hameau 1985`
(t=122690, chaleur/évacuation et navette dans la conduite), Ilse `hameau 2024`
(t=25313, trois destinations d'abri). Leurs classes sont confirmées par les entrées
et la chronique. Six captures servent aux tests : trois retours suspects et trois
cycles accomplis (rondes terminées, sécurité apaisée). Ces derniers gardent désormais
leurs preuves, auparavant omises. Une entrée changée **ne prouve pas** la justification :
`justifie_par_entree_nouvelle` devient `entree_nouvelle_a_expliquer`, avec alerte.
Les classes `non_justifie_*` restent des observations suspectes.

**Départ : cinq scénarios × quatre graines × 4 h.**

| Scénario | Accomplis | Entrée changée, à expliquer | Non justifiés |
|---|---:|---:|---:|
| Relais | 109 | 7 | 0 |
| Mine | 101 | 12 | 0 |
| Auberge | 135 | 10 | 0 |
| Crue | 64 | 208 | 367 |
| Hameau | 121 | 78 | 18 |
| **Total** | **530** | **315** | **385** |

**Preuves et coût.** **20/20 identités avec/sans sonde** : état complet SHA-256,
empreintes, chronique, mesures moteur, récit et souvenirs ; comptes par PNJ,
exemples et alertes concordent. Les vingt états/empreintes sont aussi identiques
aux bruts 196. Leurs anciennes classes (364/272/594) précèdent la prise en compte
des prédicats de fin déjà corrigés sur la base : 62 retours d'abri et deux
d'inspection sont reclassés, soit 21 suspects et 43 à expliquer supplémentaires.
Cache `_IMPOSSIBLES` remis à froid des deux côtés du seul banc de vérification :
sinon le second passage profite du premier (mine 42 : 365/363 recherches neuves,
monde identique). Temps appariés : **590,37 s sonde et analyse / 590,15 s sans** ;
surcoût non distinguable du bruit, aucun gain revendiqué. Les anciennes nuits en
cache du comparateur ne contiennent pas les épisodes complets nécessaires.

**Tests.** **33 ciblés finaux verts**, dont écriture de l'audit, deux modes du
comparateur, sauvegarde/recharge et rendu joueur sur Relais et mine. Suite unique :
**2 343 tests, 271 fichiers, 31 échecs, quatre erreurs, 16 ignorés** ; parcours en
deux fragments (41 + 230), sans rejouer les fichiers terminés. Les **35 incidents**
sont reproduits sur la copie exacte de `0fb5a07` (33 méthodes, 26 fichiers, mêmes
identifiants et catégories). La suite générale n'est donc pas verte ; les outils
modifiés passent. Traces et bilans JSON dans les bruts.

**Limite.** Mesure déterministe et alertes livrées, **garantie générale non établie**
(`certification_complete=False`) : aucun certificat moteur de démenti, de palier
supérieur ou de marge suffisante. Les catégories ne donnent pas la dépendance exacte
aux candidats ; moyens sous un même but, dérives sans retour, retours > 60 min et
`fin` dans la photographie héritée restent hors observation. Une absence d'alerte
ne certifie pas ces cas. Aucune boucle corrigée ; les lots 196a–c restent requis.
