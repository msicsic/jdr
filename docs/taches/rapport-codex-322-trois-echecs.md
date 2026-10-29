# Lot 322 — trois échecs nouveaux : diagnostic et oracles

29 octobre 2026. Branche `codex-trois-echecs`, base `integration 0a0bc9d`.
**Lot terminé**, deux travailleurs de calcul au plus, priorité réduite.
Bruts : `C:/Users/msics/donjon/artifacts/trois-echecs-322/`.

**Diagnostic.** Les trois attentes historiques confondent une scène isolée
avec un jeu où le secours peut maintenant préparer le contact d'un
bénéficiaire inconnu (contrat du lot 303). Aucun fichier du moteur modifié ;
les lots 313 et 315 ne sont donc pas concernés par une correction de code.

- **Voix : changement légitime.** Mathurine conserve le but de nourrir
  Mireille et la cherche après avoir cherché Odile pour obtenir des vivres.
  Elle appelle réellement « la grande fille de vingt-huit ans ? » depuis
  le couloir (instant 3451, niveau reçu 7), puis le grenier (3616, niveau 8).
  Le joueur saisit les mots par l'ouïe commune et entend une troisième voix
  anonyme ; aucun nom d'auteur n'est révélé. `diagnostic.json` conserve les
  étapes, intentions, bruits, paroles rendues et contrôles de recharge.
  Dans les deux tests historiques, `sans_souci` retire seulement le secours
  spontané de ce tiers, comme le placement le fait déjà pour Hugues et Tilo.
  Les égalités exactes des deux voix, l'absence de nom et les assertions
  d'invitations sont conservées. Un nouveau test garde la scène avec ce
  tiers actif : appel réel audible, trois voix, anonymat, monde, scène et
  rendu de l'écoute identiques après sauvegarde/rechargement.
- **Service : changement légitime.** Avec la voix connue, Mathe croit Odon
  au baraquement ; le plan est déjà `None`. Avec la voix inconnue, le montage
  retire toutes ses croyances sur Odon : le plan est une inspection de la
  réserve pour le localiser, sans service ni passage de porte. Le verrou
  reste cru fermé à clé. Il s'agit d'un préfixe incertain, pas d'une promesse
  de repas. La demande effective est toujours refusée comme impossible,
  même au jet 20, avec ou sans localisation préalable. Le test place
  désormais le lieu entendu d'Odon dans les deux variantes avant d'éprouver
  l'accès aux vivres ; `None` et le refus `impossible` restent exigés.

**Bissection achevée, 414,998 s.** Les trois tests originaux sont verts sur
`d1c0722` et sur le parent direct **`d7302a4`**, rouges dès la fusion
**`8406756` (lot 303)** : deux égalités de voix, puis inspection de la réserve
au lieu de `None`. Les points `02c7330`, `f8fbff2` et `79fca6a` reproduisent
ces mêmes échecs. Six références, trois tests chacune, sur copies
`git archive` sans changer le worktree courant. `bissection.json` et
`bornes.json` conservent les résultats ; le lot 312 n'introduit aucun des
trois écarts.

**Vérification ciblée : 54/54 tests distincts verts**, trois fichiers,
zéro échec, erreur ou saut. Première passe : 53 verts et une erreur
d'import de `sans_souci` dans le test modifié. Import corrigé ; les
18 tests du fichier concerné sont verts à la reprise (83,205 s).
Les deux autres fichiers (12 et 24 tests) sont inchangés depuis leur
passe verte. Les contrôles de diagnostic conservent l'état complet, le
rendu et la scène après recharge pour six variantes. `fin-calcul.json`
conserve l'échec initial ; `bilan-cloture.json` rassemble les dernières
passes, et **`fin-cloture.json` clôt le lot avec `ok=true`**.
Pas de Luna, suite complète ni banc : aucun code du jeu ne change.

**Limites.** Le verdict porte sur ces scènes et les garanties des tests ;
il ne certifie ni tous les secours, ni toute absence de boucle.
Branche poussée vers origin ; aucun calcul du lot actif.
