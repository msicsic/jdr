# Lot 427 — G14, ciblage d'un élément d'ambiance

31 octobre 2026 — `codex-g14-ciblage-ambiance`, base `origin/integration` / `ce64ba7e`.
**Contrat moteur vérifié ; geste utile avec Luna non démontré.**

**Invariant et changement.** Une ambiance publiée ne crée aucun objet. Son extraction
porte des références locales avec libellé littéral, ancrage public et statut manipulable.
`narration.schema_audit/controler/consigner` valident cette enveloppe avant publication,
recontrôlent le lieu et la visibilité, puis enregistrent texte et références ensemble.
Les anciennes listes de chaînes restent lisibles, sans autorisation de matérialisation.
La production asynchrone du prototype n'est pas présente dans cette base ; G8 reste distinct.

`faits_locaux.preparer_faits` résout le détail nommé ou son identifiant local vers son
support, puis conserve les validations communes : budget, relation, masse, capacités,
portée et usages. La création et sa liaison sont atomiques. Une sensation non manipulable
reçoit un refus moteur avec `attendu`. `lier_suite`, le MJ et `Moteur` résolvent les
références d'action vers l'objet admis, y compris sans suite jointe et après recharge.
Une proposition répétée retrouve cet objet sans changer ses propriétés ni consommer
le budget. L'identité dérivée du lieu, du support et du libellé, conservée comme métadonnée
technique de l'objet, survit à l'éviction de l'ancienne prose. La projection publique exclut
cette métadonnée ; aucun registre d'esprit, mode ou audit supplémentaire n'est ajouté.

**Tests.** La vraie boucle avec MJ simulé couvre la pierre mouillée au Relais et l'éclat
de bois à l'atelier : aucun objet avant matérialisation, prise, réexamen sans ressaisie,
objet unique après recharge et éviction de prose, état et rendu comparés. Elle couvre
aussi deux libellés identiques sur des supports distincts, une odeur non manipulable,
un budget épuisé, des enveloppes invalides et la revalidation avant publication.
Sept fichiers : **82 tests, 81 verts, un échec préexistant**, aucune erreur ni test ignoré,
154,32 s avec un travailleur à priorité réduite (`tests-final.json`). Les cinq tests G14
sont verts. L'échec narratif `test_messages_moteur_apres_deux_refus_sans_action_fictive`
attend le refus du combustible après celui de la lecture, mais la reprise refuse déjà
la substitution d'action. Même échec reproduit avec les cinq modules de `ce64ba7e`
(`diagnostic-base.log`), sans modifier ce test. Aucune suite complète.

**Banc rapide.** Relais, 4 h, graines 1985/7/42/2024, référence `ce64ba7e` cachée
par commit, un travailleur à priorité réduite : **chroniques, mesures et empreintes
des états finaux identiques**, aucun plantage (`banc-rapide.json`, `comparaison-identite.json`).
L'atelier n'a pas de scénario au banc PNJ. Aucun gain de temps revendiqué.

**Luna : une passe sur copies**, coffre principal, `gpt-6-luna`, trois scripts :
**31 appels / 9 tours MJ**, environ **16,4 s/tour** ; un repli, deux tours avec refus,
aucune erreur technique ni de recharge. Au Relais, la création proposée avec sa suite
est refusée par la revue comme perception active et pour une capacité non déclarée ;
Luna substitue le toucher du sol. À l'atelier, la cible cosmétique directe est bloquée,
puis l'admission reste refusée ; l'odeur reçoit le refus moteur. Aucun ramassage réussi,
donc aucun coût jusqu'au geste fidèle démontré. Le banc d'ambiance exerce la nouvelle
enveloppe et publie des sensations sans créer d'objet. Le lanceur s'est interrompu après
la première partie enregistrée sur un import de rapport HTML ; seuls les deux scripts
non joués ont ensuite été lancés, sans seconde passe.

**Limites.** Les paraphrases, la classification physique d'un élément et les jugements
de portée restent sémantiques. Une ancienne ambiance sans enveloppe ne permet pas
de reconstruire sûrement son ancrage. La réussite générale du ciblage avec Luna reste
ouverte ; aucun contrôle existant n'a été retiré pour obtenir un succès.

**Bruts.** `C:/Users/msics/donjon/artifacts/g14-ciblage-427/` : commandes, tests,
diagnostic de base, banc rapide, copies initiales et trois fils Luna. L'environnement
virtuel du dépôt principal a servi, celui du worktree étant absent.
`fin.json` clôt les vérifications ; aucun calcul du lot ne reste actif.
