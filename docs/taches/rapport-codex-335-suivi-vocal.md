# Lot 335 — protéger à portée de voix

**Terminé, branche `codex-suivi-vocal` poussée, non fusionnée.** Base initiale
`9237e14` ; réaccord sans rebase sur `origin/integration c9b066b` par `51fd593`.
Bruts : `C:/Users/msics/donjon/artifacts/vocal-335/reprise-c9b066b/`.

**Invariant.** L'agenda protéger réutilise le séjour `rester` du lot 266.
`planification.proximite` est commune au contact et à la voix ;
`proximite_vocale.arrivees` utilise `ouie.propager` et `parvenu` : voix
ordinaire, distance, ouvertures et portes crues. Seule l'oreille propre
intervient, sans position ni état auditif privés du protégé. Devis et marche
visent les mêmes arrivées, avec obstacles et tarifs communs. La place
admissible est conservée ; aucune rotation vers une cible inconnue.
Sans localisation, recherche commune payante ; sans case, inspection.
Les lectures acoustiques propres entrent dans `_entrees`. Le rendu
« reste à l'écoute » affirme la veille, sans révéler une présence cachée ;
son souvenir est sauvegardé. Aucun agenda ajouté aux scénarios historiques.

**Fusion.** `_pulsion` garde la demande de cause avant le séjour et la durée
du devis E3. `pnj._approcher` et `trajet_estime.approche` conservent le
terminal vocal et le contact matériel du 313 : perception fraîche,
localisation crue, observation puis contrôle physique du geste. Les ajouts
332/333 et E1–E4/357 restent présents, ainsi que les paliers, secours et fins
sur mort/départ crus. Aucun cas particulier ajouté. `etat-dev` reprend
l'intégration avec une seule entrée 335 de six lignes, non fusionnée.

**Tests ciblés : 414 / 50 fichiers, 409 verts, cinq échecs, zéro erreur ou saut.**
356 tests en 242,771 s, puis 58 en 120,716 s, deux travailleurs réduits.
Les cinq échecs (trois ouïe, deux boucles PNJ) sont reproduits sur
`c9b066b` intact avec traces identiques hors chemins (`attribution.json`).
Aucun nouvel échec ciblé, aucune assertion affaiblie. Les sept tests vocaux
passent : Relais et mine, repositionnement, appel reconnu, recherche,
priorité du désespoir, portée limite, portes crues, coût, invalidation et
inspection sans case ; mondes, rendu et scène rechargés, laps entier/découpé
identiques. Contact 313, attention conjointe 332, gardes 333, agendas,
cause de détresse, délais E1–E4 et tâches payées 357 passent.

**Banc terminé : 20/20 nuits de 4 h**, cinq scénarios × 1985/7/42/2024.
**Zéro plantage, usurpation et suspect certifié 219 dans chaque nuit.**
Un travailleur réduit, détaché ; **1 017,086 s écoulées**, CPU 1 008,328 s,
sans comparaison de temps. `fin.json ok=true` écrit en dernier par le calcul.
Les 220 sources du commit `51fd593` sont inchangées pendant le calcul et à
la clôture ; matrice et archives contrôlées (`analyse-cloture.json`).
Aucun calcul actif, aucune relance, ni suite complète ni Luna.

**Réserves du banc.** Restent 15 alertes de répétition, cinq alternances
aller voir/autre but, trois immobilités sous devoir confié, un noir long,
une dette finale, un but hors besoin ; 43 avis à expliquer, 351 dérives
ouvertes et cinq cessations physiques de service. Exemples : Mathe reste
près de Lucien douze fois (mine 1985), Lucien appelle Hugues huit fois
(auberge 2024), Ilse répète des causes d'inquiétude (hameau 2024).
Ces alertes sont conservées, sans être déclarées corrigées ni légitimes.
Aucune référence compatible de `c9b066b` en cache, aucune référence rejouée :
aucun delta, identité avec l'intégration ou attribution des alertes certifié.

**Limites.** Écoute selon les croyances du protecteur, sans garantie d'audition
réciproque, de retrouvailles ou d'absence générale de boucle. Déplacements
et localisations du protégé fournis par les scènes d'épreuve ; sa marche
autonome entière n'est pas démontrée. Les nuits sans agenda nouveau ne
prouvent pas le suivi actif ; celui-ci est éprouvé en tests. Recouvrements
330 : planification/PNJ ; 333 : agendas/PNJ/protection.
