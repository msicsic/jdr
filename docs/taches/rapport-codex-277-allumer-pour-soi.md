# Lot 277 — demander l'allumage d'un foyer fixe pour soi

**Raccord à l'intégration `bca5061` en cours**, fusion sans rebase
`59a1388` (seul conflit : documentation). Les mesures de `bbab808` ci-dessous
restent historiques ; nouvelle validation dans
`artifacts/allumer-277/raccord-266/fin.json` du dépôt principal.

La fusion d'essai 277+280 a révélé quatre cas :

- Protection et agenda de protection : Gorm répond bien à l'alarme et
  inspecte l'échoppe (600 → 836 dixièmes), puis Brune propose l'allumage payé
  (859). Le nouveau registre d'aide payée ajoutait un contrôle devenu devoir
  pressant ; avec 266, la poursuite du protégé finissait dans la crypte.
  La panne subsiste sans le nouveau recours et disparaît sans cette
  publication. Correction : conserver le travail et son estimation physique
  dans le contrat payé connu du payeur ; contrôler comme moyen du besoin
  courant, sans publier de nouvelle urgence de délégation. Alarmes inchangées.
- Voix inconnue : Odon reçoit effectivement sa part, mais Josse redemande
  l'allumage à Rémy, qui répond « déjà fait » (89 demandes relevées) ; la
  chronique bornée évacue le repas. La réponse positive sans nouveau travail
  est désormais retenue pour contrôle ordinaire, sans créer le fait dans les
  croyances ni un nouvel engagement. Même contrat pour deux foyers dans un
  nouveau test ; aucun recours, nom ou palier particulier ajouté.
- Lucien : à 19340 dixièmes (32 min), Anselme, biens 100, choisit légitimement
  d'approcher Hugues pour demander gratuitement l'allumage ; refus à 19381,
  puis recherche d'une flamme. L'absence de pièces n'interdit plus ce moyen :
  sa sortie modifie la fenêtre du vol, et l'information disponible à Lucien.
  L'ablation du recours rétablit toutes les assertions historiques. La scène
  de contrôle précise donc le poêle connu hors d'usage, garde tous les buts,
  et conserve toutes les assertions (95 min, vol 107–110, reprise du ballot,
  recherche, état/rendu/recharge). Le scénario normal garde le foyer utilisable.
  Cette contre-épreuve a révélé une lacune d'admission : `disponible` ne
  décrit que les réserves épuisées. Le recours écarte aussi la fin connue
  (`fin`) du foyer, sans consulter son intégrité réelle cachée.
  La scène précisée repasse avec toutes les assertions et retrouve les
  136 changements de choix et 191 gestes du témoin sans nouveau recours.

Fonctions supplémentaires du raccord : `Vue.attend_tache`,
`echanges._echeance_devis` ; raccord de `_entrees_communes` pour le contrat
payé et son contrôle, sans lecture privée. Neuf tests du lot verts
(43,747 s), dont attente payée sans délégation urgente, foyer connu détruit et
réalisation annoncée sans fait créé. Une ancienne sauvegarde sans estimation
de durée ne reçoit aucune date de contrôle inventée. Les diagnostics avec et sans recours, avec et sans
publication payée, conservent monde/rendu/scène rechargés dans
`allumer-277/integration/`. Tests des quatre fichiers et des appelants, puis
banc 4 h × vingt nuits sur la référence `bca5061`, en reprise détachée.
Ni suite complète ni Luna ; aucune fusion vers l'intégration effectuée.
Les quatre cas sont repassés pendant l'instruction ; leurs fichiers complets
et les appelants restent à valider dans le calcul détaché.

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
