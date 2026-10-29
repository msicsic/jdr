# Lot 310 — ordre des mesures

Branche `codex-ordre-mesures`, base intégration `13ce328`.

Dans `banc_pnj.executer`, les clés de la différence des registres de
mandats sont désormais triées avant insertion. Les valeurs et le test
d'origine restent inchangés. L'ordre antérieur des autres compteurs est
conservé ; celui des compteurs de mandat devient lexical.

Relecture des ensembles du banc : les autres usages comptent des éléments,
testent leur appartenance ou trient avant sortie (`issue`, empreintes).
Le comparateur trie également ses unions avant parcours de sortie.

**Test d'origine inchangé vert trois fois**, sous `PYTHONHASHSEED` 1, 42
et 2024 (19,779 / 15,082 / 13,076 s), puis de nouveau dans le fichier
complet. **73 tests ciblés / sept fichiers : 72 verts, une erreur**,
aucun échec ni saut, 377,549 s. L'erreur de l'audit est
`test_reveils_brune_reels_et_recharges`, `KeyError: 929` : le retour
attendu à cette date n'est pas dans le relevé. Aucun oracle modifié.

**Huit paires d'empreintes 2 h identiques** : Relais/hameau ×
1985/7/42/2024 contre `13ce328`, chronique, valeurs des mesures et état
final complet ; aucun plantage. **L'ordre des mesures change dans les
huit paires**, uniquement pour le bloc de compteurs de mandat qui devient
lexical. L'égalité des dictionnaires du comparateur ignore cet ordre ;
leurs listes de clés ont donc été comparées séparément. Huit références
absentes calculées une fois et rangées, puis huit nuits de branche,
258,102 s. Avis inchangés : zéro non justifié, douze à expliquer par côté.
Ni Luna ni suite complète. Priorité réduite, deux travailleurs au plus.

Bruts : `C:/Users/msics/donjon/artifacts/ordre-310/`.
**Erreur préexistante reproduite** : le fichier `banc_pnj.py` de
`13ce328` a été chargé en mémoire à la place du module courant (seul
fichier de code modifié), puis les 34 tests du fichier d'audit ont été
rejoués sous le même hachage 310, priorité réduite, 103,719 s.
Même `KeyError: 929`. Ce lanceur de diagnostic a aussi deux erreurs
d'import `audit_nuits` faute du chemin des outils ; elles ne figurent pas
dans la suite ciblée lancée par `tools/tests.py`. Une première tentative
confinée avait rencontré une permission sur le répertoire temporaire ;
le diagnostic retenu a été exécuté hors confinement.
Traces : `diagnostic-base.log`, `fin-diagnostic.json`.

Le bilan brut `fin.json`, `ok=false`, est conservé. La suite ciblée
n'est pas déclarée entièrement verte ; l'audit de Brune reste à corriger
dans un autre lot. Aucun changement du moteur ni des sauvegardes :
chronique et état complet inchangés sur les huit nuits, tests de recharge
existants conservés. Le correctif n'établit aucune garantie nouvelle sur
le comportement du hameau. Lot terminé, aucun calcul actif.
