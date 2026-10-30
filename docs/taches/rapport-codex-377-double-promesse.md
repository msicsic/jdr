# Lot 377 — Une même part n'est pas promise deux fois

30 octobre 2026, PC fixe. Branche `codex-double-promesse`, base
`origin/integration 2887c541` (les références locales `integration` et `main`
sont anciennes). Pas de fusion dans ce lot.

**Invariant.** Les engagements actifs du promettant diminuent les moyens d'une
nouvelle offre, qu'elle passe par une demande, une proposition, une livraison
de part, un service gratuit ou payé, ou un devis daté. Une remise réserve le
bien entier ; un service réserve les parts que consomme son plan cru. Les
outils réutilisables employés par ce plan ne sont pas consommés. La parole en
cours de revalidation est comptée une seule fois ; dater une livraison
provisoire remplace cette proposition dans la copie de calcul.

**Code.** `agendas.moyens_promis`, `disponibilite_promise` et
`monde_devis_libre` calculent ces charges depuis les engagements existants,
sans nouveau registre d'esprit. La projection retire les moyens indisponibles
du devis, laissant le planificateur chercher parmi les autres moyens crus.
`echanges` applique cette disponibilité avant les transferts et dans ses devis,
en conservant les contrôles historiques propres à chaque voie. Aucun prompt,
scénario, rendu ou format de sauvegarde n'est changé.

**Cas réel et autres cas.** La capture du lot 371, auberge 7 à 187 min et
180 dixièmes, est conservée dans `tests/captures/double-promesse-377.json.gz`.
Mireille garde sa livraison de `marmite_2` à Tilo et refuse le service vendu à
Mathurine, sans paiement ni remboursement. Tilo reçoit son bien après recharge,
en bloc et en laps découpés. Même contrôle pour une cloche promise par Aubin
à Brune, avec refus déterministe rendu au joueur. Les réserves de 2 ou 4 parts
restent vendables après une promesse de service ; une part unique est protégée.
Les tests couvrent également le combustible d'un service sans métadonnée de
part, la répétition sans second paiement, la libération après abandon et un
stock distant caché. État et rendu sont comparés après sauvegarde/recharge.

**Mesures finales.** **98 tests distincts verts** : passe de 97 tests sur onze
fichiers (`tests-final.json`, 234,1 s), puis complément de 26 tests comprenant
les sept nouvelles régressions (`tests-complement.json`, 22,7 s). Assertions
des tests voisins inchangées. Le devis daté remplace sa proposition provisoire
après détection du double comptage ; les voies historiques gardent leurs contrôles.
**Empreintes 2 h, auberge et Relais, 1985/7/42/2024**, contre `2887c541` :
**4/8 identiques**, huit nuits sans plantage, zéro usurpation et zéro aller-retour
non justifié selon la sonde courte. Les références manquantes ont été jouées une
fois et mises en cache. Deux travailleurs au plus, priorité réduite ; ni suite
complète ni Luna, aucune conclusion de performance.

**Divergences attribuées.** Auberge 1985, minute 95 : le refus du troc
`vivres_1` passe de `garde` à `impossible`, car Odile a déjà promis cette part
à Mathurine. Relais 7/42/2024, minute 4 : la nouvelle livraison à Aubin est
refusée ; Gorm est à l'échoppe, ses vivres au refuge, et leur seule disponibilité
crue ne prouve pas une seconde part libre après celle payée par Brune. La
promesse à Brune reste tenue. Cet écart expose la borne conservatrice ci-dessous,
pas une identité générale des nuits. Le code 1 du comparateur et `succes:false`
de `fin-lot.json` signalent ces différences d'empreintes, sans échec de test.
Captures d'attribution et synthèse : `analyse-*.json.gz` et `conclusion-lot.json`,
dans `C:/Users/msics/donjon/artifacts/double-promesse-377/`.

**Limites et recouvrements.** Aucun nombre de parts distant n'est inventé :
hors des biens propres à portée, la croyance « disponible » ne garantit
qu'une part. Cette borne conservatrice peut fermer une offre matériellement
possible qui demanderait de recompter une réserve distante : l'absence de
tout faux refus n'est donc pas garantie. Les parts libres d'un stock propre
comptable à portée restent vendables, comme vérifié en test. Ce lot ne promet pas une planification
temporelle globale de tous les engagements, ni leur exécution malgré une
nouvelle urgence ou une croyance fausse. Recouvrement avec **365** autour des
échanges/catalogue ; `agendas.py` peut aussi recouper des corrections PNJ de
**375**. Ni `esprits.py`, ni `planification.py`, ni nouveau registre pour S1.
Livraison terminée et branche poussée ; fusion laissée au superviseur.
