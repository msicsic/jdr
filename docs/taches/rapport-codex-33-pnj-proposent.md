# Lot 33 — Les PNJ proposent (A2b)

**Lot non validé. Branche `codex-pnj-proposent`, non fusionnée**, base `ffcc295`.
Code signé SSH et vérifié : `1bf5be8`, `e58e7ca`, `0353c00`, `684ee70`.
Créneau de 45 minutes dépassé ; aucun appel Luna, quatre travailleurs au plus,
priorité réduite, aucune modification de `main`.

**Invariant réalisé et limites de preuve.** `pnj_propositions.gestes`, déclaré une
fois dans `planification.gestes`, offre biens/parts déjà portés, pièces et services
selon le devis commun. `echanges.evaluer_proposition` puis `proposer` tranchent avant
publication ; les engagements passent par `agendas`. Validation selon les connaissances du proposant. `relations.chance_proposition` ajoute la valeur crue de
la contrepartie à `chance_demande`, sans lire l'attitude privée de l'auditeur.
Leurs lectures entrent dans `_entrees`. Les devis sont indépendants du but ; leur
contrôle se partage sous `VERIFIER` pour un état intégral identique.

`Monde.adopter` conserve les références du moteur au plan courant et attribue les
références publiques des objets nouveaux avant affichage. Une tâche de marché
exige un effet réel ; `agendas.renonce` compare travail et `prix_faute`. Un bien cédé
garde une valeur quand son propriétaire n'a aucune pièce.

**Mesures intermédiaires, non représentatives d'une validation finale.** Banc 4 h,
quatre graines, contre `ffcc295` ; référence calculée une fois puis réutilisée.
Sommes sur quatre graines :

| Scénario | Offres / acceptées | Tenues / trahisons | Vols tentés avant → après | Minutes sans recours avant → après |
|---|---:|---:|---:|---:|
| Relais | 3 / 2 | 0 / 2 | 6 → 4 | 180 → 60 |
| Mine | 10 / 2 | 0 / 0 | 2 → 2 | 65 → 50 |
| Auberge | 11 / 1 | 1 / 0 | 0 → 0 | 80 → 20 |
| Crue | 4 / 0 | 0 / 0 | 9 → 9 | 300 → 300 |

Seize nuits sans plantage ni usurpation. Nouvelle observation `voir_alterne` au
Relais 7 ; devoirs satisfaits mais PNJ immobiles à la mine 2024 : absence de boucle
nouvelle non prouvée. CPU apparié, versions lancées ensemble, 4 h, 42/1985 : mine
**11,72 → 83,16 s**, auberge **11,53 → 78,16 s** en moyenne (**+610 % / +578 %**),
avant le dernier mémo. Mesure finale à refaire ; cible +10 % non validée.

**Vérification.** Moteur final : **22 tests ciblés verts**, dont dix A2b : crue/mine,
méfiance, promesse exécutée, pièces, honnêteté 90/20, crochetage, abandon, état et
rendu après recharge, découpage temporel. Les anciens parcours isolent leur recours par des
refus d'offres antérieurs, données de scène ; A2b laisse les offres ouvertes.
Suite unique sur versions de travail, trois processus, interrompue : **120/156 fichiers achevés,
1 504 tests exécutés, 36 fichiers non achevés**, sans bilan global vert. Contrôle
spatial 1 + `VERIFIER`, crue 2 h/42 : achevé sur version intermédiaire ; mine :
défaut de clé corrigé, reprise interrompue pour son coût. Contrôles finaux incomplets.

**Reprise.** Valider coût, fichiers manquants et contrôles sur `684ee70` ; expliquer
chaque vol restant. Critère de 3e (offre avant vol dans la moitié des nuits
concernées) ouvert. Recherche bornée, contreparties déjà
portées, services suggérés par sources connues et serrures crues ouvertes, refus
retenu par objet demandé : toutes les offres possibles ne sont pas explorées.
Convertir demandes/ventes changerait prêts en cessions, parts servies en remises et
ventes sans jet en marchés évalués ; conversion, réparation et intermédiaires restent
hors lot.

Traces : `artifacts/33-{rapide-final,temps,suite-partielle,reprises,marches-final,cibles-finaux}.json`,
`33-controles-2h/`, `33-controles-correction/` et journaux (non versionnés).
