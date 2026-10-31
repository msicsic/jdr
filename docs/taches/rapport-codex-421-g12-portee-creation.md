# Lot 421 — G12, portée d'une création interactive

31 octobre 2026 — `codex-g12-portee-creation`, base `integration` / `78e4133b`.

**Invariant.** Une invention admise existe avant son geste et reste une entité du
monde après recharge. Elle ne vaut ni découverte, ni résultat de perception, ni
effet mécanique implicite. Le contrôle des usages et les revues de portée,
capacités et fidélité restent actifs ; aucun audit n'est supprimé et aucune
consigne supplémentaire n'est ajoutée au prompt du MJ.

**Changements.** `portee_narrative.contexte_admission` donne à la revue les objets
et perceptions de la projection publique, les souvenirs et les données publiques
de mission. Le seul catalogue d'ajout ne suffisait pas à comparer une invention
avec les faits existants. Les connaissances privées des PNJ restent exclues ; une
ambiance conserve sa provenance distincte et ne devient pas une attestation.
`projection_publique` porte la relation physique des créations, tout en excluant
explicitement leurs métadonnées techniques de persistance. Un champ inconnu
reste refusé. Ce contrat manquant empêchait le réexamen après matérialisation.

`faits_locaux.lier_suite`, appelé par `mj`, relie les noms exacts des seuls sujets
créés dans la transaction à leurs identifiants, dans les champs de référence du
contrat commun et dans les invariants de reprise. Les références inconnues et
les autres paramètres restent inchangés ; la prose n'est pas réinterprétée.
Une ambiguïté reçoit un refus avec champ, valeur et identifiants acceptés.
Le geste passe ensuite par la préparation, la revue et le consentement ordinaires.

**Vérification ciblée.** Les fixtures de trois fichiers anciens explicitent
`suite: null`, exigé par `compilation.schema_reponse` depuis A6. La référence
`base-tests.json` montre les refus de forme antérieurs. Aucune assertion de
sécurité n'est modifiée. Après cette adaptation et le portage de projection,
44 tests voisins passent (24,56 s). Le groupe final de sept fichiers passe :
58 tests, zéro ignoré, 216,99 s, deux travailleurs à priorité réduite. La liaison
imbriquée et son refus d'ambiguïté passent aussi séparément (1 test, 0,04 s).
Les nouveaux oracles couvrent pierre détachée au Relais et éclat de bois à
l'atelier, suite jointe ou réexamen sans répétition, ramassage, état et rendu après
recharge, puis laps entier et découpé. Ils couvrent aussi deux faux indices et
deux résultats négatifs de perception, refusés avant création et affichage.
Le compte attendu jusqu'au geste est de trois appels avec suite jointe et quatre
avec réexamen, revues comprises ; il ne s'agit pas encore d'une mesure Luna.

**Calculs demandés.** Empreintes 2 h, quatre graines au Relais, contre la base
du lot avec réemploi du cache ; l'atelier n'a pas de scénario au banc PNJ.
Une seule passe Luna sur copies : `atelier`, `relais`, `luna-restes-ambiance`,
`materiaux`, avec `SEUIL_AUTH=C:/Users/msics/donjon/.seuil-auth`.
Le lanceur enchaîne les deux calculs, à priorité réduite et deux travailleurs
au plus, sans suite complète. Lancé en fond, processus 30040 vérifié vivant ;
résultats à compléter à la reprise après `fin.json`.

**Limites.** L'admission du sens d'un texte français reste une revue sémantique :
ce lot ne garantit pas la détection de toute contradiction implicite ou de tout
faux indice mal classé par le modèle. Le moteur garantit la liaison aux seuls
sujets admis, les effets typés et leur persistance. Qualification générale (G13)
et ciblage unique d'ambiance (G14) restent distincts. Aucune mesure de vitesse
CPU n'est déduite d'une référence mise en cache.

**Bruts.** `C:/Users/msics/donjon/artifacts/g12-portee-creation-421/` : référence,
tests ciblés, commandes exactes, journaux et traces Luna ; `fin.json` est écrit
en dernier par le lanceur.
