# Lot 313 — contact sans position connue

29 octobre 2026. Branche `codex-contact-inconnu`, **rouverte avant fusion**,
base `integration d76f272`. Moteur validé sur `5660366`, inchangé depuis.

**Invariant et correction.** Une portée insuffisante ou une case inconnue
ne prouve pas l'absence. `positions_crues.case_contact`, commun à
`pnj._case_crue` et `Vue.case_objet`, suit les seuls liens crus de contenant,
support ou porteur, avec arrêt sur cycle ; la chaîne prime sur l'ancienne
case du contenu. Aucun emplacement réel de mobile ne résout ce contact.
`_approcher` marche vers le point cru ou prépare l'observation dans le lieu
cru (salle, centre, tour d'horizon). `trajet_estime.approche` mesure ce
préparatif ; `_mesurer_direct` conserve le contrôle des présences projetées.
Le geste vérifie la portée physique ; `_hors_d_atteinte` ne dément la
présence qu'à un emplacement cru effectivement touché, hors d'un objet vu
ou d'un contenant fermé rencontré. `planifier_tache` et `echanges.empeche`
restent inchangés (lot 312).

**Chaîne complète.** Archives 308 absentes du poste : capture Relais 7
reconstruite sur la base à **856 dixièmes**, générateur versionné
`tools/capturer_contact_313.py`. Gorm croit les vivres dans la réserve,
sans salle/case propre : approche **0 → 30 dixièmes**, charge conservée,
puis service à Brune. Autre cas : source contenue dans une autre salle
à la mine. Services réussis, monde et textes identiques après six minutes
d'un bloc ou minute par minute ; monde/rendu/scène identiques après
sauvegarde/recharge. Source réellement déplacée : un seul démenti au
contact pendant six minutes, aucune portion servie ni nouvelle tentative
sur ces vivres. Sept régressions couvrent aussi observation, devis pur,
cycles et déplacement réel caché sans changement du premier pas.

**Validation.** **100 tests / onze fichiers verts**, 81,247 s ; deux tests
supplémentaires du lanceur verts. Douze paires **4 h × quatre graines**,
référence figée `d76f272`, puis branche ; deux travailleurs réduits,
854,913 s cumulées pour le banc. Douze références absentes calculées une
fois et rangées avec les nouveaux compteurs ; aucune référence relancée.
Ni Luna ni suite complète. Le premier lancement a échoué avant les tests ;
imports/cwd corrigés, initialisation protégée par le bilan final,
anciens journaux conservés. `fin.json` : **ok=true, codes 0/0**.

Valeurs **référence → lot**. Refus = geste rejeté par `_hors_d_atteinte` ;
interruption = `_approcher` renvoie `None`. Parts comptées dans la chronique.
P/h = maximum de passages d'un PNJ en une heure. Suspects = sonde 219.

| Nuit | Refus | Interruptions | Parts | Suspects | P/h |
|---|---:|---:|---:|---:|---:|
| Relais 1985 | 2→0 | 0→7 | 1→2 | 0→0 | 9→8 |
| Relais 7 | 1→0 | 0→0 | 0→1 | 0→0 | 10→7 |
| Relais 42 | 0→0 | 0→0 | 0→0 | 0→0 | 8→8 |
| Relais 2024 | 1→0 | 0→0 | 2→2 | 0→0 | 10→8 |
| Auberge 1985 | 0→0 | 0→0 | 3→3 | 0→0 | 20→12 |
| Auberge 7 | 0→0 | 0→0 | 2→2 | 0→0 | 12→12 |
| Auberge 42 | 0→0 | 0→1 | 3→3 | 0→0 | 15→15 |
| Auberge 2024 | 0→0 | 0→2 | 3→3 | 0→0 | 26→25 |
| Mine 1985 | 0→0 | 0→1 | 6→5 | 0→0 | 9→9 |
| Mine 7 | 0→0 | 0→1 | 3→3 | 0→0 | 9→9 |
| Mine 42 | 0→0 | 0→0 | 4→4 | 0→0 | 9→9 |
| Mine 2024 | 0→0 | 0→0 | 3→3 | 0→0 | 9→9 |

**Lecture et limites.** Refus matériels **4→0**, interruptions **0→12**,
parts **30→31** (Relais 3→5, auberge 11→11, mine 16→15). Relais 7 : Gorm
sert Brune à **1009**. Mine 1985 : Josse reçoit un biscuit de Bram à 114316,
au lieu du pain de Lucien à 115149 puis du service de Mathe à 115200.
Aucun plantage/usurpation ; bascules **0→0** dans chaque nuit. Maximum de
passages **26→25**, avertissements répétés **4→7**, appels à l'aide **3→1**.
La répétition d'appels Lucien/Hugues à l'auberge 2024 subsiste (déjà présente).
Avis à expliquer **11→14**, dérives ouvertes **186→161** : non certifiés bénins.
Relais 1985 : **cinq interruptions du même demander d'Ilse à Gorm**, aux
instants 141060 puis 141600/142200/142800/143400, avant son service à 143873.
Ce maintien sans progression reste une limite ; zéro suspect 219 ne
certifie pas l'absence de répétitions dans un plan inchangé. Une observation
insuffisante, notamment dans le noir, reste inconnue : ni recherche
exhaustive ni absence universelle de boucle garanties.

Bruts et analyse sans rejeu : `C:/Users/msics/donjon/artifacts/contact-313/`
(`tests.json`, `comparaison.json`, `mesures.json`, `analyse-cloture.json`,
`fin.json`). Aucun calcul actif, branche poussée vers origin.

**Complément avant fusion en cours.** La seule absence de suspects 219 ne
répond pas à la décision du 27 octobre : reprise seulement après entrée
nouvelle ou progression réelle. `tools/diagnostiquer_reprises_313.py`
rejoue uniquement les sept nuits concernées par interruptions ou hausse
d'avertissements. Il compare chronique/récit/mesures/souvenirs/état final
aux archives, capture les bornes précédant les interruptions (235 min pour
Ilse), vérifie monde/rendu/scène à la recharge, puis reprend les sauvegardes
effectivement rechargées. Les traces conservent positions crues, croyances
sans dates, perception, mouvements et origine des choix (filet ou éveil).
Bruts `contact-313/reprises-avant-fusion/`, bilan `fin.json` en dernier.
La cause des reprises et l'éventuelle correction restent à établir.
