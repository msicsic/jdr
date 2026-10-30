# Lot 328 — G6, repères de position

29 octobre 2026 — Branche `codex-g6-reperes`, **non fusionnée dans integration**.
Base initiale G5 `c4cd83f` ; synchronisation demandée par fusion sans rebase de
`integration 49608db` dans `ced37a3`, à deux parents. Aucun conflit Git ; les deux
apports à `etat-dev.md` et les assertions des deux branches ont été conservés.
Le contrôle avant correction compte **2 998 assertions / 58 versions de fichiers**.

**Invariant.** `reperer` utilise le contrat d'action existant et consulte le seul
repère public courant ou mémorisé. Le moteur écrit axes métriques, distance
euclidienne approximative au décimètre et côtés dans le regard actuel. Le souvenir
reste une dernière observation, jamais une présence actuelle ; dans un autre lieu,
seule sa salle connue est donnée. Sans cases, aucune métrique n'est inventée.
Noms privés masqués, absence de repère rendue par le constat G5 ou un refus public.
Ni rotation, temps, effet physique ni registre supplémentaire ; un plan falsifié
est recompilé avant exécution. Les phrases exactes rejoignent les attestations et
sont revalidées à l'enregistrement. La prose libre garde ses audits.

**Raccord U-P décidé par l'utilisateur.** La règle commune de `jeu.py` consulte
`commandes.PERCEPTIONS` : une consultation de perception répond immédiatement ;
la faisabilité d'un geste à effet prépare sa fiche sans exécution. Aucun cas
propre aux positions. La réponse de G6 reste exacte, suivie du « Compris » U-P,
sauvegardée avant affichage, sans fiche ni confirmation.

**Vérification.** Livraison initiale : **162 tests / quinze fichiers verts**.
Après fusion : **421 tests / 39 fichiers**, 401,422 s, huit échecs, sans erreur
ni saut. Sept étaient des attentes G6 antérieures au récapitulatif U-P :
elles comparent maintenant tout le texte exact, réponse puis « Compris », en
gardant monde, nature du résultat, appels, noms, scène/carte et recharge.
Le test U-P d'examen perceptif compare les mêmes objets, joueur et journal au
moteur direct : seul `connaitre`, sans jet ni temps, est admis. Les questions de
faisabilité gardent toutes leurs assertions de non-exécution. Console, web et
vraie TUI exercent ces deux branches ; leur état complet est comparé après recharge.

Huitième échec : le repli ajoute « Le brasero : Echoppe de Gorm. ». Phrase
conservée : égalité exacte avec `rendu.position`, appartenance aux attestations
avant tout appel MJ et après recharge ; l'oracle de réponse complète et le refus
de la chaleur inventée restent vérifiés. Aucun changement du repli de production.

La reprise étendue à `test_perception` a révélé une attente G5 déjà périmée :
examiner dans le noir son couteau reconnu au toucher renvoie un constat, pas une
exception. Même échec reproduit avec le moteur exact `49608db` chargé en mémoire ;
fonction `non_perception` identique par AST. Seule cette attente est portée,
avec constat et état complet inchangés après recharge ; rallumage et autres
assertions conservés. **Reprise finale : 42 tests distincts / quatre fichiers
verts**, sans erreur ni saut : 25 tests dans la passe de 54,364 s, puis les
17 tests de perception en 0,814 s. Deux travailleurs réduits au plus. Les
421 tests ne sont pas relancés après correction, conformément à la reprise ciblée.

**Luna, avant synchronisation : une passe**, atelier/noms-dialogue, 96,320 s,
43 appels, zéro erreur/repli ; 19 états observables comparables identiques aux
archives `c9459ce`, noms et mémoire spatiale préservés dans quinze dossiers.
Appels atelier 32 → 26, noms-dialogue 13 → 17 ; aucun gain attribué à G6.
Zéro relance géométrique, mais aucune requête `reperer` ni reprise canonique :
**adoption Luna non démontrée**, voies typées vérifiées avec MJ simulé seulement.
Aucune seconde passe, suite complète ou banc PNJ.

Bruts `C:/Users/msics/donjon/artifacts/g6-328/` ; sous `fusion/`, les bilans
initiaux rouges sont conservés, ainsi que `preexistant-perception.json`,
`tests-reprise-incidents.json`, `tests-reprise-perception.json`,
`reprise-validation.json` et **`fin-reprise.json ok=true`**. Aucun calcul actif.
Recouvrements monde/moteur/narration résolus ; G5, U-P, G15 et G19 conservés.
La garantie n'est pas étendue au routage de toute question ou à toute prose libre.
