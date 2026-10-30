# Lot 316 — réveils historiques et indépendance du hachage

Branche `codex-hachage-reveils`, base intégration `60f857c`, **non fusionnée**.
Lot terminé, aucun calcul actif.

**Diagnostic.** Aucune dépendance au hachage reproduite. Avant modification,
hameau 2024 sous 1/42/310/2024 : mêmes chronique, empreintes, état final
complet, mesures, récit, souvenirs, épisodes et avis ; état/rendu/scène
conservés après recharge. Même identité pour Relais 2024 sous ces quatre
hachages et sur la base historique `13ce328` sous 1/310. Appels `2/60` h,
départ tiré, joueur chambre de la cloche ; le pas du banc termine à 5 min.
Le test d'origine échoue sous **les quatre hachages**, `KeyError: 929`.
`tests-audit` : **46/47 verts**, cette seule erreur, aucun autre défaut.

**Cause et légitimité.** Bissection des fusions depuis `c293d3f` (271),
borne saine rejouée : `980d802`, `cb1ab64`, `7ec839e`, `d7302a4` ont le
retour 929 ; `02c7330` et **`8406756` (fusion 303)** ne l'ont plus. Les deux
bornes finales sont adjacentes sur l'intégration : `d7302a4` → `8406756`.
À **479**, Maël veut toujours servir Brune, mais son lieu cru est `None`.
Avant 303, son plan reste vide ; après, il demande sa localisation à Aubin.
C'est la première différence de chronique (index 92) : question supplémentaire
avec témoins, puis déroulement différent de Brune (747/929 → 773/1067).
Le 303 prépare justement les participants inconnus par le contact commun
(`_pulsion`, `_participants_a_localiser`, `_chercher`, normalisation et
revalidation). Le changement observé est donc légitime, sans exception pour
Brune ; le moteur n'est pas corrigé pour retrouver une ancienne date.

**Correction du test.** Capture réelle du parent `d7302a4`, états après les
choix **591/929** et épisodes bruts, rangée dans
`tests/data/sonde-271-brune-hameau-2024.json.gz`, provenance documentée.
Aucun classement ou preuve calculée n'est stocké. La sonde actuelle recalcule
les retours ; les assertions **`entree_publiee_utilisee`**, **`possession_nouvelle`**
et **`lieu_cru_change`** sont exactement conservées. Entrées confrontées aux
états capturés, monde complet, rendu et scène contrôlés après recharge.
Les tuples perceptifs sont restaurés comme dans la fixture Aubin du 276 ;
la comparaison des entrées archivées emploie leur forme JSON canonique.
La capture n'a changé ni les épisodes ni la chronique des nuits déjà jouées,
aux deux bornes. Le contrôle avec/sans sonde de la nuit **actuelle** reste
dans un test distinct, sans oracle sur ses dates. Moteur et outils inchangés.

**Vérification.** Test historique corrigé vert sous **1/42/310/2024**.
**48/48 tests ciblés verts**, trois fichiers d'audit/comparateur, 109,976 s,
aucun échec, erreur ou saut ; `fin-cloture.json` : **`ok=true`**, 113,099 s.
**20/20 paires d'empreintes 2 h identiques** contre `60f857c`, cinq scénarios
× quatre graines : chronique, mesures et état final complet ; zéro plantage,
avis identiques. Références absentes calculées une fois et rangées dans le
cache ; aucun banc relancé après le changement des seuls tests. Calcul initial
détaché, priorité réduite, deux travailleurs au plus, 731,805 s ; ni Luna ni
suite complète. `fin.json` en échec conservé, bilan final `fin-cloture.json`.

**Limites.** Identité établie pour ces nuits, pas preuve universelle de
déterminisme. La fixture vérifie le classement historique ; le test vivant
vérifie la transparence actuelle de la sonde. Aucune amélioration du gameplay
ni correction moteur revendiquée. Bruts :
`C:/Users/msics/donjon/artifacts/hachage-316/`, `fin-bissection.json`,
`analyse-causalite.json`, captures avant/après, sources et journaux.
