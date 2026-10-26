# Lot 116 — Rapports narratifs cohérents par construction

26 octobre 2026 — `codex-rapports-illisibles`, **non fusionnée**, base
`5ff7ce5`, code signé SSH **6949ca6**, signature vérifiée. Luna `gpt-6-luna`,
ChatGPT medium/libre ; quatre exécutions au plus.

**Cause, établie avant modification.** Sur 280 audits archivés,
`b0042c9` produit sept segments incompatibles dans sept audits sur 124 ;
`91a4351`, 45 dans 35 audits sur 156. Tous sont `mecanique` +
`sans_fondement` (5→37) ou `contradictoire` (2→8) : perception/absence,
orientation, préalable/résultat, geste accompagnant une parole, sans ambiance
pure ni réplique seule. Les 9→44 appels supplémentaires attribués au lot 113
comptent aussi leurs suites. Le schéma permet les 32 paires depuis 83, alors
que le lecteur en interdit quatre. Les variantes de 95 gardent cette lacune ;
schémas identiques sur un même dossier entre 95, b0042c9 et 91a4351.
La hausse est observée après 95, avant 112 ; les instructions ont changé
notamment sur la perception en 102, sans causalité isolée à un lot précis.

**Invariant.** `narration.schema_audit` sépare six natures et quatre
fondements mécaniques (douze variantes). `controler` déduit le verdict
négatif d'une nature mécanique non fondée ou contradictoire ; les autres
natures conservent leurs contrôles, y compris négatifs. Le rapport canonique
est relu avant sauvegarde. Aucun prompt narratif, garde ou scénario changé ;
`mj._appeler` utilise le schéma commun. Les 68 rapports archivés rejetés ou
illisibles donnent exactement les mêmes contrôles qu'en 91a4351. Paires
anciennes incompatibles et mélange des deux formats restent illisibles.
Un premier filtrage des paires, abandonné, admettait des absences non prouvées :
il forçait à choisir entre nature mécanique et portée négative. Ses mesures
(`rejeu`, `variance`, `banc/`) sont exclues du bilan final.

**Rejeux exacts finaux.** 42/42 audits illisibles devenus lisibles :
32 refus, dix admissions, zéro erreur ; les absences explicites non prouvées
du guet sont refusées. Sur quinze refus narratifs de 91a4351, onze sont
retrouvés au premier appel. Quatre écarts rejoués cinq fois par schéma,
entrées et instructions archivées inchangées :

| Cas | Refus ancien → final / cinq |
|---|---:|
| Crypte P1 T25 audit 1, éclairage | 0→1 |
| Crypte P1 T41 audit 1, anneau | 3→3 |
| Soir-appel P2 T2 audit 4, propriété | 1→1 |
| Soir-appel P2 T2 audit 10, dette conforme | 2→1 |

Un illisible ancien, zéro final sur ces 40 appels. Seuil des lots 93/95
satisfait ; certains refus restent des extractions de compte-objet injustifiées.

**Deux passes des six scripts du lot 93**, référence 91a4351 uniquement
lue du cache, douze SHA-256 inchangés ; repli de périmètre prévu par le brief :

| Ensemble des deux passes | Référence → final |
|---|---:|
| Tours MJ / appels | 78 / 265 → 80 / 266 |
| Appels par tour | 3,397→3,325 |
| Secondes par tour, moyenne / médiane | 11,437 / 9,570 → 11,661 / 10,755 |
| Audits / illisibles | 93 / 18 → 85 / 0 |
| Relances / replis | 17 / 2 → 17 / 1 |

Aucun arrêt, erreur technique ou défaut de recharge. **Aucun gain global de
délai observé**. Poste partagé, temps historiques, lots 112/113 absents de la
référence : aucune attribution causale de latence au seul schéma.

**Tests.** Suite complète unique : **2 029 tests, 16 ignorés, 219 fichiers,
2 270,43 s**, sans échec ni erreur, deux processus réduits. Lancée avant le
dernier format ; ses sept fichiers consommateurs repris sur le format final :
**71 tests verts, 23,98 s**, aucune seconde suite complète.
Exhaustivité des qualifications, refus forgés, compatibilité ancienne,
console/recharge sur la capture réelle `signes-guet` et l'orientation de Gorm :
état et rendu conservés, refus direct sans redemande d'audit.

**Limite.** Cohérence typée déterministe, justesse du fondement et des
extractions toujours sémantique ; aucune garantie générale d'absence de faux
refus ou de fausse admission. Aucun banc moteur, simulation inchangée.
Bruts et scripts : `artifacts/illisibles-116/`, résultats finaux préfixés
`final-`, `verification.json`, `historique.json`, `tests-*` ; archives sources
en lecture seule, empreintes vérifiées.
