# Lot 213 (196 c) — contrat partiel, arbitrage avant fusion

**`codex-contrat-engagement`, non fusionnée.** `cca5f50` vérifié, 211 puis
`3aa16f7` (219) intégrés ; moteur final **`5016c87`**. Aucun Luna, deux travailleurs
réduits maximum. Commits non signés, aucune clé. Bruts/manifeste exclusivement
`C:/Users/msics/donjon/artifacts/engagement-213/`.

**Contrat.** `choisir` revalide avant l'arbitrage, même à plan vide/hors de vue.
La façade `agendas.py` lie demande, parent, raison crue, phases et sortie attestée
à l'intention, sans agenda de secours. Une recherche indéterminée attend sans
geste périmé ; une délégation payée suspend l'action propre. Les moyens ne sont
conservés que si leur tête revalidée est identique, contenu/prix compris.
**217 : `INERTIE + VOL/4`, aucun coût passé** ; coûts futurs des moyens au
planificateur, raccord supplémentaire de coût de bascule non défini.

**Péril.** `pnj.refus_etape`, partagé par choix et `agir`, juge la tête sur l'eau
et les routes crues, sans nouvelle lecture réelle. `_plan_abri` essaie d'autres
moyens ; `PERIL_EAU` reste absolu, aucune attente retenue dans l'eau. Raccord
autorisé par l'utilisateur ; AST : seuls `agir`/`refus_etape` changent dans pnj.
`_abriter`, témoins/voisines et `_lieu_cru`/`salle_crue` intacts.

**Sept écarts, assertions conservées, tous verts dans la suite finale :**
- `test_amener_flamme` : scène sans repas de secours concurrent achevant le plan.
- `test_besoins` : moyens revalidés conservés ; livraison de Gorm isolée des secours tiers.
- `test_constater_rumeurs` (Odile) : pas d'appelant secourable concurrent de Mireille.
- `test_corps` : pas de seconde commande de secours par un tiers.
- `test_mine` : don initial du bois à Josse explicite ; charges entières réellement brûlées.
- `test_refus_retenus` : attente déléguée ; tête périmée remplacée, pas d'offre répétée.
- `test_tensions` : achat d'Ilse isolé des achats pour secourir un tiers.
Autres prémisses : serrure de Lucien résistante (jet fixé), tentative sous témoin
sans repas tiers. Une fin de secours exige condition accomplie et cause persistée.

**Preuves.** 48 ciblés verts, puis **2 448 tests / 283 fichiers, deux échecs Mimo
préexistants (`6 != 5`), zéro erreur**, passage complet unique après raccord,
2 179,317 s. Les mêmes deux échecs sont reproduits sur `3aa16f7` ; suite non verte.
Captures réelles 209/211 et hameau 42 min 135, autre PNJ/but/scénario ; monde,
rendu/scène rechargés et laps entiers/découpés contrôlés.

**Banc 219 : 20 paires de 4 h**, vingt références du cache. Classes : suspects
**13 → 5**, cycles **486 → 468**, préemptions légitimes **57 → 53**, autrui **1 → 0**,
progrès **0 → 0**, à expliquer **97 → 61** ; séparément, dérives **185 → 196**,
états payés perdus **7 → 6** (durée non spécifiée). Zéro plantage/usurpation,
aucun scénario en hausse de suspects. Attente/sans recours/eau : moyennes PNJ·min ; S/F/D : 183.

| Scénario | Suspects | Attente / sans recours | Eau | S/F/D avant → après |
|---|---:|---|---:|---|
| Relais | 3 → 0 | 0/0 → 0/0 | 0 → 0 | 11,25/3,75/1,5 → 9,5/3,5/1,438 |
| Mine | 1 → 1 | 0/0 → 0/0 | 0 → 0 | 22/4,25/1,607 → 25,5/4,5/1,964 |
| Auberge | 2 → 2 | 0/20 → 0/20 | 0 → 0 | 12/4,25/1,063 → 11/4,25/1 |
| Crue | 2 → 2 | 178,75/0 → 196,25/0 | 2,5 → 1,25 | 14/6,75/2 → 17,5/7,5/2,625 |
| Hameau | 5 → 0 | 128,75/0 → 97,5/0 | 10 → 6,25 | 31/8/2,542 → 31/7,5/2,667 |

**Limites/arbitrage.** Hameau 42 après raccord : **120 → 5 PNJ·min d'eau sur la
nuit entière** ; ancien séjour de Brune de 110 min supprimé, sortie à 135 min.
Attente crue en hausse ; cinq suspects restants (trois après `MANQUE`, deux a1).
A1 hameau 2024 : activations/sommeils 5/6 → 5/4 ; Gorm sans but 160 min, confiées/attente.
Alertes nouvelles : Gorm Relais 42 en charge confiée, répétitions d'états d'agenda
crue 1985 réparties de 1 à 124 min ; lecture répétée mine 7. **Absence générale
de boucle et liste fermée des sorties non garanties**, notamment pour les sources
anciennes sans demande persistante. Suspension de charge à travers reconstruction
forcée laissée au **218**. **À arbitrer : l'absence de plan admissible au coût
suffit-elle à suspendre la priorité d'un agenda (politique actuelle), ou doit-elle
garder l'intention en attente ?** Attendre peut bloquer un besoin du même palier ;
libérer autorise les reprises d'a1 observées. Ne pas fusionner avant cet arbitrage.
