# Lot 84 — Une part proposée reste une part à remettre

25 octobre 2026 — Branche `codex-part-proposee`, **non fusionnée**, base d'intégration
`7cce974`, brief `3dbd225`. Livraison sans modification de `main`, `narration.py`,
`mj.py`, du planificateur, des scénarios ou du modèle `gpt-6-luna`.

**Invariant et correction.** La proposition ne demande plus au planificateur la remise du
lot entier avant de détacher une part. `propositions.prestation` distingue la remise d'un
bien disponible en main (`biens.disponible_en_main` : porté ou à portée, contenant ouvert)
du travail explicite et de la livraison à aller chercher. Le prix propre de la part reste
celui de `valeur_proposition`, avec la garde de la réserve, sans protéger toutes les parts
par le devoir portant sur le lot entier. `evaluer_proposition`, `proposer` et `contre_offre`
partagent `_livraison_proposition` : constat des propres biens disponibles, essai sur copie
par `_remettre_part`, puis même chemin à l'exécution. Le devis matériel porte sur la pièce
détachée ; lot, masse et quantité restent conservés. L'accord et le paiement précèdent
l'affichage ; la livraison différée conserve la pièce dans l'engagement et les comptes.
La contrepartie matérielle du proposant doit toujours être en main. Le contrat typé des
tâches admet le service existant `servir` : demander un repas servi garde un devis et un
engagement, même si les vivres sont portés. Aucune nouvelle instruction narrative.

**Tests et mesures.** Quatre nouveaux tests, dont les planches d'Aubin sans enquête
préalable et une autre ressource, chacune portée ou à portée : vraie console avec MJ
simulé, paiement, réserve, propriété, livraison et inventaire après recharge. Réserve
gardée ou part trop chère refusée sans paiement, contre-offre sur le même chemin, soupe
à servir et part dans une autre salle (devis sur la pièce, jamais le lot). Suite complète
unique : **1 912 tests, 16 ignorés**, 195 fichiers, trois processus à priorité réduite,
**1 763,95 s**, aucun échec ni erreur. Après son lancement, suppression du contrôle de
livraison répété dans `proposer` (déjà fait par `evaluer_proposition`) et complément des
tests de refus par la valeur et de la saisie réelle : les six fichiers concernés repris
sur le code final sont verts, **39 tests, un ignoré, 64,47 s**, deux processus.
Pas de seconde suite complète. Banc rapide **Relais, 4 h × 4 graines**, contre `7cce974`
(référence absente, calculée une fois et rangée en cache) : aucun plantage, violation
ni usurpation ; états finaux identiques, trois recherches neuves supplémentaires au total,
mêmes constats d'audit (`fige_presse` : trois nuits). Temps CPU moyen
**7,625 → 6,816 s/nuit** ; un seul couple sous charge variable, aucun gain revendiqué.

**Luna, une passe.** `soir-appel` et `ressources`, ChatGPT medium/libre, copies temporaires ;
référence `7cce974` absente du cache, repli prescrit sur `882907c`, relue sans exécution.
**28 → 39 appels / 7 tours MJ**, **4,00 → 5,57 appels/tour**, **16,2 → 29,8 s/tour**,
relances **2 → 4**, refus **0 → 2**, aucun repli, arrêt ni erreur technique/recharge.
Temps historiques sous une autre charge, aucun gain de performance revendiqué.
Dans `soir-appel`, demande historique d'abord proposée puis faussement rejetée par la
revue de fidélité, correction en proposition, accord et trois pièces payées ; au premier
déplacement suivant, Aubin remet `planches_1`, portée dans les états rechargés suivants.
Or **26 → 23** dans les faits transmis après validation ; aucune nouvelle part prélevée
pendant les relances narratives. `ressources` : réponses sur bois et nourriture exécutées,
sans achat demandé dans ce script. Aucun second passage Luna.

**Limites et bruts.** La remise d'une part posée garde le cycle moteur existant : elle
peut être différée jusqu'au prochain geste qui fait passer le temps. Une part explicitement
à servir est consommée par ce service, pas remise comme objet. Le typage et les audits de
Luna restent sémantiques ; les faux refus de fidélité et les relances narratives du soir
ne sont pas corrigés dans ce lot. Aucun banc des autres scénarios ni audit long.
Bruts dans `artifacts/tests-cibles*.{log,json}`, `tests-complets.{log,json}`,
`banc-rapide.{log,json}`, `verification-luna-lot84.json` et
`bancs-multi/20261025-182117-38300/` du worktree de livraison.
