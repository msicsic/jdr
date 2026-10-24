# Lot 42 — Fouille et faits narratifs

Branche `codex-fouille-faits`, **non fusionnée**, base d'intégration `de74ec1`,
brief `6d26d5e`, correctif `5502858`, signature SSH vérifiée. 24 octobre 2026.
Aucun changement de `main`, des scénarios,
du modèle `gpt-6-luna` ni des quatre fichiers réservés au lot 41.

## Cause et invariant

Les fils complets des deux parties d'intégration montrent deux étapes distinctes :
Luna propose d'abord des empreintes, puis corrige les refus de représentation ou d'impact
sur la quête en décrivant le support. La revue accepte alors « sol » ou « surface du sol »
comme aspect. **Elle ne reçoit pas la demande du joueur** : elle ne peut donc pas juger
que cette description remplace une recherche. Son contrôle des indices est aussi centré
sur l'objectif de scénario. Le rendu juxtapose mécaniquement le nom et son support.

La demande, le sol de pierre visible, éclairé et à portée n'autorisent aucune empreinte.
La comparaison des entrées archivées retrouve des conversations et ambiances différentes ;
`consignes.py` ne change pas entre `3b6415b` et `8443458`. Les fils établissent la dérive
de correction et le défaut du contrat ; ils **n'isolent pas la cause probabiliste du premier
choix** de Luna. Aucune causalité propre à une modification du contexte n'est démontrée.

`mj._appeler` transmet désormais demande et transaction entière à la revue de portée.
`portee_narrative.SCHEMA_FAITS` et `controler_usages` exigent un jugement par ajout,
y compris sans prose : perception remplacée et indice créé sont deux causes de refus
distinctes. Chaque `attendu` cite l'ajout, son ancrage et les opérations de
`moteur.PERCEPTIONS`. Un rapport incomplet bloque la transaction ; une qualification
déjà refusée ne paie pas une revue physique supplémentaire. Aucun ajout refusé n'est
sauvegardé ou affiché. La règle commune est dite dans les consignes et dans le retour
d'audit narratif, qui orientait auparavant toute invention vers `etablir_faits`.
`faits_locaux.preparer_faits` conserve le nom ciblable et l'ancrage d'un détail, mais ne
leur accole plus « sur » ; les objets physiques gardent leur relation explicite.

## Vérifications

- Cinq tests nouveaux : console/MJ simulé/recharge, recherche du sol au Relais et fouille
  d'un coin de l'atelier, avec et sans `suite`, résultat et objets identiques à une perception
  directe ; indice sans lien avec une quête ; qualification sans prose ; détails légitimes
  persistants sous trois noms ; rapport exhaustif et refus séparés. Les doubles historiques
  renseignent le jugement supplémentaire sans supprimer leurs vérifications existantes.
- Suite complète unique (`tools/tests.py --processus 3`), priorité réduite : **1 714 tests,
  16 ignorés, 1 313,6 s**. Deux erreurs du même ancien double de parole, qui ne fournissait
  pas le nouveau jugement ; double adapté, **ses 19 tests rejoués seuls, verts en 54,9 s**.
  Les **162 fichiers sont validés après correction**, sans autre rejeu de la suite complète.
- Luna, une passe ChatGPT, copies, quatre scripts par `banc_multi`. Référence `main`
  `42bb9c0` lue du cache, clés vérifiées avec son `banc_parties.py` historique, aucun rejeu.

| Script | Appels/tour MJ, main → lot 42 |
|---|---:|
| relais | 3,00 → 2,63 |
| crypte | 2,67 → 2,56 |
| atelier | 3,91 → 3,09 |
| luna-restes-ambiance | 4,00 → 2,67 |

Ensemble : **106 → 86 appels**, **3,31 → 2,77 appels/tour** (32 → 31 tours MJ),
13,4 → 11,8 s/tour, replis 1 → 0 ; aucune erreur technique ou de recharge.
Relais n° 5 : `examiner antichambre_sol` du premier coup, **deux appels, 6,39 s** ;
texte affiché et enregistré : **« Le sol en pierre. »** Aucun fait narratif ajouté.

## Limites et traces

Le moteur rend les informations existantes du support : il ne dispose pas ici d'une
mécanique dédiée aux empreintes et ne conclut pas « aucune trace ». Le classement de
l'usage et de l'indice reste sémantique ; ce lot ne garantit donc pas toute détection.
La passe réelle choisit directement la perception ; les refus du nouvel usage sont
exercés par les chaînes simulées. Une passe, plusieurs lots entre versions et des temps
de cache ne prouvent aucun gain causal de vitesse.

Bruts dans le worktree : `artifacts/cause-42.json`, `reference-42.json`, `mesures-42.json`,
`cibles-42*.json`, `suite-42.*`, `correction-double-parole-42.*`, `verification-42.json`
et `bancs-multi/20261024-182640-17164/` (passe explicitement `--connexion chatgpt`).
