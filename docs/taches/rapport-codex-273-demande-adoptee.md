# Lot 273 — demande adoptée et moyen démenti

29 octobre 2026. **`codex-demande-adoptee`, non fusionnée**, base `c9459ce`,
moteur initial `3ec23bb`, banc antérieur sur `527b505` ; correction des
fournitures et du sommeil ajoutée dans le même lot.

**Verdict avant fusion : correction livrée, mesures de confirmation en cours.**
Une demande typée survit au démenti d'un moyen. Sa continuation suit les
provenances publiées des fournitures ; sans plan admissible, elle dort et
libère son palier. Le banc antérieur ne certifie pas cette nouvelle version.

**Contrat commun corrigé.** `poursuites.py` conserve les liens source→résultat
des reçus/remises (`lot`, `objet`), transitivement et hors mémoire bornée ;
`esprits.py` les enregistre avant éviction et migre les reçus encore présents
dans les anciennes sauvegardes. `deliberation._reprendre_demande` replanifie
le service/la fourniture avec le moyen concret tout en gardant la condition
adoptée, son but et son palier. `_fin_demande` évalue les mêmes liaisons.
Une condition exigeant l'identité d'un objet (localisation, garde, restitution,
état) ne reçoit aucune substitution. L'égalité des raisons ne vaut jamais
égalité des demandes. Aucun cas par PNJ, objet, scénario ou prompt ; ni
`agendas.py`, ni `echanges.py`, ni `signes.py` modifiés.

**Sommeil sans délai.** Un résultat de planification `None` conserve la demande
dans `demandes_suspendues`, avec son but, début et urgence, et libère l'arbitrage.
Un plan vide admissible (livraison, délégation, garde) reste actif. Le réveil
replanifie seulement après changement des croyances/moyens ; le passage du
temps seul ne le provoque pas. Une fin attestée retire la demande. La lecture
seule du rapport `origin/ds-demande-adoptee` confirme sa limite déclarée,
mais sa généralisation par « même raison » n'est pas reprise. L'immobilisation
est reproduite sur Anselme au poêle (capture 120) ; les simples plans vides
de garde de Bram ou de vente ne prouvent pas un épuisement. L'attribution
individuelle des dérives ouvertes de Gorm reste à vérifier avec le nouveau banc.

**Contrôles ciblés : 16 tests verts** (137,136 s pour 15 succès et une prémisse
à actualiser ; Aubin corrigé puis rejoué seul : 1,906 s, vert). Capture mine
1985 **373** : Josse sert `biscuits_1` à Odon, même demande, début et palier,
phase `continuer`. Autre PNJ : chaîne de deux détachements reçus, mémoire vidée,
recharge puis repas effectif ; mission d'objet précis non substituée. Capture
**Aubin 117503** : la part déjà reçue est servie immédiatement, faim réelle
**70,209→20,329** ; la prémisse d'une attente jusqu'au retour perceptif est donc
remplacée par le service effectif, sans renaissance. Anselme libère son palier,
ne réessaie pas après 60 min de seule horloge, puis reprend la même demande
avec bois et flamme réellement disponibles et rallume le poêle. Égalités du
monde, rendu et scène après recharge, laps entier/découpé, contrôlées.

**Calcul détaché de confirmation**, priorité réduite : les 47 autres fichiers (49 au total) qui
exercent `choisir`/`_reprendre_demande` et les schémas d'esprit, puis **vingt nuits
de branche seules**, cinq scénarios × quatre graines × 4 h, un processus.
La référence `0e3e626` provient exclusivement des vingt nuits archivées dans
`banc.json`, avec empreinte SHA-256 ; aucun rejeu de référence. Le banc se lance
même si les tests complémentaires échouent. Critères encore **non certifiés** :
aucune hausse de suspects **par nuit**, mine S/F/D dans l'étendue de référence
(toute perte résiduelle exige une justification). Sonde actuelle 265/271,
compteur 219, fonction `cats` du lot 183 identique. Fin attendue :
`C:/Users/msics/donjon/artifacts/demande-273-sol/correction/fin.json`.

**Mesures antérieures (avant cette correction).** Vingt paires de nuits 4 h,
référence `0e3e626`, sonde 265/271 : aucune hausse de suspects par nuit,
**1→0**, suspect Aubin Relais 2024 `117518` absent. Mais mine S/F/D
**25,75/5/1,964→15,25/5/1,464** ; S par graine 1985/7/42/2024 :
**32→12 / 19→18 / 24→13 / 28→18**, soit 64 pertes et 22 gains.
Le défaut lot→part prouvé à 373 interdit d'excuser ce recul comme légitime.
Les familles/auteurs, premières divergences, contre-épreuve de service
(faim Odon 85,077→35,077) et alertes crue/hameau restent dans le
[diagnostic détaillé](diagnostic-codex-273-richesse-alertes.md).

**Limites.** Le changement des entrées réveille une replanification, pas une
promesse de réussite. Une ancienne sauvegarde dont le reçu a déjà été évincé
ne permet pas de reconstruire sa provenance manquante. La causalité de
chaque signature perdue et de chaque dérive ouverte n'est pas certifiée.
`fin-banc.json` (`ok=true`) reste le résultat antérieur. Bruts dans
`C:/Users/msics/donjon/artifacts/demande-273-sol/`, nouvelle passe dans
`correction/`. **Ni Luna ni suite complète.**
