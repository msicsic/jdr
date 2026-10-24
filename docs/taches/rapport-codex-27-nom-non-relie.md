# Lot 27 — Noms sans lien nominal

24 octobre 2026. Branche `codex-nom-non-relie`, **non fusionnée**, base `ea4d562`
(issue du lot 26, `64351b2`). Correctif signé **736c043**.

**Invariant et fonctions.** Un nom ne permet pas au MJ de choisir lequel des corps
inconnus le porte. `noms.personnage` reprend la résolution commune de la parole,
corps reliés et appellations de voix compris. `verifier_nom` exige une référence
perçue ; `verifier_saisie` contrôle le lexique de l'état avant la syntaxe locale,
la conversation et le MJ, sans liste de gestes. Le refus local porte un `attendu`,
une cause, sans attribution privée ni apprentissage. `jeu.main`, `commandes.analyser`
et `MJ.echanger` appliquent cette frontière, questions et MJ forcé compris.
Paroles, citations, désignations publiques et noms hélés gardent leur contrat.
Les diagnostics existants passent avant la saisie de jeu.
Contexte et règles de Luna distinguent déjà noms reliés et appellations : aucun
prompt ajouté, aucun fichier réservé ni donnée de scénario touché.

**Preuves après recharge.** Neuf tests nouveaux, verts en 15,4 s : cas réel
« je pousse Aubin » du banc `echanges`, don de la cloche à Brune, autres gestes,
question, MJ forcé et absent connu. **Zéro appel** dans les refus, en ligne et hors
ligne ; état complet et rendu inchangés après recharge. Geste permis avec lien,
mots cités et voix impostrice vérifiés aussi.

Une suite complète (`tools/tests.py --processus 3`), puis seules reprises ciblées :
**1 607 tests validés, 15 ignorés**, bilan consolidé sur 147 fichiers. Première
passe : attentes anciennes adaptées au refus précoce et à la perception ; diagnostic
remonté ; HTTP local interdit et deux workers TUI bloqués dans le bac à sable.
Workers arrêtés, reprises hors bac à sable à priorité réduite :
82 tests verts en 63,8 s, puis 33 TUI verts en 161,2 s. Aucun second lancement complet.
Traces brutes et rapprochement : `artifacts/tests-*.json`, `verification-finale.json`.

**Luna, une passe.** `gpt-6-luna`, ChatGPT, effort `medium`, copies temporaires,
`SEUIL_AUTH` vers le coffre principal ; suite à priorité réduite en fond.

| Script | Appels | Appels/tour MJ | Secondes/tour MJ | Replis |
|---|---:|---:|---:|---:|
| echanges | 10 | 3,33 | 15,90 | 0 |
| noms-dialogue | 12 | 3,00 | 12,90 | 0 |

« je pousse Aubin » : **0 appel**, « Tu ne sais pas lequel d'entre eux est Aubin. »,
aucun temps, jet ni déplacement ; don à Ilse non reliée également refusé localement.
Fil du lot 26 (`6fbdda2`) réutilisé : 10 appels et 34,72 s pour pousser, sans relancer
la référence. La salutation ne nomme personne sans lien. Noms appris : Brune s'écarte,
position rechargée `[0, 2]`, Ilse répond. Aucun arrêt ni recharge invalide. Les trois
« mentions sans fondement » comptées sont les noms cités dans les refus locaux.
Fils et mesures : `artifacts/nom-non-relie/`.

**Limites.** Un nom absent du lexique n'est pas reconnu comme nom propre ; les
formulations mixtes classées comme parole restent sémantiques. Une condition sur
un absent nommé reçoit aussi le refus local. Le garde narratif reste celui du
lot 26 : une passe ne prouve ni toute absence de faux refus ni un gain global de
latence. Le critère d'ambiance et le sifflement joyeux restent ouverts.
