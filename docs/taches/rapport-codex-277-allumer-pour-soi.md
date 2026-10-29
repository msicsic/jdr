# Lot 277 — demander l'allumage d'un foyer fixe pour soi

29 octobre 2026, branche `codex-allumer-pour-soi`, **non fusionnée**, code
**`bbab808`**, référence **`1852d6e`**. **Validation du lot terminée :
314 tests verts, 20/20 paires de nuits 4 h sans hausse de suspects, aucun
plantage ; `correction/fin.json`, `ok=true`.** L'intégration contient depuis
le lot 266 « rester près » : ces résultats ne portent pas sur sa fusion
avec 277. Le superviseur fera la fusion d'essai et la suite complète.

**Diagnostic préalable.** Captures 269 à 615 et 652 min, brasero et poêle :
condition `allume` admise, aucune offre chaleur `confier`/`engager`, aucun
refus de tâche retenu. Aubin ne garde pas son poste ; l'aide gratuite ne
s'ouvre pas et le travail payé exige une pulsion explicitement visée.
Gorm est cru porter une flamme, mais **son devis reste impossible sur les
quatre cas** : ajouter le recours ne garantit pas d'éviter le coup.
Monde/rendu/scène des captures identiques après recharge.

**Invariant et fonctions.** Un foyer mécanique (`foyer=True`) fixe cru
éteint et chargé, utilisable sans faute et hors de l'eau attendue, ouvre
une demande à qui est cru porter une flamme si le demandeur n'en porte
aucune. Positions et moyens viennent des croyances. Devis, jugement,
priorités, refus et réalisation restent ceux de `confier`/`engager`.
La projection compare les moyens ; le plan s'arrête à la demande, puis
attend le travail réel. Aucun feu ni déplacement n'est produit à l'accord.
Fonctions touchées : `planification.Vue.__init__`, `gestes`,
`_aide_sur_place`, `_confier_tache`, `_allumer_pour_soi`, `_engager` ;
`echanges.engager`, `confier`, `_retenir_aide` partagent l'attente gratuite
ou payée et sa durée physique. Ni `agendas.py`, `signes.py`,
`deliberation.py` ni prompt modifiés ; pas de Luna.

**Épreuves et correction.** Scènes d'auteur brasero/poêle : permission
de Maël, demande, déplacement/allumage/chauffage réels ; accords gratuits
et payés, parole du joueur par `proposition`, huit minutes en bloc/découpées,
monde/rendu/scène après recharge. Contre-épreuves : flamme crue éteinte,
foyer vide sans combustible, eau crue, position cachée, refus sans rappel
par délai. Six captures avant/accord/travail rechargées, tous contrôles verts.
Sur `d306370`, les huit erreurs venaient de la fixture `foyer=False` ;
les deux échecs historiques passent sur `1852d6e` (8/8, 96,496 s) :
régressions du lot. L'admission trop large aux luminaires fixes ajoutait
des états au graphe faim de Rémy et des demandes à la chronique bornée de
Bram, évacuant son ancien appel. Admission corrigée sur la mécanique
`foyer`, sans nom ni motif de besoin ; **six empreintes historiques
inchangées, monde final de Bram identique au témoin**. Fixtures précisées
sans retirer leurs assertions : chaleur en lumière naturelle, permission
sans restitution concurrente, réserve inconnue, joueur au contact et foyer
connu. Les prêts ordinaires peuvent légitimement privilégier la restitution.
Passe finale : **34 fichiers, 314 tests, zéro échec/erreur/saut, 878,547 s**.

**Banc final, `1852d6e` → `bbab808`.** Suspects 219 par nuit :

| Scénario | 1985 | 7 | 42 | 2024 |
|---|---:|---:|---:|---:|
| relais | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| mine | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| auberge | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| crue | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| crue_hameau | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |

**Coups : 0 → 0 dans chaque nuit.** Demandes/offres naturelles d'allumage
**13 → 14**, aucune acceptée : les treize offres payées de Gorm, impossibles,
sont conservées ; seul ajout, crue/42 à **215 min, instant 129220**, Ilse
demande à Aubin d'allumer le poêle du guet, **refus**. Aucun ajout au hameau.
S/F/D (`cats` du lot 183) : **S total 417 → 416**, **F moyen 5,45 → 5,45**,
**D moyen 1,997024 → 2,034524**. Seules trois nuits changent ces mesures :

| Nuit | S | F | D |
|---|---:|---:|---:|
| relais/42 | 8 → 7 | 3 → 3 | 0,75 → 0,75 |
| relais/2024 | 19 → 18 | 5 → 5 | 2,25 → 2,75 |
| crue/42 | 29 → 30 | 7 → 7 | 3,25 → 3,5 |

Les dix-sept autres triplets sont identiques. Référence absente du cache :
vingt nuits calculées une fois ; deux travailleurs réduits au plus,
**2 684,018 s** pour la chaîne entière. Aucun temps comparé entre campagnes.

**Limites et preuves.** Réussite naturelle et bénéfice universel non
démontrés ; le banc 4 h ne couvre pas le coup historique à 652 min.
Réussite prouvée sur les scènes d'auteur ; refus impossible conservé sur
les captures historiques. Ni nouveau calcul de clôture ni suite complète.
Aucun calcul actif. Bruts dans `C:/Users/msics/donjon/artifacts/allumer-277/` :
ancien `fin.json` négatif conservé, instruction base/branche/corrigé ; bilan
final dans `correction/{fin,tests,scenes,comparaison,bilan}.json`.
