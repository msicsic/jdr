# Lot 103 — la garde compatible avec son propre service

Branche `codex-boucle-garde-manger`, non fusionnée ; base `811ae4b`, code signé
`ddfbc36`.

**Cause.** Capture mine 3 à 8 min, rejouée minute par minute avec recharge :
à 9 min, Mathe déverrouille pour servir Lucien ; sa garde interrompt ce plan,
puis le service recommence. Fermeture et verrouillage figuraient pourtant à
sa fin. `retabli_par_son_plan` ne protégeait que les motifs urgents ou les
engagements ; aucun besoin de Mathe n'était urgent. La bissection situe le
déclenchement à `1e7b4d9` (contre-offres, lot 77, code `a8b8603`) : son parent
`38e5d7e` produit 14 gestes sur le garde-manger en 30 min, contre 353 après
fusion. Le contrôle défectueux est plus ancien et inchangé entre ces versions.

**Correction commune.** `deliberation.retabli_par_son_plan` respecte la remise
sous clé prévue par le plan d'un autre but, même non urgent. `retablir` portait
déjà cette restauration : il reste inchangé. L'arbitrage de la garde elle-même
est conservé ; buts et gestes restent revalidés. Aucun délai ni cas de scénario,
aucune route ni intervention sur le MJ.

**Preuves.** Mathe, Gorm servant Brune depuis sa réserve gardée, et garde après
un tiers : monde, croyances, chronique et texte public contrôlés après recharge,
même laps d'un bloc ou découpé. Suite complète unique : **1 988 tests,
16 ignorés, 2 092,61 s**, deux processus réduits ; deux erreurs du nouveau
placement de rendu et une régression intermédiaire de l'arbitrage propre de
la garde corrigées, sans modifier les tests historiques. **33 tests repris
verts en 135,02 s**, sans seconde suite complète.

Banc **4 h × quatre scénarios × quatre graines** contre `811ae4b` : aucun
plantage ni usurpation, mêmes catégories et nombres de constats (huit) ; bascules **0/0/0/5**
et maxima de passages/PNJ/h **8/10/15/24** inchangés. Référence calculée une
fois puis relue du cache ; CPU non comparés, charges différentes. Audit
**mine 3, 12 h** : déverrouiller/ouvrir/fermer/verrouiller
**328/291/291/328 → 3/3/3/3** ; Lucien servi à **9 min** (82 dans le brut initial),
aucun plantage, usurpation ni constat de répétition. **VERIFIER + spatial.VERIFICATION=1, 2 h : aucun écart, borne reconnue, plantage ni usurpation**, 4 532 s à priorité réduite.

**Limites.** Avis textuels redits en mine **3 → 7**, dont Josse 76/79 en graine
2024 (déjà 76/78 en graine 7) ; noir prolongé et besoins sans recours persistent.
Aucune nouvelle classe de boucle signalée, sans preuve générale sur tous les
buts : l'invariant vise les plans portant une restauration sous clé. Aucun
appel Luna. Bruts, captures, bissection et mesures : `artifacts/lot103/` ; bruts
du lot 94 seulement relus dans le dépôt principal.
