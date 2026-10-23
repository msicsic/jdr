# Rapport Codex 12 — le coup et assommer (4b)

Branche `codex-force-4b`, non fusionnée, base `36cc4f1` (tâche sur le code de `main`
après 3b et 4a ; code identique à `origin/main` `a7ecb50` au départ,
seul le fichier de tâche diffère). Aucun changement de `main`. Luna reste `gpt-6-luna` et la comparaison
entre modèles reste désactivée. Bancs successifs, quatre processus au maximum, priorité
réduite ; aucune sauvegarde de partie de l’utilisateur n’a été employée.

## Règles et fonctions

- `combat.arme`, `valider`, `rotation`, `frapper` : même règle physique pour le joueur
  et les PNJ. Armes contondantes, tranchantes, improvisées à partir de 0,5 kg, ou mains
  nues ; DEX pour une lame légère, FOR sinon. Caractéristiques modulées, égalité à la
  victime, défense fixe 10 par surprise, coup automatique sans défense ou tenu par un
  autre. Les dégâts suivent le plan ; un coup ne tue jamais.
- La perception de la victime est relevée **avant** le coup. Le registre, les souvenirs
  et les conséquences sont établis avant l’affichage. Un coup touché interrompt le geste
  en cours. Le cri vient de la victime consciente ; il porte à 9, distinct de l’appel à
  l’aide dans le rendu. Le coup porte à 7. Son bruit ne donne pas d’esquive rétroactive.
- Assommer exige un contondant, ôte 1 PV ; surprise ou absence de défense donne
  l’inconscience, sinon résistance de VOL. Le réveil tiré et sauvegardé reste celui de
  4a. Un joueur assommé traverse son inconscience dans la même action, sans lire les
  événements survenus pendant son absence. Aucun ajout de mort, fuite ou riposte.
- `Moteur` prépare l’action `frapper` avec méthode `simple` ou `assommer`, puis emploie
  cette règle commune. Les refus ont un `attendu`. `Plan.confirmation` exprime le contrat
  de fiche avant tentative ; il se propage aux manœuvres composées et s’applique aussi à
  la commande locale. Il ne dépend ni d’un personnage, ni d’une formulation de saisie.
- `pnj` exécute les coups, l’approche feutrée `dans_le_dos`, la rotation et la prise sur
  un porteur sans défense. Le registre distingue une contrainte sur une personne d’un
  coup pour forcer un objet. Vue et ouïe conservent leurs règles d’attribution ; un bruit
  seul ne donne pas un nom. Les victimes ont `subi`, les auteurs `a_frappe`, les témoins
  `vu_agir` ou `entendu_agir`. `relations.EPREUVES` porte `subi` et `violence_vue`, sans
  doubler chez la victime l’épreuve de son propre coup.
- `planification` offre assommer-pour-prendre seulement pour un moyen utile au but.
  Les coûts comparent demande, moyens propres et agression ; aucun ordre de recours
  n’est écrit. Honnêteté et douceur ont des faits distincts. La gravité 2 s’applique
  avant le plafond d’enjeu. `prix_violence` prévoit la défense future à douceur 100,
  sans ajouter un but de défense en 4b.
- La recherche ne suppose pas que les témoins crus disparaîtront. Hors désespoir, leur
  présence écarte l’embuscade ; perception nouvelle, choix nouveau. Sur place, approche,
  regard et oreilles revalident encore la possibilité. Une personne crue inconsciente
  ne compte plus comme observateur. La transition de recherche groupe l’assommement et
  la prise, mais les gestes réels restent distincts et revalidés.
- `force.force_crue` expose une estimation fondée sur les armes et blessures connues,
  avec la FOR adverse invisible comptée à 10. Ce n’est pas une simulation de duel.
- `rixe.py`, `scenario_rixe.json` et `scenario_rixe_douce.json` : chargement par données,
  valeurs prescrites et corde à l’échoppe ; `jeu.py --rixe`, `banc_pnj --scenario rixe`
  ou `rixe_douce`. Aucun comportement ne teste ces noms de scénarios ou de personnes.
- `corps.mesures`, `recit_pnj`, registre et rejeu : coups portés/touchés, dégâts,
  assommés, inconscience, réanimations et témoins ; section « Violences et corps ».
  Les PV des PNJ restent réservés au rejeu omniscient.

## Cas vérifiés après rechargement

`tests/test_combat.py` vérifie notamment :

- Gorm, puis Aubin, surpris : perte de 1 PV, inconscience persistante, auteur inconnu
  au réveil ; mêmes victimes voyant le coup : auteur retenu et méfiance, témoin d’Ilse ;
- joueur frappant Brune, puis Gorm : fiche, arme, résultat moteur, état visible après
  recharge ; refus guidés, classification des armes, égalité et résistance à assommer ;
- coup interrompant un geste et mettant à 0 PV sans mort ; coup d’un PNJ sur le joueur,
  attente automatique jusqu’au réveil et sauvegarde vivante ;
- même état complet et même rendu après un laps d’un bloc ou découpé/rechargé, après
  le coup **et depuis l’embuscade encore à entreprendre**, avec les deux porteurs ;
- épreuve Brune affamée, refusée pour les vivres, sans capacité de crochetage : elle
  préfère demander la clé, puis, après refus, approche feutrée, assomme le porteur par
  surprise sans témoin, prend la clé, et reste sans meurtre. Même chaîne avec Aubin.
  Gorm peut ranimer son protégé : le test contrôle aussi ce réveil réel lorsqu’il arrive ;
- douceur 100 excluant l’agression ; témoin cru empêchant l’embuscade ; fiche locale
  affichée avant « tenter » ; rotation vers une cible déjà visible comptée et sauvegardée.

Deux épreuves supplémentaires de 8 h, sous contrôle croisé complet et avec rejeux, partent
des mêmes états : un coup touché et 1 PV perdu dans chaque cas, surprise et zéro témoin.
Gorm reste inconscient 10 minutes ; Aubin 1,0317 minute, ranimé par Gorm. Aucun mort,
états finaux sauvegardés puis rechargés identiques. Archives : `epreuves/marchand.html`,
`epreuves/aubin.html`, états de départ et d’arrivée dans `artifacts/force-4b/`.

L’ancien test de demande refusée fixe désormais douceur 100 : il isole le recours social,
au lieu de présupposer qu’aucun autre recours n’existe.

## Bancs et contrôles

Les empreintes sont comparées sans normalisation : chronique, mesures et **état final
complet**, nuit par nuit. Référence `36cc4f1`, puis fichiers du worktree courant.

**Empreintes 2 h et 8 h : identiques** sur les quatre scénarios, graines 1985, 7, 42,
2024, plus 3, 11, 99 et 500 au Relais : vingt paires de nuits à chaque durée,
soit quarante paires. Aucun coup dans ces nuits.

`planification.VERIFIER=True` et `spatial.VERIFICATION=1` sur 2 h, puis spatial 0,2
sur 8 h, graine 42, Relais/mine/auberge/crue/rixe : dix nuits sans écart, sans borne
atteinte, sans usurpation ; `Monde.verifier` à chaque pas. Le contrôle du planificateur
reste complet pendant la passe à 0,2 du spatial.

Rixe et variante douce : huit graines (1985, 7, 42, 2024, 3, 11, 99, 500), 8 h.
Référence sur les mêmes données, puis branche, sans les lancer ensemble.

| Mesure moyenne par nuit | Rixe référence | Rixe branche | Écart |
|---|---:|---:|---:|
| CPU total (s) | 6,125 | 6,186 | +0,99 % |
| Nœuds explorés | 34 914 | 34 985,875 | +0,21 % |
| Temps des recherches (s) | 1,871 | 1,925 | +2,88 % |

La variante douce garde 33 734 nœuds, CPU 6,408 → 6,430 s (+0,34 %), recherches
1,915 → 1,963 s (+2,51 %). La marge de 10 % est respectée sur ces moyennes (et sur chaque nuit mesurée : CPU au plus +2,30 % à rixe,
+6,57 % au contrôle doux) ; une passe
sur un poste chargé ne démontre pas une borne de temps pour toute exécution future.

Aucun coup spontané ni mort dans les seize nuits libres, aucune usurpation. Le recours
violent est démontré par les états d’épreuve, pas par une agression apparue spontanément
sur ces graines. La variante douce exclut la violence ; son identité avec toutes les
mesures du Relais n’est pas revendiquée, car elle garde aussi les autres valeurs de `rixe`.

Les premières passes ont révélé deux défauts communs : gravité appliquée après le plafond
de scrupule, et plans supposant la disparition des témoins. Ils ont été corrigés dans le
contrat de coût et de recherche. Aucun filtre de scénario ou de personnage n’a été ajouté.

### Suite complète

Suite complète : **1 432 tests exécutés, six échecs, aucune erreur, quatre ignorés**, en
167,417 s avec quatre processus. Les quatorze tests 4b passent. Aucun échec nouveau
par rapport à la référence. Le critère « suite entièrement verte » n’est donc pas atteint
sur ce poste. Les six échecs MiMo sont reproduits sur la référence intacte : quatre sous-cas d’état d’affichage
historique (`I/G` devenant `L`), deux comptes de transport (6 au lieu de 5). Ils ne sont
ni ignorés ni corrigés par un changement hors du périmètre 4b.

### Reproduire

Depuis le worktree, Python du dépôt principal :

```powershell
$py = 'C:/Users/msics/donjon/.venv/Scripts/python.exe'
& $py tools/tests.py --processus 4
& $py tools/comparer_bancs.py --reference 36cc4f1 --scenarios relais mine auberge crue --empreintes --heures 2 --processus 4 --sortie artifacts/force-4b/empreintes-2h.json
& $py tools/comparer_bancs.py --reference 36cc4f1 --scenarios relais mine auberge crue --empreintes --heures 8 --processus 4 --sortie artifacts/force-4b/empreintes-8h.json
& $py -m donjon.banc_pnj --scenario rixe --heures 8 --graines 1985 7 42 2024 3 11 99 500 --processus 4 --diagnostic
& $py -m donjon.banc_pnj --scenario rixe_douce --heures 8 --graines 1985 7 42 2024 3 11 99 500 --processus 4 --diagnostic
```

Contrôles croisés, en série, depuis le même worktree (aucun appel au modèle) :

```python
from donjon import banc_pnj, planification, spatial
joueurs = {"relais": "chambre_cloche", "mine": "galerie", "auberge": "dortoir",
           "crue": "chambre_cloche", "rixe": "chambre_cloche"}
for heures, taux in ((2, 1), (8, 0.2)):
    planification.VERIFIER = True
    spatial.VERIFICATION = taux
    for scenario, joueur in joueurs.items():
        planification.BORNES.clear()
        _, mesures, _ = banc_pnj.nuit(scenario, 42, heures, joueur, diagnostic=True)
        assert mesures["usurpations"] == 0 and not planification.BORNES
```

Archives locales non versionnées : `artifacts/force-4b/`, matrices d’empreintes, contrôles,
états complets, diagnostics et journaux de tests. Les nombres utiles sont recopiés ici.

## Vérification Luna à faire

**Différée à la fusion sur un autre poste, à la demande de l’utilisateur.** Aucun essai
de connexion n’a été lancé. Deux essais préliminaires ont seulement constaté l’absence
de session utilisable ; ils ne valident aucun comportement de Luna.

Scènes préparées et versionnées :

- `tests/data/bancs/force-4b-frapper.json` : joueur au refuge, Brune à une case à l’est,
  nom déjà entendu, autres PNJ à l’échoppe. Saisies exactes : `je frappe Brune`,
  `tenter`, `quitter`.
- `tests/data/bancs/force-4b-assommer.json` : joueur derrière Gorm, à une case, Gorm
  orienté à l’est, nom déjà entendu, autres PNJ à l’échoppe. Saisies exactes :
  `j'assomme Gorm par derrière`, `tenter`, `quitter`.

Les deux préparations se chargent et se rechargent hors ligne. Le banc les joue dans des
répertoires temporaires ; aucune sauvegarde réelle n’est nécessaire.

```powershell
$env:SEUIL_AUTH = 'CHEMIN_DU_DEPOT_PRINCIPAL/.seuil-auth'
& $py tools/banc_parties.py tests/data/bancs/force-4b-frapper.json tests/data/bancs/force-4b-assommer.json --fil --max-appels 30 --sortie artifacts/force-4b/luna-fusion
```

Attendu : proposition typée `action=frapper`, cible correspondant à Brune ou Gorm
(la référence opaque est résolue par le moteur), `outil=""`, `difficulte=0`, méthode
`simple` puis `assommer`. Aucun mouvement supplémentaire n’est nécessaire dans ces scènes.
La première saisie affiche une fiche sans modifier PV ou conscience ; « tenter » applique
le résultat du moteur. Selon le jet, le coup peut manquer. Sur assommement touché par
surprise : 1 PV perdu, Gorm inconscient et état conservé après recharge, sans mort.

Viser au plus trois appels pour obtenir la proposition typée, audit d’action inclus
(nominal : réponse + audit, soit deux). Mesurer séparément la narration après « tenter »
(nominal : récit + audit, soit deux autres). Rapporter les corrections, replis, appels et
temps réels ; ne pas compter quatre appels au total comme quatre appels de typage.

Le joueur doit lire la fiche, puis seulement l’issue établie : coup porté ou manqué,
effondrement si l’inconscience est réelle, résistance si elle ne l’est pas. Aucun PV de PNJ,
aucune mort, blessure, perte de connaissance ou identité d’agresseur supplémentaire ne peut
être inventé. Aucune parole ne doit venir d’un inconscient. Vérifier le JSON et le rendu
du fil, puis l’état rechargé. Ces résultats restent à produire ; aucun succès Luna n’est revendiqué.

## Limites du jalon

Le moteur, les états d’épreuve et les bancs locaux sont vérifiés dans le périmètre 4b.
La suite héritée empêche de revendiquer une suite entièrement verte sur ce poste. L’émergence
d’une agression dans les nuits libres et l’égalité de toutes les mesures du contrôle doux
avec le Relais ne sont pas démontrées. Le recours autonome vise les porteurs PNJ ; le geste
exécutable peut aussi frapper le joueur. Le dialogue nécessaire pour solliciter ou dépouiller
les biens du joueur n’est pas étendu ici.

Les coups suivent la convention des gestes courts, conséquence au début puis occupation
de l’horloge ; les issues différées restent en 4d. Les contradictions de narration restent
en partie sémantiques, sans exception lexicale ni consigne supplémentaire au-delà du typage.
