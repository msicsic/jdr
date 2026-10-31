# Tâche Codex 437 : la reprise d'une recherche bornée reste comparable à son contrôle

Défaut relevé par la vérification d'intégration 402 (`docs/taches/rapport-codex-402-verif-integ.md`, fusionné, « Petits
lots à ouvrir » ; bruts `C:\Users\msics\donjon\artifacts\verif-integ-4539dd68\`, PC fixe, `cas-a-instruire.json` et
l'archive de l'auberge 42 renforcée). Sous `VERIFIER` + `spatial.VERIFICATION`, la nuit auberge 42 s'arrête à l'avance
**360 → 365 min** : Lucien, but `garder:chambre_chaude`, assertion « ancienne borne, complète » : le résultat repris
coûte **82,7204**, le recalcul complet rend `None`. Sur 8 h, **29 recherches bornées ne trouvent aucun plan alors que le
contrôle complet en trouve** (dès Lucien `placer:ballot`, 303 min), contre 88 anciennes bornes toutes au coût du
contrôle sur `0bad227`. Écart nouveau.

Lis `AGENTS.md`, `docs/etat-dev.md` (court), le rapport 402, `docs/plan-planificateur.md` (contrat des bornes, lot 48 :
« si la référence uniforme plafonne, autre résultat permis seulement au coût de la complète, ou aucun plan si elle n'en
trouve pas » ; `planification.BORNES`, `REFERENCE`), et les rapports des lots S1k/S1m (refus et renoncements publiés)
et 374 (positions datées), qui ont changé des entrées de la recherche depuis `0bad227`.

## Invariant (un seul)
**Un résultat repris (mémoire, graphe ou certificat) égale exactement une recherche refaite sur les mêmes entrées, et une
recherche jouée bornée ne rend un résultat différent de la référence complète que dans les cas permis par le contrat du
lot 48.** Établis d'abord, sur la capture à 360 min (reconstitue-la sur copie), si l'écart vient d'une reprise dont une
entrée manque à la clé (`_entrees`), d'une référence complète qui lit un état différent, ou d'une limite du contrôle.
Corrige la cause commune (clé de reprise, ou contrôle) ; aucun plafond changé pour masquer l'écart, aucune exception de
personnage ou de but.

## Contraintes
**Poste : le laptop.** Fichiers attendus : `donjon/planification.py` (et les lectures concernées), tests. Lots en
cours : 431 (admission préalable), 435 (S1o, mémoire des aides et contrats), 436 (G20, conception), 438 (mandat refusé,
`agendas.py` / `deliberation.py`). Deux processus au plus, priorité réduite, calculs longs détachés.

## Vérification
La capture à 360 min sous `VERIFIER` + `spatial.VERIFICATION=1` : plus d'arrêt, résultat repris égal au recalcul.
Lucien `placer:ballot` à 303 : une borne jouée qui ne trouve rien alors que la complète trouve est soit permise par le
contrat (dis pourquoi), soit corrigée. Autre cas de même nature (mine ou crue). `VERIFIER` + spatial 0,2 sur auberge 42
**8 h** (détaché) : achevée sans arrêt. Empreintes 2 h, quatre graines, auberge et Relais, contre la base. Pas de suite
complète, ni Luna.

## Livraison
Branche `codex-reprise-bornee`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
l'utilisateur ; poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-437-reprise-bornee.md` ; entrée « non
fusionnée » de 8 lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves). Bruts dans
`C:\Users\msics\donjon\artifacts\reprise-bornee-437\` (copie les bruts utiles du 402 depuis le PC fixe par `scp` si besoin).
Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
