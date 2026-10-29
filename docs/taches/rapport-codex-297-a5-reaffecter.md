# Lot 297 — réaffecter une charge en retard

Branche `codex-a5-reaffecter`, **non fusionnée**, base intégration
`83a2e89`, moteur `4c634cb`, 29 octobre 2026. Ni MJ, scénario, protocole
joueur, Luna ni suite complète modifiés ou lancés.

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
erreur ou ignoré ; dernières versions par fichier, **145,231 s cumulées**,
deux travailleurs réduits au plus. Dix nouveaux tests : Gorm/Aubin/Ilse
et Brune au hameau, Bram/Josse/Mathe et Lucien à la mine, déplacement et
information. Remplacement réellement accepté, refus réellement prononcé
et non redemandé, retrait entendu ou manqué, état privé caché invariant,
retrouvailles, résultat constaté et compte rendu en route, suffixe périmé,
absence de retour aux anciens titulaires, VOL 1/20 et échéance physique.
Monde, rendu, scène et écoute sont contrôlés après sauvegarde/recharge ;
les intervenants agissent pendant les laps entiers/découpés identiques.
Le contrôle AST réserve aussi `attributions` à la façade des agendas.

**Empreintes en cours**, 2 h, hameau/mine/Relais × 1985/7/42/2024,
référence figée `83a2e89` et cache commun, deux processus réduits, référence
puis branche. Aucune comparaison de temps avec des références en cache.
Bruts : `C:/Users/msics/donjon/artifacts/reaffecter-297/` ;
`tests-bilan.json`, `empreintes.json`, `empreintes.log` et fichier de fin
`fin-verification.json` (écrit aussi en cas d'échec). La clôture des
empreintes reste à constater ; aucun banc 4 h supplémentaire tant
qu'aucune réaffectation naturelle n'est constatée.
