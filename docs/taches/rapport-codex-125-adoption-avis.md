# Lot 125 — Pourquoi les avis ne sont pas adoptés

Branche `codex-adoption-avis`, diagnostic, non fusionnée ; base **85b9204**.
Aucun code du jeu ni scénario modifié, aucun Luna. Python du dépôt principal,
un processus de nuits à priorité réduite ; brièvement un second pour les captures.

**Conclusion.** Dans les nuits étudiées, l'avis n'apporte pas de menace nouvelle :
l'auditeur tient déjà la même conclusion et dispose d'une estimation propre `vu`,
conviction **1**, poids **1**. La réception renvoie réellement **`doute`**, même
quand le contenu est redondant ; cela ne veut pas dire que l'auditeur doute de la
menace. Le moteur décline la substitution de sa prévision par celle d'autrui.
La classe principale est donc **même avis déjà tenu**, avec en plus un poids reçu
inférieur ; aucune preuve d'un défaut de calcul ni d'une conviction écrasée.

| Crue, départ tiré, joueur `chambre_cloche` (galerie) | Avis dits | Réceptions, témoins compris | Adoptions / disputes |
| --- | ---: | ---: | ---: |
| 4 h, 1985 | 7 | 10 | 0 / 0 |
| 4 h, 7 | 2 | 2 | 0 / 0 |
| 4 h, 42 | 5 | 7 | 0 / 0 |
| 4 h, 2024 | 4 | 4 | 0 / 0 |
| 12 h, 500 | 17 | 41 | 0 / 0 |
| 12 h, 2024 | 5 | 6 | 0 / 0 |

Les **70 réceptions** sont de la même classe ; les **40 avis dits** ne produisent
aucune adoption. Dans 59 réceptions les coefficients eux-mêmes sont identiques,
dans 11 ils diffèrent sans changer la conclusion de menace. Poids reçus :
**0 ; 0,056 ; 0,154 ; 0,2772 ; 0,5005 ; 0,63 ; 0,6825**, contre **1** acquis.

**Chaîne et poids.** `eau.observer` enregistre niveau visible et pente mesurée,
`estimation` combine les derniers repères, `esprits.prevision_propre` prend la
qualité de la preuve la plus faible. `social._avis` transmet ici une conviction
de **1** ; `poids_source` puis `recevoir_prevision` appliquent exactement
**0,7 × confiance/100 × (1 + affection/200) × conviction**. Le détail nominatif,
lieu ciblé, lieu de parole, date, coefficients, source, conviction, relation,
poids et issue de **chaque réception** est dans `artifacts/adoption-125/nuit-*.json`
et `receptions.csv` (`marchand` désigne Gorm). Les dates de preuve propres et dites
sont égales : aucun rejet n'exige la priorité d'un constat **plus récent**.
Aucun cas « poids inférieur malgré l'absence de constat », ni autre classe.

**Disputes.** `social._contradiction` est observé avant la réception des témoins :
aucun auditeur ayant saisi les mots ne tient la menace contraire. Le premier
critère manque, avant la comparaison de conviction, le registre de répétition
ou l'audibilité d'une réponse. Ce relevé ne prouve pas que tous les PNJ éloignés
étaient d'accord : il porte sur les auditeurs effectifs, destinataires compris.

**Vérification.** Chaque nuit est rejouée sans sonde : état complet final,
chronique, empreintes intermédiaires du banc et mesures identiques. L'outil
`tools/diagnostic_adoption_avis.py` ne modifie pas le monde observé (assertions
avant appel réel). Le cache global `_IMPOSSIBLES` est vidé entre nuits, comme
les autres caches du banc : sans cela, 42 gardait les mêmes états mais comptait
599 puis 597 recherches neuves. Deux captures de réception nouvelles sont sauvées
et rechargées deux fois : même décision, prévision et rendu rechargés.
Les **3 tests historiques `test_avis_reels` passent** via `--captures` : Aubin →
Gorm à 72 min (500), Aubin → Ilse à 102 min (2024), parole entière, même monde
et perception après recharge et temps découpé. Le joueur distant entend une voix,
sans les mots. Seul l'emplacement temporaire de sauvegarde est adapté aux ACL
du bac Windows. Pas de suite complète, conformément au brief.

**Portée et suite proposée.** Le résultat est compatible avec le contrat du § 7.3,
sans justifier une correction du moteur. Pour rendre un avis utile, le scénario
peut créer une asymétrie de preuves : un observateur suit l'eau pendant qu'un
autre, concerné et joignable, reste hors de vue de l'eau et n'a pas encore de
pente propre ; leur confiance permet alors l'adoption. Une dispute naturelle
demande deux prévisions contraires étayées et une occasion de parole commune.
Ces conditions relèvent des lieux, accès, positions et relations initiales,
sans exception pour un PNJ ni nouvelle consigne au MJ. L'utilité tactique d'un
avertissement plus précoce pendant un plan actif n'est pas démontrée ici.
Les chiffres historiques 16/6 du lot 88 ne sont pas postulés pour cette base :
le moteur a évolué (ici **17/5** à 12 h) ; les 18 avis de 4 h sont retrouvés.
Bruts locaux non versionnés. Aucune clé de signature Git configurée sur ce poste :
commit non signé ; branche livrée sans fusion ni modification de `main`/`integration`.
