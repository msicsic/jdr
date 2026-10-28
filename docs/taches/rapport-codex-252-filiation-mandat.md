# Lot 252 — filiation unique et bornée des mandats

Branche `codex-filiation-mandat`, **non fusionnée**, base `59cb572`
(`origin/integration` au départ). Banc d'empreintes terminé et validé.

## Invariant et réalisation

`agendas.confier(monde, mandant, parent, titulaire, sorte, parametres,
accepte=...)` publie une acceptation déjà jugée. Les sortes livrées sont
`amener` et `informer`. Un refus retourne `None` sans aucune écriture.
Le parent est un identifiant local à son titulaire ; l'enfant reçoit une
origine `mandat` avec `de`, `parent`, `minute`. Le parent conserve ses
références `confies` (`titulaire`, `agenda`). `filiation` retourne la chaîne
racine → enfant, `enfants` ses références sortantes, toujours copiées.
La profondeur est dérivée des liens persistés, sans compteur redondant.

Avant publication : rejet d'un titulaire déjà dans la chaîne (dont A→B→A),
et rejet d'une troisième arête, avec causes distinctes et `attendu`.
Un même parent, titulaire, sorte et condition réutilise le même enfant ;
l'ordre, les doublons et la forme chaîne/liste des destinataires ne créent
pas de nouvelle condition. `confirme` renouvelle la date de confirmation,
sans changer l'origine ni réveiller un résultat terminal. Les projets
déclarés du titulaire sont activés avant l'insertion pour ne pas les perdre.
La manière du parent est héritée et le plafond commun de trois actifs reste
appliqué. La publication est interdite pendant une évaluation provisoire :
elle doit être appelée après le devis et le jugement d'acceptation.

`agendas.verifier`, déjà appelé par la validation des esprits à la recharge,
contrôle les références réciproques, la profondeur, les cycles, les dates,
les enfants absents, les références et conditions dupliquées. Aucun raccord
dans `esprits.py` n'est nécessaire. Le contrôle AST protège aussi l'accès
aux nouveaux champs `confies` et `confirme` hors du module.

## Vérifications et mesures

**25 tests distincts verts, cinq fichiers directement concernés** :
`test_agendas_mandat`, `socle`, `activation`, `amener_fin`, `evaluation`.
Passe initiale de cinq fichiers : 24 succès et un échec de prémisse du nouveau
test (il assimilait `amener` à une marche sur soi). Le parcours a été corrigé
pour exercer la demande sociale commune à autrui. Fichier mandat final :
**5/5, 4,175 s** ; les quatre autres fichiers : **20/20** dans la passe initiale.
Deux sortes, deux niveaux, refus sans mutation même après une acceptation,
relance, cycle, troisième niveau, corruption des liens et doublon de condition
couverts. Sauvegarde réelle/recharge, monde, rendu et scène perçue identiques.
La parole est réellement transmise, la demande de déplacement réellement
acceptée et exécutée par la marche ; une relance conserve l'enfant atteint.
Un engagement historique est chargé inchangé après création d'un mandat.

**Empreintes validées : 20/20 paires identiques**, référence figée `59cb572`
contre branche `28983ff`, 2 h, Relais/mine/auberge/crue/`crue_hameau`, graines
1985/7/42/2024. Chronique, mesures et **état final complet identiques**, sans
retirer de champs : aucun champ nouveau n'est créé tant que l'API n'est pas
appelée. Zéro plantage sur les quarante nuits ; avis inchangés, **2 → 2 non
justifiés**, **39 → 39 à expliquer** (les deux non justifiés sont dans la crue,
graines 7 et 2024). Ces constats préexistants ne sont pas résolus par ce socle.
Un travailleur réduit, référence puis branche ; les vingt références exactes
manquantes ont été calculées une fois puis rangées dans le cache commun.
Pas de conclusion de performance. `fin.json` : code 0, fin le 2026-10-28 à
17:53:02 +01:00 ; bilan `empreintes.json`, divergence nulle.

Bruts : `C:/Users/msics/donjon/artifacts/filiation-252/` : tests initiaux,
`tests-mandat.json`, `calcul.ps1`, `empreintes.log`, résultat et fichier de fin.
Les tests ont nécessité une exécution hors bac à sable : les répertoires
temporaires Python y étaient inaccessibles. Premier lancement du banc arrêté
avant toute nuit (argument `hameau` corrigé en `crue_hameau`), journal et fin
archivés avec le suffixe `lancement-initial`. Push d'abord refusé par le contrôle
automatique, puis autorisé après présentation de la ligne de livraison du brief.

## Limites

Socle de filiation uniquement : aucun appel automatique depuis les décisions,
aucune sélection, autorité, parole nouvelle, compte rendu, réaffectation ou
conversion d'ancien contrat. L'acceptation est fournie par l'appelant, non
prouvée par cette API. Le contenu de parole reste à juger par le contrat
social existant ; l'API ne transforme pas un propos en vérité du monde.
Le suivi et les échéances propres aux mandats restent pour les lots suivants.
L'identité du jeu est prouvée sur ces vingt paires, pas sur toute partie possible.
Ni suite complète, ni Luna, ni scénario/MJ/moteur de décision modifiés.
