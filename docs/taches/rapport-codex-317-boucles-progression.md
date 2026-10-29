# Lot 317 — Deux boucles, deux causes distinctes

Diagnostic seul, base `integration 2ddfbe0`. Aucun code du jeu modifié.
Bruts : `C:/Users/msics/donjon/artifacts/boucles-317/`.

## Reproduction et frontière

Les deux nuits de `27ff8c4` sont reproduites avec `audit_nuits`, mêmes paramètres
que le 284 : 12 h, départ tiré, joueur passif en `chambre_cloche`. Chronique,
empreintes, récit, souvenirs, mesures, relevés, bilan final et sonde **identiques
aux archives**. Les témoins `0bad227` sont réutilisés, sans relance.

Bissection des fusions : `cc40031` positif, `7c12e8f` négatif, **`01d32e5`
(lot 266) positif**, puis contrôle de son **parent direct `1852d6e` négatif**,
pour les deux nuits. Les chroniques de `01d32e5` égalent même celles de
`27ff8c4`. Le 266 introduit donc ces manifestations ; cela n'attribue pas à lui
seul toutes les lacunes des contrats qu'elles révèlent.

| Maximum de passages du PNJ par heure | Parent `1852d6e` | `01d32e5` / `27ff8c4` | Intégration `75b6dfb` |
|---|---:|---:|---:|
| Hameau 1985, Aubin | 5 | 120 | 6 |
| Crue 3, Gorm | 16 | 299 | 298 |

Intégration figée depuis `origin/integration` au lancement ; les fusions
ultérieures ne sont pas couvertes par ces deux nuits. Quatorze nuits ciblées
au total, strictement séquentielles et à priorité réduite, dont deux contrôles
sans sonde également identiques. Aucun banc comparatif, Luna ou suite complète.

## Causes établies

**Aubin : le rendez-vous réussit, sa demande n'aboutit pas.** Entre 540 et
649 min inclus, Sève appelle Aubin **110 fois et le retrouve 110 fois**. Les
109 reprises signalées ne prouvent donc pas une marche sans arrivée ni une
absence réelle de nouvelle parole. À 540,083 min : appel, « J'arrive ! » ;
540,155 : arrivée au palier (`beffroi`) ; 540,230 : « Me voici ! », clôture du
rendez-vous par `appel.tenir` / `retrouves`. `deliberation.choisir` rend alors
Aubin au secours `pres marchand`, retenu sur la détresse crue de Gorm ; il
repart à 540,288, avant la demande de vivres de Sève préparée à 540,250.
L'inspection de contact consommée, Sève reprend au prochain tour et rappelle.
La progression du rendez-vous est effacée avant la tentative qu'il préparait.
Les approches de `rester` manquées et la case inconnue de l'interlocuteur
participent au contexte : **recoupement avec le lot 313**, sans démonstration
que ce lot suffise à corriger toute cette chaîne.

**Gorm : un constat admissible n'a pas de coût, puis le moyen est remplacé.**
Le libellé historique « informer Ilse » est trompeur : l'état porte l'agenda
`evacuer_crue`, de sorte `amener` (rendu corrigé depuis par le 309). Ilse accepte
d'aller à la galerie à 170,015. À l'arrivée de Gorm, `_amener` propose
`inspecter chambre_cloche` pour constater l'aide attendue, sans remplir
`mesure`. `agendas.choisir_mandataire` valorise alors le recours propre à
**l'infini** et choisit une délégation finie au refuge. Hors du rendez-vous,
le retour vers la galerie redevient le moyen propre moins coûteux ;
`choisir` remplace le suffixe avant son accomplissement. Le circuit repart,
sans inspection ni constat conservé. Neuf arrivées observées entre 170 et
180 min présentent cette inspection sans coût remplacée. Ce défaut ne vient
pas d'une interruption de `_approcher` ni de `trajet_estime.approche`.

## Preuves, limites et lots proposés

Captures à 530 et 160 min, avant les circuits : sauvegarde/recharge identiques
pour **monde, rendu et scène**. Les reprises de 15 min égalent les archives
(547 et 113 lignes cumulées). La chronique interne ne garde que 300 lignes :
le premier contrôle du hameau comparait à tort ce tampon à toute la période ;
la consolidation par `_nouvelles` confirme l'identité. Quinze minutes d'un bloc
ou minute par minute donnent le même monde, rendu et scène après recharge,
avec 22 et 30 passages respectivement. Les textes intermédiaires de bilan des
présences diffèrent selon le découpage ; leur identité n'est pas revendiquée.
`fin-diagnostic.json` et `fin-consolidation.json` font foi ; l'assertion exploratoire
erronée « plan vide » de `fin-cloture.json` reste archivée : le plan observé est
une **inspection sans coût**. La disparition naturelle d'Aubin sur `75b6dfb`
ne garantit pas son invariant ; Gorm y boucle encore.

Contrat commun proposé : **retenir la progression de la demande et de ses
moyens jusqu'au constat utile ; un simple retour au même lieu ou une variation
de coût due au déplacement ne réhabilite pas un circuit déjà vain.** Deux petits
lots successifs, un invariant chacun : (1) transmission du contact obtenu à la
tentative préparée, ou rupture explicite, dans appel/choix/approche ; (2) coût
typé de tout recours admissible, inspection et attente comprises, puis continuité
de ce moyen dans agenda/choix. Garder ces états après sauvegarde, reprendre sur
un événement pertinent ; aucun délai arbitraire ni interdiction de revisiter.
Chaque correction devra rejouer son cas réel et un autre contact/agenda après
recharge. Aucun de ces correctifs n'est implémenté dans ce diagnostic.
