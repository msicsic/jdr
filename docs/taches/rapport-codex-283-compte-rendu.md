# Lot 283 — le compte rendu du mandaté

Branche `codex-compte-rendu`, **non fusionnée**, base `c5a1740`,
29 octobre 2026. **Lot terminé**, code `5aef281`, validation sur `2204921`.
Ces commits sont poussés sur `origin`, autorisé explicitement par l'utilisateur.

**Invariant.** Le mandant apprend une parole sur l'issue, sans lire l'état privé
du mandaté. `agendas.compte_a_rendre` propose une charge terminale `mandat`
quand le mandant est cru joignable ; `social.bavarder` la prend dans les
occasions de parole existantes. `echanges.rendre_compte` vérifie la portée,
enregistre avant affichage et utilise `faire_entendre` : voix, témoins et rendu
communs. Le contenu identifie le contrat et l'issue `reussi/echoue/renonce`.
L'émission persistée est unique. Dissimuler l'échec passe par le prix commun
de faute d'honnêteté comparé au poids du projet ; honnêteté 100 l'interdit.

`recevoir_compte` conserve aussi le doute et la voix non attribuée. Une voix
attribuée au titulaire connu passe par la persuasion commune ; la croyance
reste `dit`, avec confiance et poids relationnel. `actualiser` clôt sur cette
croyance, sans déplacement ni transmission fictifs, et révise sur constat
contraire ; une clôture ainsi démentie se rouvre. Suspicion bornée par
`RECENT`, preuve propre de parole `entendu`, position observée `vu`.
Validation des contrats/contenus/croyances à la recharge. `paroles.TYPES`
déclare le type PNJ ; protocole joueur, jugement et choix faire/confier intacts.

**Validation finale : 529 tests / 53 fichiers verts en 399,515 s**, zéro
échec, erreur ou ignoré, dont les sept nouveaux tests du lot et les fichiers
d'agendas, engagements, parole/voix/ouïe concernés. Sur `crue_hameau`,
Gorm → Aubin → Brune : deux charges, trois issues, mensonge, doute, voix non
attribuée, portée réelle, émission unique et réception après recharge.
Information exécutée par la parole réelle ; déplacement exécuté par la
marche réelle de Brune avant l'annonce. Autre mandant : Ilse → Gorm.
Monde complet, rendu, scène et écoute comparés après recharge ; laps
entier/découpé identiques sur cet autre couple pour les deux charges.
Constats contradictoires avant/après réception sur les deux charges.

**Empreintes 2 h : 20/20 paires identiques**, chronique, mesures et état final
complet, `c5a1740` → `2204921`, aucun plantage. Relais, mine, auberge, crue et
crue du hameau, graines 1985/7/42/2024, départ tiré. Vingt références absentes
du cache calculées une fois et rangées ; vingt nuits de branche. Aucun mandat
accepté relevé des deux côtés : ces nuits prouvent la neutralité hors compte
rendu, les scènes ciblées prouvent son fonctionnement. Le banc 4 h conditionnel
n'a donc pas été lancé. Les avis signalés « à expliquer » sont identiques
des deux côtés ; aucune nouvelle alerte non justifiée.

**Limites.** Une absence de preuve de transmission ne prouve pas qu'une
information n'a pas été transmise : une réussite mensongère d'information
reste du ouï-dire tant qu'aucune preuve contradictoire n'est disponible.
La preuve négative générale de cette absence n'est pas ajoutée. Le test de
démenti d'information porte sur un échec annoncé malgré une transmission
personnellement attestée. Pas de réaffectation, d'annulation à distance,
de protocole joueur, ni de garantie de retour d'un mandaté occupé ailleurs.
Le renoncement testé est une charge supplantée, déclarée en fixture.

Bruts : `C:/Users/msics/donjon/artifacts/compte-rendu-283/` : `tests.json`,
`empreintes.json`, `mandats-naturels.json`, journaux et `fin-verification.json`
**ok=true**, codes tests/empreintes **0**. Campagne séquentielle détachée,
un travailleur réduit, **934,374 s** au total. Sources du jeu et tests inchangés
depuis cette validation ; aucun nouveau calcul à la clôture, aucun calcul actif
du lot. Ni Luna ni suite complète. Vérification d'intégration au superviseur.
