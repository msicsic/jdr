# Rapport 289 — un service admis au plan, refusé à l'exécution (bénéficiaire de lieu inconnu)

29 octobre 2026. Branche `ds-service-lieu-inconnu`, base intégration `980d802`.
**Diagnostic seul** : aucun fichier de code du jeu, de test ou de scénario modifié ;
aucune Luna, aucun banc, aucune suite. Un processus Python à la fois, priorité
réduite. Bruts et scripts dans `C:/Users/msics/donjon/artifacts/service-289/`.

## 1. La capture reproduit l'admission puis le refus

Capture `echec-service-273.json` (auberge, **226 min + 352 dixièmes**,
`mode_cases`), les deux champs de la branche 273 retirés comme dans le script
de Sol. Tilo est en **cuisine** [3,1], Mathurine au **cellier** [1,3], la
marmite `marmite_1_1` est sur lui avec **1 portion**. Sa croyance du lieu de
Mathurine est **nulle** (`{valeur: null, source: "vu", minute: 226}`) : elle
vient de quitter sa vue (« Mathurine, pèlerine passe dans : Cellier. »).

Le plan proposé est `[servir marmite_1_1 pour mathurine]`, mesuré à
**0,5167 min**, sans marche. `pnj.refus_etape` renvoie `None`, et la
revalidation de `pnj.agir` (ligne 1871) le confirme juste avant le geste.
À l'exécution, `echanges.servir` (lignes 1339-1341) refuse :

| Terme | Valeur |
|---|---|
| `o["portions"] > 0` | 1 |
| bénéficiaire personnage | oui |
| `autre["lieu"] == monde.objets[id]["lieu"]` | **faux** : cellier ≠ cuisine |
| `peuvent_se_parler` | vrai |

Le refus est donc la seule inégalité de salle ; le monde reste intact
(1 portion, aucune chronique, aucune ligne joueur). Après rechargement,
monde, rendu et scène perçue sont identiques dans les deux sens.

## 2. Admission voulue par le 259, refus constaté sur place

L'admission vient de deux gardes de croyance :

- `pnj._a_reunir` (664-687) ajoute Mathurine aux participants requis
  (`servir`, aucun contrat de venue en cours) ;
- `planification._mesurer_direct` (2872-2875) ne rejette un requis que s'il
  n'est pas présent **et** qu'il est touché **ou** que sa salle crue est
  connue ; `pnj.refus_etape` (1820-1822) applique la même condition.

Ici : non touchée, salle crue inconnue → aucune des deux branches ne rejette.
C'est exactement l'invariant du **lot 259** : « seule une présence crue
impossible à cet instant rend l'étape inadmissible ». Une localisation
inconnue n'y est pas une absence. Le refus relève de l'exécution, qui juge la
présence réelle au moment du geste ; c'est un **constat sur place**, de la
même classe qu'une marche vers une salle où la personne n'est plus. Il n'y a
donc pas de désaccord de contrat : le plan est admissible *sur ce qui est cru*,
l'exécution constate le réel. La solution proposée par le bilan 273
(« présence crue ou venue convenue pour tous les participants requis »)
reviendrait sur le 259 pour le cas inconnu et n'est pas retenue en l'état.

## 3. Coût observé

**Capture, 12 minutes rejouées** en blocs d'une minute et d'un bloc : gestes,
chronique, états finaux identiques (`identiques: true`, rendus égaux).
Deux exécutions de `servir` seulement :

- **226 + 352** : refus (cuisine / cellier) ; le pas est compté `MANQUE`,
  le plan est abandonné, la pulsion reste engagée avec un plan vide ;
- **226 + 362** : Tilo apprend le cellier **par ouï-dire** (`entendu`) — la
  coïncidence d'une conversation voisine —, tente `demander marmite_1 à
  hugues` (refus, Hugues est au cellier), puis choisit
  `[aller cellier, servir]` ;
- **226 + 408** : service réussi au cellier ; portion consommée.

Coût : **un geste perdu, 5,6 s de jeu**, aucune boucle, aucun plan identique
reproposé, aucune parole affichée pour l'échec. Le service n'est pas perdu :
il attend la présence.

**Contre-épreuve (variante explicite)** : la même capture avec Mathurine
déplacée au grenier sans témoin. Le service échoue à 352, la pulsion reste en
attente (plan vide) ; Mathurine revient d'elle-même et entre en cuisine ;
le service réussit à **228 + 0**. Toujours aucun renvoi du même plan.

**Autre cas de même nature** : mine, Mathe sert `vivres` à Lucien, cru nulle
part, réellement à la galerie. L'admission est identique (`refus_etape` nul,
mesure admise) : le défaut d'admission est **général**, il ne tient ni au
repas, ni au bénéficiaire, ni à l'auberge. Le témoin avec lieu cru
(capture 251, Mireille/Mathurine) reste refusé à l'admission
(« participant cru absent »), comme prévu par le 251/259. En revanche, la
pulsion naturelle ne s'y forme pas : `deliberation.secours` exige de **voir**
le bénéficiaire (`percus`). Plan posé comme dans la capture : un refus à
l'instant 0, puis **aucune reproposition en 12 minutes** et 8 portions
intactes ; le service n'est pas rendu dans cette scène. La différence avec la
capture vient de la persistance de la pulsion, pas du contrat.

## 4. Conclusion

**Ce n'est pas un défaut à corriger par un petit lot d'invariant.** Le 259 a
explicitement choisi de ne pas traiter une localisation inconnue comme une
absence ; refuser l'admission sur l'inconnu le rouvrirait. Le refus est le
constat d'exécution prévu, sans effet de bord, sans mensonge au joueur, sans
boucle ; le service est différé puis rendu dès que le bénéficiaire est là.

**Limite conservée** : le plan est *mesuré* comme exécutable sans aucune place
projetée pour le participant (0,517 min, sans marche) ; il dépense donc un
geste qui ne peut pas aboutir. Une amélioration générale — planifier une
recherche ou un appel avant le service, ou obtenir une venue convenue — est
un lot de planification distinct, qui doit se garder de la boucle du 251 et ne
pas relire la position réelle. Rien de tel n'est proposé ici.

**Portée** : deux cas et une capture rejouée ; aucun banc, aucune nuit. La
généralité du constat d'admission est établie sur les deux scènes, pas le
risque résiduel d'un plan identique répété quand la pulsion persiste sans
information nouvelle : non observé ici, non exclu par construction.
