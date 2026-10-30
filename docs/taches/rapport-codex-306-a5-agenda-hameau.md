# Lot 306 — agenda d'évacuation du hameau

Branche **`codex-a5-agenda-hameau`**, non fusionnée, base initiale `7ec839e`.
Reprise sur le **laptop**, 30 octobre 2026 : fusion sans rebase de
`origin/integration` **`c9b066bb`** dans `0a12fd12` (ancienne intégration `13ce3286`).
**Tests ciblés validés ; nouveau banc détaché en cours, validation comportementale en attente.**

**Invariant et données.** Gorm reçoit `evacuer_crue`, `amener` vers
`chambre_cloche`, comme dans la crue, pour Ilse, Brune, Maël et Sève.
Ces deux nouveaux évacués ignorent les salles basses ; Maël connaît Gorm,
Sève connaît Aubin/Ilse ; Gorm accueille les évacués, Aubin surveille les vannes.
Aucun mandat initial, lien, coût, savoir ou charge `informer` ajouté.
Aucune donnée ajustée après mesure ; moteur et MJ identiques à l'intégration.

**Fusion et vérification ciblée.** `docs/etat-dev.md` reprend l'intégration
avec une entrée 306 de huit lignes au plus. Le conflit d'occasions conserve
les deux intentions : empreinte complète du hameau **85955d0e…**, et
empreinte intégration **72a33d77…** après retrait du seul agenda 306.
Les six autres empreintes restent strictes et inchangées.

**54 tests / neuf fichiers verts, 143,892 s**, deux travailleurs réduits :
agendas et autorité du hameau, occasions, scénario hameau, faire/confier,
devis de l'observateur, compte rendu, réaffectation et récit d'agendas.
Chargement, activation, absence d'attribution imposée, Maël/Sève marchant
après accord, monde/rendu/scène/écoute rechargés et temps découpé contrôlés.
Premier lancement sous sandbox inexploitable : fichiers temporaires Windows
inaccessibles ; passe retenue hors sandbox. Aucune suite complète ni Luna.

**Banc de reprise.** Hameau **4 h × 1985/7/42/2024**, comparaison à `main`
`0bad2272542abd68f4952ac714838740b3f811dc` (instruction de reprise).
Le cache commun du laptop est relu avec sa clé d'instrumentation ; les
quatre nuits hameau manquent dans les références copiées et seront seules
calculées puis rangées. Branche jouée ensuite, deux processus au plus,
priorité réduite, captures finales et contrôles de recharge monde/rendu/
scène/écoute. `analyse.json` et `comparaison.json` contiendront mandats,
refus par cause, comptes rendus, réaffectations, évacuations, suspects 219,
boucles, usurpations et plantages. `ok` dans la fin prouve l'achèvement
technique, pas l'absence de boucle : l'analyse reste à instruire.

Crue d'origine : empreintes **2 h × quatre graines** refaites contre
l'intégration fusionnée, dont le moteur est identique, pour isoler les
seules données du 306. Cette comparaison suit le banc du hameau.
Les écarts hameau contre `main` comprennent aussi les lots de l'intégration ;
aucune causalité exclusive ni comparaison de performance avec le cache.

**Mesures antérieures**, contre `13ce3286`, conservées dans l'historique Git
(`0a12fd12`) et sur le PC fixe : mandats proposés/acceptés/refusés
**4/0/4, 5/2/3, 3/3/0, 1/1/0** ; évacués à la galerie **4/2/3/2** ;
mandats atteints **0/2/3/1**, un compte rendu en 42, aucune réaffectation.
Suspects **0/0/0/7**, 160 recharges identiques, crue 4/4 empreintes identiques.
Ce banc restait non validé : achats promis répétés en 7 et réclamations de
Sève en 2024 ; leur état après les lots récents ne sera affirmé qu'après
lecture du nouveau banc. Les données ne changent pas pour les contourner.

Bruts de reprise dans le worktree : `artifacts/agenda-hameau-306/reprise-integration/`
(`tests.json`, `lancer.py`, `banc.log`, comparaisons, captures, `fin.json` écrit
même en cas d'échec). Anciennes archives : PC fixe,
`C:/Users/msics/donjon/artifacts/agenda-hameau-306/reprise-309/`.
