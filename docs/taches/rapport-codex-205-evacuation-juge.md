# Lot 205 (196 b) — péril d’eau et abri communs

Branche `codex-evacuation-juge`, **non fusionnée** ; départ `71bb01d` vérifié,
puis reprise demandée sur **`ef86cab` (204 intégré)**. Aucun Luna, deux calculs
réduits au plus ; aucune clé Git, commit non signé. Bruts exclusivement
`C:/Users/msics/donjon/artifacts/evacuation-205/`.

**Invariant.** `eau.peril_cru`/`en_peril` jugent le lieu sans intention ;
`route_admissible.refus` partage ce péril. Un repli vers moins d’eau reste possible,
mais `choisir` refuse tout séjour ordinaire en péril, y compris les substitutions
sociales/commerciales. `traversee_sure` vérifie déplacements, délais et issue sèche.
`_candidats` maintient `PERIL_EAU` pour l’évacuation adoptée. `abri_valide` est commun
au choix, à `planification.abri` et à `pnj._abriter` ; la cible valide reste tenue
jusqu’au terme d’`abriter`, sans annulation par le prix du séjour intermédiaire.
**Seul `_abriter` change dans `pnj.py`**, raccord autorisé pour 204 ; aucun changement
de sauvegarde, du MJ ou de `_lieu_cru`/`salle_crue` (autre lot). Périmètre vérifié par AST.

**Cas réels.** Sur le départ, les anciens créneaux de Brune ne se reproduisent
plus : refuge sec/sans intention à 42 min, chambre de la cloche à 204 min.
Le diagnostic **209** fournit les familles actuelles : 25 retours d’eau et sept
cibles d’abri. Quatre états isolés depuis ses captures sont en fixtures : Aubin,
Ilse, Gorm dans l’eau, et cible d’Ilse. Priorité/cible sans entrée nouvelle,
sortie au sec, monde complet/rendu rechargés, laps entier/découpé vérifiés.
Les retours de localisation inconnue ne sont pas traités.

**Vérification.** Suite ef86cab : **2 410 tests / 279 fichiers, 1 996,70 s,
9 échecs, zéro erreur** ; deux MiMo `6 != 5` reproduits sur la copie exacte.
Les sept autres écarts sont retestés avec prémisses explicites : obscurité réelle,
lampe propre éteinte, témoin présent, abri adopté, observation d’un acteur mobile,
extinction puis recharge comptée du poêle. Assertions mécaniques conservées.
**157 ciblés distincts consolidés verts / 17 fichiers.** Une passe complète par
base : la première sur 71bb01d est archivée, la seconde était demandée après 204.
Pas de troisième suite. Moteur final identique à celui de la suite intégrée.
**VERIFIER + spatial 0,2**, crue 1985, 2 h : vert.

**20 paires finales de 4 h contre ef86cab**, compteur 199, référence rangée une
fois ; aucun CPU de cache comparé. Eau/attente : moyennes PNJ·min ; passage : pire
PNJ/heure ; suspects : somme des quatre graines.

| Scénario | Suspects | Eau | Attente urgente | Pire passage |
|---|---:|---:|---:|---:|
| Relais | 0 → 0 | 0 → 0 | 0 → 0 | 9 → 8 |
| Mine | 1 → 1 | 0 → 0 | 0 → 0 | 9 → 9 |
| Auberge | 5 → 5 | 0 → 0 | 0 → 0 | 18 → 18 |
| Crue | 27 → 9 | 13,75 → 7,5 | 77,5 → 102,5 | 28 → 18 |
| Hameau | 24 → 9 | 13,75 → 2,5 | 27,5 → 111,25 | 28 → 26 |

**Limites avant fusion.** Suspects **57 → 24**, entrées à expliquer **272 → 204**,
aucun scénario en hausse, zéro plantage/usurpation. Mais **7/12 empreintes 2 h
identiques** seulement : quatre mondes changés, plus les mesures seules de mine 7.
Le contrat commun modifie aussi les abris hors crue, sans exception de scénario.
Hameau 2024 : huit activations/sommeils d’a1 de Brune (deux nouvelles alertes de
répétition), Gorm sans but 125 min, devoir en attente. Relais 2024 ajoute une
alerte de devoir confié ; celle de Relais 42 se raccourcit. Sans recours en crue :
**15 → 27,5 PNJ·min**. **Identité hors eau et absence de boucle nouvelle non
validées ; aucune garantie générale ni d’attente réduite.** Alertes à expliquer,
contrat complet 196 c distinct. Créneau 30–45 min dépassé ; à revoir avant fusion.
