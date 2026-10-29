# Lot 309 — récit des buts d'agenda

Branche **codex-recit-buts-agenda**, base intégration **02c7330**,
29 octobre 2026. **Lot terminé ; un échec préexistant qualifié.**

**Invariant.** Un but d'agenda est une référence locale au titulaire,
pas une description complète du projet. `recit_pnj.but_en_mots` reçoit
désormais ce titulaire et lit sorte et paramètres avec `agendas.projets`,
puis les liens avec `agendas.filiation`. Le même rendu générique sert
aux six sortes, aux mandats et aux sous-mandats : aucune branche par
sorte, personnage ou scénario ; aucun champ ajouté aux buts. Une
référence non résolue reste affichée en JSON, sans deviner une charge.
Les contenus structurés de parole restent des données citées.

`Recit.personnage` et `Recit.donnees` transmettent le titulaire, comme
`audit_nuits._releve`. L'audit charge le rendu de l'observateur courant
pour rester utilisable avec une référence dont l'ancienne API ne recevait
pas le titulaire. Deux autres appelants du rendu commun, le rejeu
(`Enregistreur._penser`) et les intentions enregistrées
(`paroles.engagements_enregistres`), transmettent seulement cet identifiant.
Aucun moteur de décision, scénario, prompt, audit du MJ ou modèle modifié.

**Preuve réelle acquise.** Capture intégrale du lot 306, hameau 42,
minute 5, conservée compressée dans `tests/data/`. Le code de `02c7330`
reproduit `KeyError: 'qui'` sur le but sans cible d'Aubin. Le correctif
rend ce mandat et le sous-mandat d'Ilse, avec leur chaîne
Gorm/evacuer_crue → Aubin/a1 → Ilse/a1. Monde, rendu joueur, scène,
relevé et récit sont identiques après sauvegarde/rechargement ; le rendu
ne modifie pas le monde. Bruts `capture-*` archivés.

**70 tests / neuf fichiers, 69 verts, un échec, aucune erreur ni saut**,
203,511 s, deux travailleurs réduits. Contrôle AST du socle vert.
Les trois nouveaux tests sont verts : six scènes (amener,
informer, garder, protéger, obtenir par dette et récupérer par spoliation),
chacune rendue avec quatre formes de sous-but ; capture réelle et
sous-mandat ; identifiants `a1` locaux distingués et référence absente.
État/rendu/scène après recharge, récit texte et données, relevé, rejeu et
intentions enregistrées contrôlés. Les premières assertions de noms et
de prix des nouvelles scènes ont été corrigées d'après leurs données ;
aucun oracle existant modifié.

**Échec préexistant reproduit sur `02c7330`.**
`test_des_nuits_en_parallele_comme_une_a_une` compare deux textes complets.
Seule diffère la ligne « Mesures » : l'union des clés dans
`banc_pnj.executer` insère les compteurs de mandat dans un ordre dépendant
du hachage du processus. Valeurs égales, autres lignes identiques.
`banc_pnj.py` et ce test sont inchangés depuis la base. Diagnostic isolé
sur la base, 18,423 s, priorité réduite ; worktree temporaire supprimé.
Aucun oracle affaibli, aucune correction de banc ajoutée à ce lot.
Traces : `test-base.log`, `diagnostic-base.json`, `fin-diagnostic.json`.

**Empreintes : huit paires 2 h identiques**, Relais/crue ×
1985/7/42/2024, `02c7330` → `4eb05f8` : chronique, mesures et état final
complet identiques nuit par nuit, zéro plantage. Huit références absentes
calculées une fois et rangées, puis huit nuits de branche ; 154,450 s,
deux travailleurs réduits. Avis à expliquer inchangés : Relais 1985/42
1/1, crue 1985/42 1/2, zéro pour les autres graines ; aucun avis non
justifié. Calcul groupé terminé en 358,962 s. Ni Luna ni suite complète.
**`fin.json` brut conservé, `ok=false`** à cause du test ci-dessus ;
clôture qualifiée dans `fin-cloture.json`. Code/tests inchangés depuis
la vérification, seule la documentation est close ensuite. Branche
poussée vers origin ; aucun calcul actif ou relancé à la clôture.

**Limites.** Le texte des agendas change également lorsqu'il attribuait
auparavant une mauvaise sorte, par exemple « informer » pour « amener ».
Les paramètres structurés sont rendus en JSON, sans paraphrase. Un appel
extérieur sans titulaire garde le but brut. Le correctif ne traite pas
les répétitions comportementales signalées par le lot 306 et ne valide
pas son banc du hameau. La suite ciblée garde l'échec d'ordre des mesures
préexistant ; elle n'est pas déclarée entièrement verte.
Bruts : `C:/Users/msics/donjon/artifacts/recit-309/`.
