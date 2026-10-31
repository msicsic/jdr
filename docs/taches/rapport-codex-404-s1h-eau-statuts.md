# Lot 404 — S1h, preuves d'eau et statuts sourcés

31 octobre 2026 · `codex-s1h-eau-statuts` · base exacte `integration d451a4ce`.
Code soumis aux empreintes : **`88f4f9ab`**. Vérification détachée en cours.

**Invariant et code.** Les mesures d'eau (hauteur, niveau, pente, repère), les avis
reçus et les statuts passent par les vues profondes de `memoire` : `mesure_eau`,
`mesures_eau`, `avis_eau`, `statuts_connus`. `esprits.croyance` protège également
ces trois familles ; `prevision` rend une copie même pour un avis qualitatif.
Aucune consultation ne crée d'esprit, ne complète une preuve depuis le réel,
ne réapprend une information ni ne relance un jet. Zéro, faux et liste de statuts
vide restent des preuves négatives, distinctes d'une absence de preuve.

`memoire.prevision_propre/prevision/recevoir_prevision` et `recevoir_statuts`
portent les politiques historiques ; les anciennes fonctions restent façades.
La prévision propre conserve sa borne et la qualité de sa preuve la plus faible.
La réception des avis conserve date, poids × conviction, arrondi à douze décimales,
égalité refusée sauf départage de dispute, rang, chronique puis reconsidération.
Les statuts conservent date puis poids × conviction, égalité admise et validation.
L'admission commune remplace les cellules et retire durablement les avis antérieurs
à un constat propre étayé ; l'observation d'eau garde le même calcul de repère.
Stockage, ordre et sérialisation historiques inchangés ; aucun registre ajouté.

Lecteurs portés : `eau.eau_crue/borner/estimation/observer`, prévisions d'`esprits`
et cause de détresse liée à l'eau. Le contrat commun protège aussi les lecteurs
existants d'avis, de disputes et de statuts qui passent déjà par les façades.
Aucune fonction de passage du 381 ni terminal de remboursement du 399 modifiés.
Recouvrement possible avec 403 : modules et tests communs, sans correction de
ses rouges ni modification de leur scénario. `historique-lots.md` reste intact.

**Inventaire et tests.** Inventaire AST fermé : **168 → 129 expressions**, aucune
addition. Les contre-épreuves couvrent clés indirectes, alias, boucles et mutations
des trois familles. Le contrôle historique des statuts admet seulement les fonctions
de schéma/vue/admission de `memoire`, sans exemption globale du module.
**36/36 tests de porte verts** (71,1 s) : socle, localisation, quatre nouveaux tests
S1h. Copies imbriquées et preuve négative, retrait durable d'un avis et pureté sont
vérifiés. Deux captures historiques du 124 (crue 500, Gorm ; crue 2024, Ilse) :
dix minutes entières ou dix fois une minute avec recharges ; état complet et ordre
JSON, lignes, rendu, scène et registre des paroles identiques après recharge.
La persistance des statuts vérifie également scène et paroles au Relais et à la mine.

**Vérification restante.** Quatorze fichiers ciblés, puis **2 h × quatre graines
1985/7/42/2024 × Relais/mine/auberge/crue**, contre la base exacte `d451a4ce`.
Référence puis branche, cache partagé, deux travailleurs au plus, priorité réduite.
Le script écrit `fin.json` en dernier, y compris en cas d'échec ; sa présence ne
signifie pas que les contrôles sont verts. Aucune suite complète ni Luna.

**Bruts et limites.** `C:/Users/msics/donjon/artifacts/s1h-404/` : `tests-porte.json`,
`tests-cibles.json/log`, `empreintes-base.json/log`, `run404.py`, `fin.json` attendu.
L'identité des seize empreintes reste à confirmer avant clôture. Le contrôle AST
reste syntaxique et local, sans preuve exhaustive des flux interprocéduraux Python.
Pas d'unification nouvelle des arbitrages, d'oubli ou de jugement social.
