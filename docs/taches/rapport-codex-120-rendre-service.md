# Lot 120 — Regagner la confiance en rendant service

Branche `codex-rendre-service`, **non fusionnée**, base `0a53910`.
Code signé SSH `7ec9fbc`, signature vérifiée.
Sans Luna, sans modification de `social.py`, `ouie.py`, des scénarios ni de la recherche.

**Invariant.** `services.preparer/constater` encadrent les effets de `pnj._executer`
et `Moteur._appliquer` : manque cru, modification effective, auteur et résultat perçus,
puis croyance de l'effet et épreuve commune `service_rendu`. Dons et repas spontanés,
joueur compris : confiance +20, affection +10, rancune −15, dette +20, modulations et
hystérésis conservées. Une preuve rejouée ne crédite ni relation ni nouveau recours.
Prestations convenues, prêts et restitutions gardent leurs épreuves, sans double crédit.

`pnj_propositions.rendre_service/plan_recours` réutilisent les devis existants après
méfiance ou rancune et les moyens ordinaires, avant une faute envers le même PNJ.
Une tentative persistante par refus/besoin, un candidat autonome, aucune fourniture
future ni délégation. Le projet reprend après sauvegarde, cède aux moyens ordinaires
et cesse avec le refus résolu. Aucun droit inventé. Le constat lève le refus retenu
comme moyen nouveau, sans garantir la demande suivante.

**Preuves.** Brune recharge le brasero qui sert Gorm ; Joss verrouille une réserve
commune avec sa clé pour Odile : confiance 25 → 45, méfiance levée, redemande et repas
obtenus. Monde et journal rechargés ; même laps découpé, chroniques et esprit identiques.
Huit tests nouveaux : joueur, absence de témoin, impossibilité, rancune, droits, preuve
rejouée, prestation payée et ancien refus résolu. Identité inconnue également contrôlée.

**Suite complète unique.** **2 048 tests, 16 ignorés, 221 fichiers, 1 860,72 s**, deux
processus réduits. Sept échecs d'ancienne attente de don ou d'empreinte : les nouveaux
registres sont retirés des projections historiques seulement s'ils sont vides ; oracles,
plans et rendus inchangés. Une erreur Windows `os.replace` dans la TUI avant le geste.
Reprises **28 tests métier verts en 20,19 s**, puis **un test TUI vert en 3,17 s**, sans
modification de son code. **Bilan consolidé vert**, aucune seconde suite complète.

**Banc et CPU.** 4 h × quatre scénarios × quatre graines, départs tirés, copies
locales lancées ensemble, un processus réduit chacune, sans cache pour le temps.
CPU base → branche, sommes des quatre graines, en secondes :

| Relais | Mine | Auberge | Crue | Total |
| --- | --- | --- | --- | --- |
| 21,750 → 21,719 | 69,734 → 69,922 | 55,672 → 55,766 | 66,094 → 66,281 | **213,250 → 213,688 (+0,21 %)** |

**16/16 audits, indicateurs de boucle et chroniques hors relations identiques**,
aucun plantage ni usurpation. Propositions/acceptées identiques : Relais 0/0,
mine 10/1, auberge 3/1, crue 5/0. Trois repas spontanés rendus et constatés dans
la mine (Mathe → Lucien), zéro demande accordée ensuite ; ailleurs zéro service
inscrit. **Aucune réparation délibérée de méfiance observée naturellement** : ce
parcours est prouvé par les deux scènes ciblées, pas par un gain statistique.
Mesure ponctuelle sur poste partagé. Base conservée dans le cache autorisé ; bruts
`artifacts/service-120/`. Aucun banc long ni appel au modèle.

**Limites.** Choix sur manques observés, sans buts privés ; un seul candidat peut en
masquer un autre. Sans geste et cible perçus, aucune preuve ; droits antérieurs nécessaires.
Un lien très dégradé peut rester méfiant ou rancunier : aucune bande forcée.
Vérifications lourdes laissées à l'intégration ; créneau dépassé par la vérification.
