# Lot 88 — Les avis se disent dans les nuits réelles

Branche `codex-avis-reels`, non fusionnée ; base **c9245dd**, code signé SSH
**1dffefd**. Sans Luna, changement de profil/scénario, ni modification de
`main`, `planification.py` ou `deliberation.py`.

**Invariant.** Une conclusion de menace commune ne vaut pas identité des preuves.
`social._sait` ne supprime plus l'avis pour ce motif ; `_auditeur` ne consulte
plus la prévision privée du destinataire. `recevoir_prevision` compare les preuves
après la parole. Le registre borne aussi les avertissements déclinés. Le souci
altruisme + empathie + affection ≥ 100 ne bloquait aucun cas : seuil conservé.

**Diagnostic.** Base sur copies, départ tiré, joueur à la galerie ; photographie
après perception de chaque minute entière. Unité : minute × locuteur × salle
menacée × autre PNJ ; filtres recouvrants. Identités/localisations conservées
dans `artifacts/88/diagnostic-{500,2024}.json`.

| Filtre / population | 500 | 2024 |
| --- | ---: | ---: |
| Locuteur × salle menacée × minute | 7 466 | 6 955 |
| Paires avec un autre PNJ | 22 398 | 20 865 |
| Localisation crue inconnue | 553 | 3 676 |
| Autre cru ailleurs que dans le lieu menacé | 18 244 | 16 555 |
| Souci < 100 / déjà dit | 0 / 0 | 0 / 0 |
| Salles réelles différentes | 2 682 | 8 697 |
| Hors de portée de parole ou présence non reconnue | 2 800 | 10 900 |
| Auditeur source de l'avis | 60 | 223 |
| Auditeur croit déjà une menace (`_sait`) | 22 392 | 20 396 |
| Plan actif sans créneau de confidence | 3 579 | 9 120 |
| Minute de confidence déjà prise | 0 | 0 |
| **Tous les filtres passent sauf `_sait`** | **3 327** | **44** |

L'exploration comptait plusieurs occasions par minute ; ce tableau ne compte
que ses frontières. Les diagnostics retrouvent les mesures de la base : zéro
avis/adoption, eau **1 095 / 275 min·PNJ**. Aucune comparaison de performance.

**Preuves.** Trois tests sur captures complètes avant Aubin → Gorm à **72 min
25,5 s** (500), Aubin → Ilse à **102 min 25 s** (2024). Dix minutes d'un bloc ou
par quinze secondes sauvegardées : monde complet, avis, rendu identiques.
Preuves propres conservées ; joueur distant : voix sans mots. Prévisions privées
modifiées : même auditeur choisi. **24 tests ciblés verts**, dont trois nouveaux.

Banc **4 h × quatre graines × crue/Relais**, c9245dd : **0 → 18 avis**, zéro
adoption ; eau **133,75 → 133,75 min·PNJ**, mêmes alertes et compteurs de boucles.
Relais : quatre mondes finaux/chroniques identiques. Aucun plantage, violation ou
usurpation. Huit références absentes calculées une fois, puis mises en cache.
Suite complète unique : **1 930 tests, 16 ignorés, zéro échec/erreur**,
199 fichiers, deux processus à priorité réduite, **2 231,5 s**.

| Audit branche seule, 12 h | Avis / adoptions | Eau min·PNJ (base → lot) | `eau_longue` | Lieux finaux |
| --- | ---: | ---: | ---: | --- |
| 500 | 16 / 0 | 1 095 → 1 085 | 4 | Gorm refuge ; Brune galerie ; Ilse conduite ; Aubin vannes |
| 2024 | 6 / 0 | 275 → 325 | 1 | Tous au refuge |

Aucun plantage/usurpation. Les 22 avis sont déclinés et tous distincts par
locuteur/destinataire/lieu. Bruts : `artifacts/88/audit/`, `audit-analyse.json`.

**Limites.** Adoption exercée par les tests du lot 80, pas ces nuits. Eau longue
non résolue. Nuit 2024 modifiée : violence à 649 min, va-et-vient et **237 passages
en une heure** ; absence de boucle nouvelle non démontrée. Créneau désœuvré/attente
et une confidence par minute conservés : avertissement immédiat non garanti
pendant un plan actif. Ni priorité nouvelle, dispute, ni autre prédicat.
Priorité réduite, trois processus au plus (banc à un, suite à deux).
Créneau de 45 minutes dépassé par la suite complète sous charge partagée.
