# Lot 122 — Passer par un intermédiaire, faute de mieux

Branche `codex-intermediaires`, **non fusionnée**, base **219bc8d**.
Code signé SSH **fc5f62a**, puis **76c071a**. Aucun Luna ni scénario modifié.

**Invariant.** La commission utilise `echanges.confier` ; son porteur demande
ensuite en son propre nom, avec ses relations et les refus communs. Le demandeur
choisit un seul candidat connu et joignable d'après ses croyances d'attachement
de la cible envers lui, sans méfiance ou hostilité connue envers le demandeur.
Aucune relation privée adverse ne guide ce choix. Une tentative par refus
social/besoin est sauvegardée, même refusée. Les moyens ordinaires sans faute
priment ; service spontané et commission sont départagés par coût propre :
devis du service ou valeur du don, contre approche et peine commune de commission.
Une commission acceptée s'attend avant une faute envers la cible.

**Contrats communs.** Le porteur peut acquérir le bien même à servir ou livrer,
sans déléguer le travail. `confier` conserve un seul jet, dont le DD compte
altruisme, lien et coût du `devis_service`. Une nourriture explicitement demandée
à emporter passe par `_remettre_part`, sans nourrir personne à l'accord.
`agendas.affecter_part` lie une seule tâche à la part effectivement reçue.
Le devis d'une remise chiffre acquisition et livraison ; `servir` et `remettre`
tiennent la parole après le geste, même si le livreur n'est pas propriétaire.
Aucun transfert ni droit nouveau à l'acceptation. La demande au cédant ne nomme
pas le bénéficiaire ; une commission entendue peut le révéler. Registre durable,
chronique, journal perçu et trois compteurs : sollicitées, acceptées, abouties.

**Preuves.** Huit tests nouveaux : Brune/Ilse/Gorm en crue et
Joss/Mireille/Odile à l'auberge, refus direct réel puis part reçue et repas,
monde/journal rechargés et même laps continu/découpé. La cible reste méfiante
envers le bénéficiaire. Bien durable livré sans droit inventé, choix indépendant
des relations privées, croyance favorable nécessaire, méfiances connues/réelles,
refus de la cible sans boucle, unique jet sans remise à l'accord, ordre des coûts.
Les oracles historiques excluent le nouveau registre seulement s'il est vide.

**Suite unique.** **2 065 tests, 16 ignorés, 223 fichiers, 3 634,73 s**,
un processus réduit. Un échec de fourniture et une erreur Windows TUI.
Le premier a révélé une dépendance indirecte : le commanditaire pouvait promettre
une fourniture après une demande future à un tiers. `devis_service` vérifie
maintenant aussi l'autonomie de cette livraison, pour parts et biens indivisibles,
sans supprimer les fournitures permises au commanditaire. Cas réel Ilse/crue 7
minute 353 et autre lot conservés. Reprises finales : **55 tests verts en
104,54 s**, puis **un TUI vert en 8,42 s**, sans changer la TUI.
**Bilan consolidé vert**, aucune seconde suite. Créneau dépassé par la suite séquentielle.

**Banc.** **4 h × quatre scénarios × quatre graines**, contre `219bc8d` :
**16/16 chroniques, mesures métier, audits et boucles identiques**, aucun
plantage, violation ou usurpation. **Zéro commission naturelle** sollicitée,
acceptée ou aboutie : preuve par scènes d'auteur seulement. Référence calculée
une fois puis cachée ; aucune comparaison CPU entre versions successives.
Ce banc concerne **fc5f62a**, avant le resserrement des fournitures ; celui-ci
est contrôlé par les reprises ciblées, sans second banc. Bruts `artifacts/intermediaires-*`.

**Limites.** Attachement interprété éventuellement faux ; sans signe favorable,
pas de candidat. Coût de commission conventionnel, pas futur temps réel du porteur.
Fournitures accessoires de tiers et travail délégué exclus. Transmettre un bien
durable ne transmet aucun droit d'usage supplémentaire : les permissions
antérieures conservent leur portée. Fréquence naturelle et gain CPU non établis.
