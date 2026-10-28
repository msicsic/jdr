# Lot 259 — présence au service d'une part promise

**`codex-presences-regression`, non fusionnée**, base `integration 7e69227`.
Ni Luna, suite complète, scénario, MJ, `social.py`, `esprits.py`, `agendas.py`
ou `relations.py` modifié ou lancé.

**Invariant et correction.** Une présence se juge au moment du geste dans
le plan ; la venue convenue au lieu des vivres satisfait le devis d'une part
demandée, gratuite ou payée. La présence réelle reste obligatoire pour
consommer la portion. Le lot 251 traitait cette venue comme la présence
d'une cible fixe et refusait ainsi les demandes à distance des vivres.
`pnj._a_reunir` distingue désormais l'admission avec les venues convenues
du contrôle matériel. Il lit le contrat existant de `echanges.demander`
(`objet`, `pour`, condition de service, engagement non annulé), déjà installé
provisoirement avant le devis et retiré en cas de refus. Aucun nouveau champ
de sauvegarde, déplacement, savoir privé du bénéficiaire ou état hypothétique
persisté. Une pulsion spontanée de nourrir autrui ne constitue pas cet accord.
`planification._mesurer_direct` utilise ce contrat dans ses lieux projetés.

La revalidation par `pnj.refus_etape` conserve le contrôle des participants
supplémentaires ; les cibles de contact gardent leur approche et leur
observation ordinaires. Le contrôle ajouté en 251 empêchait aussi de constater
la disparition d'un objet et d'enregistrer la croyance qui répare le plan :
les deux erreurs du journal relevaient de cette admission prématurée.

**Vérification.** Première passe : **74 tests verts**, six fichiers,
56,418 s, deux processus à priorité réduite. Vérification finale en cours :
les **18 fichiers en échec du journal**, sans assertion affaiblie, et six
voisins (`service_repropose`, contrat d'engagement, trajet estimé, part
estimée, parts achetées, engagement et déplacement). Liste exacte et résultats
dans les bruts. La nouvelle contre-épreuve joueur/Ilse vérifie demande,
engagement et plan après recharge, devis sans mutation, refus matériel avant
la venue sans consommation, puis service réel, clôture de l'engagement,
portions, mémoire ou texte joueur, état et rendu après recharge.
Les captures Mireille/Mathurine et Mathe/Lucien du lot 251 restent couvertes.

**Banc rapide demandé.** Lancé détaché après réussite des tests, cinq scénarios ×
quatre graines × 4 h, deux processus réduits au plus ; références `39db079`
et `e875877`, caches réemployés, branche calculée une fois puis réemployée
par son commit. Suspects et S/F/D contre les deux références restent à
rapporter : aucune conclusion de non-régression globale avant ce résultat.
Version figée du moteur : `3c529db`. Le lanceur attend la fin du processus
de tests, sans travailleur de banc simultané ; en cas d'échec des tests,
il écrit la fin en erreur sans lancer le banc.

**Limites.** Une venue convenue est une hypothèse du devis, pas la garantie
de l'immobilité, de l'ouïe ou de l'arrivée future du bénéficiaire. L'exécution
commune vérifie encore la salle et la parole avant tout effet. Aucun nouveau
système général de rendez-vous ni de recherche du bénéficiaire ajouté.
Bruts : `C:/Users/msics/donjon/artifacts/regression-259/` ; fin attendue :
`banc.termine.json`.
