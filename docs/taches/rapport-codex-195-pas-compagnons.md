# Lot 195 — preuve d'accomplissement après 224 et arbitrage des attentes

28 octobre 2026. **346c1aa fusionné par 11f728a** ; extension autorisée à
`echanges.tenu` en plus de `ouie.py`. Aucun autre fichier du moteur modifié,
aucun Luna, deux calculs réduits au maximum. Bruts exclusivement sous
`C:/Users/msics/donjon/artifacts/pas-195/` : `extension-346/`, `arbitrage/`,
historique `reprise-bd45/`, références exactes `references/`.

**Correction.** L'ouïe attribue un bruit ordinaire compatible avec une présence
crue mobile sans confirmer son déplacement ; attribution/méfiance communes,
recalage précis et voix reconnues conservés. Dans **`tenu` seulement**, un
souvenir neutre `suivi_engagement` conserve la croyance pertinente au premier
jugement après la parole (état, lieu ou verrou). Une preuve nouvelle `vu`/`essai`
peut ainsi établir l'ordre dans la même minute après recharge ; sinon, il faut
un constat propre strictement postérieur. Les prises/clôtures/abandons séparent
les promesses identiques. Ancien état, bruit et délai seuls insuffisants ;
aucun constat fabriqué, position, émotion ou retour au choix ajouté.
**Le bloc `retenir_service` du 224 reste intact**, puis `agendas.echoir` clôt.
Contrôle AST : seule `tenu` change dans `echanges.py` par rapport à `346c1aa`.

**Preuves : 41 ciblés verts**, dont quatre nouveaux tests : geste propre après
checkpoint/recharge, geste antérieur et bruit non probants, observation d'un
tiers, deux paroles identiques dans la même minute sans partage de preuve.
Monde/rendu/scène rechargés ; restitution de clé distincte. Tilo allume et solde
sa tâche à minute 0, protection 224 conservée. Son relevé excluait cette minute :
même notification contrôlée dans toute la chronique, plus clôture/protection,
sans réancrer la scène. Prêts, contrat 213, tests 224 et palier passent.

**Banc final 219 : 20 paires de 4 h**, cinq scénarios × graines 1985/7/42/2024,
référence constituée une fois. Après correction de la borne : vingt références
relues, vingt nuits candidates identiques au premier banc (état, chronique,
mesures, épisodes). Zéro plantage/usurpation. Suspects : totaux ; autres : moyennes.

| Scénario | Suspects | Retournements | Bruits inconnus / aller voir | S/F/D (183) |
|---|---:|---:|---|---|
| Relais | 0→0 | 54→27,25 | 20,5/4,25→17,5/4,25 | 11,5/4,25/1,625→14,5/4,5/1,813 |
| Mine | 1→0 | 68,25→18 | 14,5/2,25→16,5/2,5 | 26,25/4,5/1,964→24/4/1,607 |
| Auberge | 2→1 | 48,75→24,75 | 40,5/12→33/10,25 | 10,25/4,5/0,969→8,25/4/0,906 |
| Crue | 2→0 | 50,25→27,25 | 31,75/4,75→27,75/2,5 | 16,5/7,25/2,438→17,75/7,5/2,688 |
| Hameau | 0→0 | 139,25→48 | 64,5/4→36/2,25 | 40,5/8,5/2,667→27/7,5/2,167 |

**Suspects 5→1**, aucune hausse par scénario ; préemptions 67→65, cycles
494→462, autrui 1→1, progrès 0→0. **À expliquer 67→77, dérives 202→210**,
états payés perdus 8→7, observations « figés pressés » 3→4 ; aucune certification.
Vols vus/entendus nuls ; richesse non uniformément améliorée. Résiduel : Mireille,
auberge 7, servir Mathurine, **111690/111725/111910**. Aucun retour Gorm vers
servir Ilse au Relais 2024 ; Brune hameau 2024 : zéro alerte dans les deux variantes.

**Arbitrage des tests.** La suite précédente (2 497 tests, 13 échecs et une
erreur) isolait quatre préexistants et neuf échecs/une erreur du candidat.
Sur autorisation, **huit échecs et l'erreur** sont corrigés par des prémisses
explicites de scène : rencontre localisée, silence, absence de dette concurrente,
corps déjà rassasiés, départ du trajet, travail réellement en attente.
**273 assertions identiques par AST**, huit fichiers / **67 tests ciblés verts**.
Classement de chaque cas et détail des prémisses dans
[l'annexe d'arbitrage](rapport-codex-195-arbitrage.md). Moteur inchangé depuis
`e7aab68` ; banc final ci-dessus réutilisé, aucune référence relancée.

**Suite après arbitrage : 2 497 tests / 289 fichiers, 2 091,515 s, cinq échecs,
zéro erreur, zéro ignoré**, une passe complète après les dernières prémisses,
deux travailleurs réduits. Exactement les quatre préexistants et le défaut
de placement ci-dessous ; aucune autre régression. Bruts `arbitrage/suite.json`.

**Origine des préexistants vérifiée sur sources exactes** : troisième voix
apparue à la fusion **221, d7dbf1a** ; attente historique de perte de torche
à la fusion **224, 346c1aa**, par interaction avec 221 (les deux tests passent
sur la branche 224 seule `0ae525f`). MiMo ×2 déjà rouge sur `bd45f65`.

**Placement hors périmètre.** Une attitude périmée bloque le recours d'abri.
Proposition non appliquée dans `signes.place`, essayée en mémoire : 21 tests
verts, Ilse rejoint Brune, mais l'assertion particulière sur Aubin reste rouge.
Ce n'est pas une correction validée des anciens tests. **Défaut laissé rouge,
lot séparé à créer**, cas/fonctions/contrat proposés dans l'annexe ; aucun patch
de placement appliqué. Les quatre préexistants restent également rouges.

**Richesse du hameau : perte réelle, pas retrait des sons dans le compteur.**
S ne compte ni bruits ni retournements : 162→108 signatures sur quatre nuits,
soit **40,5→27**. Décomposition : demandes −28, offres −10, promesses −10,
travail payé/appels/services −3 chacun, disputes −2, avis +5. Les échanges
acceptés passent **16→9**, tâches faites **4→2**, prêts/rendus **1/1→0/0** ;
des interactions réelles disparaissent avec les perceptions fortuites.
Les occurrences de travail payé montent néanmoins **20→26**. Différences
intégrales et exemples datés dans `arbitrage/richesse-hameau.json` et l'annexe.
Aucune garantie de richesse préservée ; les suspects ne montent nulle part.

**Limites.** Checkpoint oublié ou croyance inchangée dans la même minute : preuve
propre ultérieure nécessaire. Compteur non certifiant ; bornes géométriques et
datation optimistes. Rondes apprises et registre visuel joueur hors lot. Aucune
clé Git de signature configurée.
