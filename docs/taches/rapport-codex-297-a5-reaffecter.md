# Lot 297 — réaffecter une charge en retard

Branche `codex-a5-reaffecter`, **non fusionnée**, base intégration
`83a2e89`, moteur `4c634cb`, validation `599dfbb`, 29 octobre 2026.
Lot terminé, branche poussée vers origin, aucun calcul actif. Ni MJ,
scénario, protocole joueur, Luna ni suite complète modifiés ou lancés.

**Invariant.** L'historique `confies` conserve la filiation ; le registre
`attributions` distingue attribution active, remplacement et reprise par
le mandant, par destinataire et contenu de charge. `agendas.confier` refuse
les attributions simultanées qui se recouvrent et le retour à un titulaire
retiré, avec `attendu`. La recharge contrôle cette unicité et les liens.
Une confirmation conserve l'enfant et ne repousse pas son échéance.

`_confies_attendus` rend une charge échue au choix commun faire/confier.
`choisir_mandataire` utilise les devis fermés 258/260, les disponibilités
crues et les refus retenus ; aucun état privé d'avancement n'est consulté.
Un titulaire déjà essayé pour cette charge est exclu. Le moyen entrepris
reste choisi si son surcoût relatif reste dans la marge commune
`marge_engagement` (points convertis en pourcentage, croissante avec VOL).
Le prochain sous-but et le choix du mandataire restent séparés.

**Parole.** Le plan propose d'avertir l'ancien titulaire cru présent,
avant le remplacement, sans détour pour obtenir un acquittement.
`echanges.avertir_mandat` passe par `se_parler`, l'ouïe, l'attribution de
voix, la chronique et `faire_entendre`. Seule une parole comprise et
attribuée ferme l'agenda du titulaire et le réveille pour reconsidérer son
plan. L'avertissement identifie la charge ; les références citées passent
par le rendu commun. Une tentative sans réception reste enregistrée ;
elle ne recommence que si la croyance de présence change, pas sur le seul
temps. Les retrouvailles permettent un avertissement différé. Une
réalisation constatée ou un compte rendu cru arrête le choix en route ;
l'exécution écarte aussi un suffixe de retrait/mandat devenu périmé.

**Échéance et limites.** `echeance_observee` réutilise `duree_devis` dans
la projection du mandant : durée physique, jamais coût pondéré ni esprit
du titulaire. Un plan incertain ne reçoit aucune date inventée. Une date
explicitement connue peut être publiée avec l'accord ; les scènes
`amener` fixent ainsi un rendez-vous convenu. Les mandats anciens sans
date et les conditions historiques du suivi 242 ne sont pas convertis.
Le lot ne garantit donc pas une réaffectation temporelle de ces attentes,
ni la réussite du remplacement. **Deux intervenants peuvent continuer à
agir tant que le retrait n'a pas été entendu** : une attribution unique
dans les croyances du mandant n'est pas une annulation distante.

**Preuves.** **86 tests distincts / 12 fichiers verts**, zéro échec,
erreur ou ignoré ; dernières versions par fichier, **145,226 s cumulées**,
deux travailleurs réduits au plus. Dix nouveaux tests : Gorm/Aubin/Ilse
et Brune au hameau, Bram/Josse/Mathe et Lucien à la mine, déplacement et
information. Remplacement réellement accepté, refus réellement prononcé
et non redemandé, retrait entendu ou manqué, état privé caché invariant,
retrouvailles, résultat constaté et compte rendu en route, suffixe périmé,
absence de retour aux anciens titulaires, VOL 1/20 et échéance physique.
Monde, rendu, scène et écoute sont contrôlés après sauvegarde/recharge ;
les intervenants agissent pendant les laps entiers/découpés identiques.
Le contrôle AST réserve aussi `attributions` à la façade des agendas.

**Empreintes terminées : 12/12 paires identiques**, 2 h, hameau/mine/Relais
× 1985/7/42/2024, départ tiré, `83a2e89` → `599dfbb` : chronique, mesures,
empreintes, SHA-256 de l'état final complet, récit et souvenirs, nuit par
nuit. Aucune nuit divergente ni plantage ; avis non justifiés **0 → 0**,
entrées à expliquer **16 → 16**, avis complets identiques. Aucun mandat A5
accepté ni retrait dans ces nuits : pas de réaffectation naturelle ; la
preuve du comportement vient des scènes ciblées. Aucun banc 4 h ajouté.
Douze références exactes manquantes calculées une fois et rangées dans le
cache commun, puis douze nuits de branche ; deux processus réduits au plus,
**242,022 s**, `fin-verification.json` : **ok=true, code 0**. Aucun gain de
performance déduit. Résultats lus à la clôture, aucun calcul relancé et
sources/tests inchangés depuis validation.

Bruts copiés dans `C:/Users/msics/donjon/artifacts/reaffecter-297/` : tests
et `tests-bilan.json`, `empreintes.json`, journaux, lanceur, fichier de fin,
`analyser_fin.py` et `analyse-fin.json` (lecture des résultats existants).
