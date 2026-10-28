# Lot 247 — quatre oracles après les fusions d'intégration

Branche `codex-suite-bf4cede`, **non fusionnée**, corrections sur `f46a0b5`.
Les quatre échecs de `bf4cede` sont reproduits sur cette base. Aucun code
moteur, scénario ou MJ modifié. Bissection des révisions de premier parent
entre `4306c14` et `bf4cede`, dans `.worktrees/bissection-247`, avec les tests
historiques de chaque révision ; une absence de test n'est pas comptée verte.
Chaque frontière retenue est confirmée par le test vert sur le parent direct
et rouge sur la fusion. Bruts : `C:/Users/msics/donjon/artifacts/suite-247/`.

| Échec | Fusion qui l'introduit | Cause et verdict |
|---|---|---|
| Promesse annoncée du hameau | `bf4cede` (234), parent `d606305` vert | Le placement commun de `pnj._jugement_placement` / `_pas_placement`, utilisé aussi par `signes.place` et le rapprochement, change la perception au constat. Ilse reste connue à l'antichambre. L'attente `None` est périmée : la trace doit conserver `antichambre`. |
| Prestataire mobile, bloc/découpe | `bf4cede` (234), parent `d606305` vert | Même changement de connaissance, pas une clôture fautive de `biens.services_proteges`. L'espion sur `retenir_service` compare chaque nouvelle trace au lieu cru **à sa création** ; l'ancrage exact est rétabli, toutes les protections et assertions de persistance conservées. |
| Capture des étapes, auberge | `b744265` (244), parent `4422f13` vert | `Vue.recharge_utile` écarte le combustible sans gain de capacité pour une flamme faible encore allumée. Exploration **20 632 → 8 573 visites**. Seuls le hash des visites, leur nombre et les diagnostics changent ; plans (78), monde complet projeté, lignes et deux vues gardent leurs empreintes. Oracle d'exploration périmé. Mine inchangée. |
| Descente / chauffage dans la crue | `d606305` (242), parent `1c4261f` vert | L'échéance calculée par `confier → duree_devis` change les déplacements de l'agenda de Gorm. Il ne transmet plus à Ilse la mesure de la crypte à 91 min. L'ancienne scène lui donnait implicitement une connaissance devenue absente ; prémisse périmée, pas un contournement du contrat d'eau. |

**Preuve particulière pour l'eau.** Avant 242, la croyance reçue de Gorm
porte 41 cm à 91 min, vitesse 60 cm/h ; à 100 min, estimation `[100,-50,60]`,
plan vers le poêle sec. Après, Ilse conserve seulement les 11 cm confiés par
Aubin à 61 min, sans vitesse ; sa propre observation du beffroi ne remonte
qu'à 91 min, trop récente pour mesurer une pente. `estimation=None`, échoppe
crue sèche : plan vers le brasero. Les mondes et deux vues ont été comparés
après sauvegarde/rechargement sur les deux révisions. Deux contre-épreuves
sur 242, ancien `confier` seul ou `duree_devis=None` seul, restaurent exactement
l'estimation et le plan antérieurs ; neutraliser la clôture seule ne le fait pas.

La scène corrigée déclare explicitement la mesure connue, comme connaissance
d'auteur (`croire`, source `savoir`), puis recharge. Elle conserve le refus de
la ronde noyée et du brasero, le recours positif au poêle et le coût de l'eau ;
elle contrôle aussi les ensembles menacés/noyés, cinq minutes d'exécution,
la position, l'absence de chauffage dangereux annoncé et l'identité du monde,
du rendu et de la scène après recharge. Le cas réel crue 500 reste contrôlé
dans le même fichier. Les tests de services conservent annonce, paiement,
réussite, torche allumée/protégée, bloc/découpe et deux vues rechargées ;
l'autre service de l'auberge (Joss/Odile, lanterne portée) reste couvert.

**Validation.** Quatre tests initiaux rouges, puis **4/4 verts, 32,449 s**.
Quatre fichiers entiers : **39/39 verts, 118,060 s**, zéro erreur ni ignoré.
Après ajout du contrôle d'exécution/recharge de l'eau : **7/7 verts, 67,695 s**.
Un travailleur réduit pour ces fichiers, au plus deux calculs du lot simultanés.
Aucun banc d'empreintes requis : seul le code des tests change. Aucune suite
complète, aucun Luna. Limite : ce lot rétablit des oracles justifiés ; il ne
prouve ni une suite complète verte ni une nouvelle garantie générale du moteur.
