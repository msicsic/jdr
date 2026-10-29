# Lot 320 — G15, émissions de parole

Branche `codex-g15-emissions`, **non fusionnée**, base `integration 0fcc99e`.
Lot terminé ; bruts `C:/Users/msics/donjon/artifacts/g15-320/`,
`fin.json` initial en échec conservé, `fin-cloture.json` pour la clôture.

**Invariant.** `emissions.py` porte le registre unique : identifiant, ordre,
auteur, acte, paramètres, modalité, événement source, destinataires, auditeurs
acoustiques, mots, rendu, lieu et instant. L'ouïe, les faits admis et
`narration.consigner` enregistrent avant publication ; cela atteste la parole
et son audition, jamais la vérité du contenu. Les lectures historiques sont
des projections ; les anciens registres sont migrés et retirés.
`paroles.preparer_parole` distingue les émissions prononcées des réponses encore
autorisées ; rapport, contrôle et rendu lisent ce flux. Une restitution exige
le même auteur et les mêmes mots (variantes typographiques seulement), sans
réémission. Le raccord conserve les répliques moteur dans leur ordre, même
omises par Luna. Le silence d'un témoin dépend de l'absence d'émission de cet
auteur. Aucun refus de nouveaux mots ne nie sa parole antérieure ; une réaction
entendue sans réponse nouvelle autorisée n'est pas déclarée absente. Projection
publique sans auditeurs cachés ni paramètres privés de réception ; attribution
sans nom d'auteur inconnu. L'écoute distante référence la même émission.

**Cas réel.** Archives 86/87 de `c9459ce`, deuxième saisie de la passe 1
(indice 1, galerie de ronde), premier tour rejoué auparavant. Propositions,
dialogues et audits originaux extraits en gzip avec SHA source. Sans réseau :
silence refusé, trois citations suivantes restituées, **Gorm seul répondant**,
sans doublon. Onze nouveaux tests verts : autre dispute, cantonade sans réponse
nouvelle, écoute distante, inconscients, répétitions, migration, noms inconnus ;
monde, texte, scène et rendu contrôlés après recharge.

**Tests.** **579 tests / 53 fichiers consolidés : 577 verts, deux échecs
préexistants, zéro erreur ni saut**, sans suite complète. Base `0fcc99e` : mêmes
échecs d'achat de planches, `23 != 26` (`test_audience`), et d'inspection préparée
au lieu de `None` dans la réserve (`test_voix_inconnues`). Aucun oracle affaibli.
Reprise de dix fichiers : **146/146**, 156,431 s ; derniers contrôles :
**33/33**, 44,027 s, dont les onze nouveaux tests. Préparations qui mutaient les
anciennes listes portées explicitement. `tests-consolides.json` retient la
dernière validation de chaque fichier, sans cumul.

**Empreintes.** Huit paires Relais/crue, 2 h × quatre graines : **chroniques,
mesures et état hors ajouts de schéma identiques**. Empreintes brutes distinctes :
seul le retrait explicite de `emissions_parole` et de `bruits[].emission`
rétablit l'identité complète. **386 émissions** conservées. Huit références
absentes calculées une fois et rangées ; référence puis branche, 159,797 s,
aucun plantage. Mesures sur `6f60266`, sans relance après correction du rapport
de parole du joueur, sans effet sur ces nuits passives.

**Luna.** Une seule passe sur `6f60266`, `avis-joueur` et `echanges`, six tours
MJ, aucune erreur technique ou de recharge, aucun repli. Référence historique
relue, aucun appel relancé : **33 → 25 appels**, **6 → 1 obstacles narratifs**,
**5 → 1 relances**, refus **1 → 1**. Restent le refus du gardien non identifié
et un acquiescement non établi. Trois répliques affichées au cas réel, Gorm seul
répondant. Aucun gain général ou de vitesse revendiqué. La passe précède la
clôture du silence dérivé du flux et n'a pas été répétée. Bruts et analyse
copiés dans le dossier du lot.

**Limites.** G16–G19 non portés, contrôles transitoires conservés ; aucune
garantie générale sur la sémantique libre. Le discours indirect ne devient pas
une citation historique exacte. L'ordre intra-tour perdu des anciens registres
reste explicitement inconnu. Deux travailleurs réduits au plus par vérification,
aucun calcul actif. `moteur.py`, `rendu.py`, `jeu.py` inchangés : aucun
recouvrement avec les fichiers signalés pour U-P 319.
