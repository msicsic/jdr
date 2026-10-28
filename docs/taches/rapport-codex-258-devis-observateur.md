# Lot 258 — devis d'un acteur vu par un observateur

Branche `codex-devis-observateur`, **non fusionnée**, base et brief
`e9a8dfe`, 28 octobre 2026. Aucun choix autonome raccordé ; devis réel du
256, scénarios, MJ, `social`, `esprits`, `echanges` et `deliberation` intacts.

`agendas.devis_observateur` prépare un prochain sous-but sur le modèle fermé
`planification.ContexteDevis`. Observateur et acteur sont explicites ; aucun
esprit du tiers n'est lu. Le départ et les possessions, y compris dans les
contenants, viennent des croyances de l'observateur. Les couples
`(sujet, attribut)` partagés ou à transmettre sont déclarés par l'appelant et
doivent être connus de l'observateur ; ses autres souvenirs ne deviennent pas
ceux du tiers. Relations et refus restent ceux de l'observateur, dans ce seul
contexte. Départ inconnu : devis impossible. Profil inconnu : caractéristiques
**10**, valeurs **50** (`caractere.BASE/NEUTRE`), besoins calmes, aucune charge
ou compétence spécialisée présumée, bourse ordinaire (`biens.BOURSE`).
Carte et catalogue structurel restent les a priori communs du planificateur ;
les champs `CHANGEANTS` sont remplacés par les croyances. Aucune installation
de Monde ne réinjecte des connaissances lors de cette projection temporaire.

`Vue` porte le contexte ; départ et coûts utilisent le monde projeté. Toutes
ses données entrent dans `_entrees`, en plus du relevé commun ; mémoires,
graphes et preuves d'impossibilité ont une place distincte par observateur et
acteur. Les clés des recherches réelles restent inchangées.
`relations.autorite_estimee` lit le statut propre cru dans sa portée :
ascendant reconnu et dette réciproque inconnus valent **zéro**. Le lien dirigé
de l'observateur vers le tiers n'est pas retourné pour inventer sa réciproque.
Ce lecteur reste distinct du jugement réel `autorite_mandat`.

**Épreuves** : huit nouveaux tests, Gorm → Aubin → Brune et information à
Ilse. Position réelle hors perception, savoir privé retiré, possession non
vue, liens, capacités, valeurs et faim privés modifiés : **projection entière
et devis identiques**. Départ cru changé et clé crue en main pour franchir la
porte : **devis modifiés pour les deux charges**. Refus retenu, transmission
explicite, impossibilité sans savoir et séparation des caches couverts.
Chaque variante des charges est sauvegardée/rechargée : monde complet,
rendu joueur, scène perçue et devis conservés ; pureté du monde contrôlée.
Les devis réels du 256 restent identiques et réagissent encore à la perte du
savoir du titulaire. Dans le cas d'information original du 257, Gorm ignore
le contenu privé d'Aubin : estimation impossible jusqu'à apprentissage
explicite par Gorm, sans consulter Aubin.

**Tests ciblés** : onze fichiers concernés, **75 tests distincts verts**
(dernière version de chaque fichier ; les passages intermédiaires incluaient
sept tests importés, ensuite exclus de la découverte). Huit fichiers en
77,361 s puis quatre fichiers en 7,036 s ; vérifications finales de projection
et d'autorité consignées séparément. Au plus deux processus, priorité réduite.
Ni suite complète ni Luna. `git diff --check` propre.

**Empreintes validées : 20/20 paires 2 h identiques**, cinq scénarios
(Relais, mine, auberge, crue, hameau) × quatre graines 1985/7/42/2024.
Référence **e9a8dfe**, l'`origin/integration` du départ, branche **9149386** :
chroniques, mesures, empreintes et hash de l'état final complet identiques
nuit par nuit ; divergence nulle, zéro plantage. Avis non justifiés **1 → 1**
(crue 7), entrées à expliquer **41 → 41**, aucun accroissement. Vingt
références exactes absentes calculées et rangées une fois, aucune rejouée ;
vingt nuits de branche également rangées. Calcul détaché terminé en
**226,699 s**, deux processus réduits au plus, `fin.json` code **0**.
Aucun calcul actif. Bruts :
`C:/Users/msics/donjon/artifacts/observateur-258/` (`empreintes.json`,
`fin.json`, journaux et résultats des tests ciblés).

**Limites** : coût du prochain sous-but, aucune garantie de réussite complète
ni d'adhésion réelle ; neutralité vérifiée sur les vingt paires ci-dessus.
L'appelant doit expliciter ce qu'il sait partagé ou prévoit de transmettre ;
aucune inférence automatique d'un savoir partagé. Le catalogue structurel et
la carte suivent le contrat actuel du planificateur : cette projection
n'ajoute pas de mémoire historique des propriétés structurelles cachées ou
transformées. L'invariance démontrée porte sur les états privés, départs et
possessions visés ici ; ce dernier point limite une garantie épistémique
plus générale. Aucun choix faire/confier livré.
