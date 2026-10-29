# Lot 309 — récit des buts d'agenda

Branche **codex-recit-buts-agenda**, base intégration **02c7330**,
29 octobre 2026. **Code livré ; vérification groupée en cours.**

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

**Épreuves initiales : 3 tests verts, 10,721 s.** Six scènes (amener,
informer, garder, protéger, obtenir par dette et récupérer par spoliation),
chacune rendue avec quatre formes de sous-but ; capture réelle et
sous-mandat ; identifiants `a1` locaux distingués et référence absente.
État/rendu/scène après recharge, récit texte et données, relevé, rejeu et
intentions enregistrées contrôlés. Les premières assertions de noms et
de prix des nouvelles scènes ont été corrigées d'après leurs données ;
aucun oracle existant modifié.

**Vérification restante, détachée.** Neuf fichiers ciblés, dont le contrôle
AST existant du socle, puis empreintes 2 h Relais/crue × 1985/7/42/2024
contre `02c7330`, avec cache des références. Deux travailleurs maximum,
priorité réduite, référence puis branche. Ni Luna ni suite complète.
Le lanceur écrit **`C:/Users/msics/donjon/artifacts/recit-309/fin.json`**
en dernier ; relire ce bilan avant de déclarer le lot validé.

**Limites.** Le texte des agendas change également lorsqu'il attribuait
auparavant une mauvaise sorte, par exemple « informer » pour « amener ».
Les paramètres structurés sont rendus en JSON, sans paraphrase. Un appel
extérieur sans titulaire garde le but brut. Le correctif ne traite pas
les répétitions comportementales signalées par le lot 306 et ne valide
pas son banc du hameau. Les empreintes et fichiers voisins restent à
qualifier à la reprise. Bruts : `C:/Users/msics/donjon/artifacts/recit-309/`.
