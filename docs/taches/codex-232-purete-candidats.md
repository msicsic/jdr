# Tâche Codex 232 : évaluer un candidat sans rien écrire

La vérification d'intégration 4306c14 (lot 231, `docs/taches/rapport-codex-231-verif-integ.md`) a deux nuits interrompues
par l'assertion de `planification.vues_du_choix` « Une méthode candidate a modifié le monde ou l'esprit » :
- mine 42, 8 h, `VERIFIER` + `spatial.VERIFICATION` 0,2, à **415 min** ;
- rixe 42, même contrôle, à **350 min**.

Ces deux contrôles passaient sur `4d4c625`. Piste relevée par le lot 228 (`docs/taches/rapport-codex-228-ceder-outil-reprise.md`
sur la branche `codex-ceder-outil-b`, « Attribution des sept échecs ») : `_entrees_communes` appelle
`biens.services_proteges`, qui **retire des traces de `services_rendus` pendant l'évaluation** (Brune, minute 60, sur la
trajectoire 202). Cette fonction vient du lot 224. À confirmer sur les deux cas réels : l'auteur et le champ modifié.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste : le PC fixe** (`C:\Users\msics\donjon`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. D'autres lots
calculent sur ce poste : au plus 2 processus, priorité réduite.

**Fichiers** : `biens.services_proteges` et ses appelants, la publication des clôtures à la sortie du choix (comme
`attentes_bornees` du lot 87 ou les transitions d'agenda du lot 146 b), et leurs tests. **Pas** : `ouie.py`,
`echanges.tenu` (lot 233), `social.py` (lot 235), `signes.py` et `pnj.agir` (lot 234), le MJ.

**Bruts dans `C:\Users\msics\donjon\artifacts\purete-232\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

## L'invariant
**Évaluer un candidat ne change ni le monde ni un esprit.** Toute écriture qu'une lecture découvre nécessaire (service
fini, trace close) est retenue puis publiée à la sortie d'un choix complet ; rien pour un devis isolé ou un choix
interrompu. Le résultat de la lecture est le même, que la clôture soit déjà publiée ou non. Aucun cas propre à un PNJ,
un scénario ou un service.

## Vérification
- Reproduire d'abord les deux arrêts sur l'intégration (même graine, même contrôle) ; dire l'auteur, la fonction et le
  champ. S'il y a une autre écriture que `services_proteges`, la traiter par la même règle ou la signaler.
- Tests après rechargement : le cas réel (capture juste avant l'arrêt), un autre cas de même nature, choix interrompu sans
  publication, même laps d'un bloc ou découpé, monde et rendu rechargés identiques.
- Les deux nuits 8 h `VERIFIER` + `spatial.VERIFICATION` 0,2 (mine 42, rixe 42) achevées sans arrêt.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference integration`), Relais/mine/rixe × quatre graines :
  identiques attendues hors des nuits où la clôture était publiée trop tôt ; tout écart expliqué.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
- Branche `codex-purete-candidats` poussée (pas `main`). Si la poussée est bloquée par la revue, laisse le commit local
  et dis-le.
- `docs/etat-dev.md` : « Branche `codex-purete-candidats`, non fusionnée ».
- Rapport d'une page `docs/taches/rapport-codex-232-purete-candidats.md`.
