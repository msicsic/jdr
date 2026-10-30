# Lot 358 — revalider une action différée après refus

Branche `codex-revalider-apres-refus`, base **`integration a3855ad9`**.
**Vérification en cours ; livraison non encore validée pour fusion.**

**Invariant.** Une réponse refusée encore valable s'applique au prochain geste
d'un plan conservé comme à celui d'un nouveau plan. `pnj.refus_etape`, déjà appelé
au choix et par `agir`, consulte désormais `deliberation.refus_geste`. Cette
fonction traduit les opérations typées en demandes (bien, enquête, tâche,
mandat, feu, marché) et réutilise les juges existants des refus/offres. Aucun
nouvel essai, parole, jet ou perception au contrôle. Ni scénario ni prompt
modifié. Les règles de levée restent intactes : moyens/croyances, mandat
distinct, hausse de prix et meilleure contrepartie ; le délai seul ne lève
pas une impossibilité. Un préparatif d'observation reste possible avant le
suffixe social ; le suffixe est contrôlé lorsqu'il devient le prochain geste.

**Preuves.** Capture 306 originale à **t=4200**, plan de Gorm datant de minute 4,
refus de Maël minute 6 : refus d'admission et `MANQUE` avant toute réexécution,
sans modification de l'état, sans parole ni geste. Fixture compressée sans
retouche (`tests/data/refus-358-hameau-1985-4200.json.gz`), SHA-256 du JSON brut
`1529ca9f54e17c0c16de2d2d98e85a04b0bd7d3cdcc66065229885f4630c004a`.
Autre scène : tâche payée impossible de Mireille à Mathurine à l'auberge,
préparée avant sa réponse, conservée au-delà de `REDEMANDE`. Les tests contrôlent
monde complet, rendu, scène et écoute après recharge, reprise en bloc ou par
demi-minutes, plus les nouveaux moyens et les termes distincts.

**Vérifications lancées.** Onze fichiers ciblés/voisins, deux processus réduits,
puis version finale des huit régressions du lot ; banc 4 h × quatre graines ×
Relais/mine/crue, référence `main` en cache, branche seule hors cache.
Le lanceur détaché enchaîne ces calculs ; fin écrite en dernier :
`C:/Users/msics/donjon/artifacts/revalider-358/fin.json`.
Les erreurs initiales de harnais (temporaires Windows, horloge flottante,
croyance absente et chronique bornée) restent dans les précontrôles bruts.
Un nouvel apprentissage peut légitimement permettre un autre mandat après
4200 : la reprise instrumentée vérifie chaque réexécution contre le refus
alors valable, sans imposer le gel des croyances.

**Limites et intégration.** Mesures finales et éventuels échecs voisins à
instruire après le fichier de fin ; aucune conclusion de banc anticipée.
Le lot ne prouve pas l'absence générale de boucles ni le changement des règles
de refus existantes. Recouvrement **335 : `donjon/pnj.py`**, limité ici à
`refus_etape` ; `agir`, `planification.py`, `trajet_estime.py` et `agendas.py`
inchangés. Ni Luna ni suite complète. Bruts dans `artifacts/revalider-358/`
du dépôt principal, précontrôles aussi dans le worktree.
