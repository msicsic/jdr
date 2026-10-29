# Lot 295 — suite ciblée après G2, G4 et U-D

2026-10-29. Branche `codex-suite-g2-g4`, base intégration `475d29d`.
**Lot terminé, non fusionné.**

**Invariant.** Une réponse de forme invalide ne décide pas de l'intention du
joueur. `MJ._appeler` repasse par `MJ._repli` et `narration.repli` : les
attestations perceptibles de la cible de la saisie restent disponibles ; à
défaut, l'interprétation demande une précision. Aucune exception d'objet,
de formulation ou de mode proposé. Les refus d'action gardent G2 ; le
résultat exécuté garde G4, sans récit ni audit après exécution.

Attribution par les diffs de fusion : G2 `8f38db9` → `6036d0e`, G4
`9e52df4` → `80738af`. Le rejeu des sept fichiers sur `475d29d` reproduit
**exactement 15 échecs et 9 erreurs**, 70 tests, 48,026 s : aucun défaut
supplémentaire attribuable à U-D. Les comptes ci-dessous incluent les sous-tests.

| Test (fichier, méthode abrégée) | Lot | Classe | Correction |
|---|---|---|---|
| `websocket_jeu`, deux scènes (2 échecs) | G4 | Attente périmée | Deux appels avant action ; rendu moteur exact et reprise. |
| `websocket_jeu`, coupure avant/après sauvegarde (2 échecs) | G4 | Attente périmée | Fragment rejeté avant action ; transport perdu à l'affichage après sauvegarde, sans reconnexion. |
| `websocket_jeu`, reconnexion aux quatre étapes (4 échecs) | G4 | Attente périmée | Reconnexion aux deux étapes restantes ; requête rejouée identique, une exécution. |
| `fournisseurs_jeu`, OpenAI HTTP (2 erreurs) | G4 | Attente périmée | Compilation/revue seules, résultat exact sauvegardé. |
| `fournisseurs_jeu`, Anthropic (2 erreurs) | G4 | Attente périmée | Même garantie. |
| `fournisseurs_jeu`, MiMo (2 erreurs) | G4 | Attente périmée | Même garantie. |
| `fournisseurs_jeu`, MiMo avec correction (2 erreurs) | G4 | Attente périmée | Correction et traces SSE conservées ; un appel de format supplémentaire. |
| `restes_fusions`, MiMo après reprise (1 erreur) | G4 | Attente périmée | Parcours partagé corrigé ; rejets archivés inchangés. |
| `cache_kv_local`, deux scènes (2 échecs) | G4 | Attente périmée | Deux requêtes, slots 0/3 ; cache et reprise contrôlés. |
| `luna_noms`, approche structurée (2 échecs) | G4 | Attente périmée | Rendu moteur témoin exact ; approche conservée, brouillon absent, recharge. |
| `parole_corrections`, refus de forme (1 échec) | G2 | Attente périmée | Explication finale retirée ; précision moteur exacte après trois propositions invalides, sans audit ni effet. |
| `sans_message_technique`, description mal formée (2 échecs) | G2 | Régression | Repli perceptible rétabli dans le contrat commun. |

**Validation finale : 147 tests / 12 fichiers, tous verts**, zéro erreur,
échec ou ignoré ; 87,162 s écoulées, deux travailleurs à priorité réduite.
Sept fichiers du brief plus `refus_moteur`, `repli_et_appel`, `audits_attendu`,
`narration` et `recit_resultat`. Mur et bobine : questions initiales et
descriptions impératives, enveloppes invalides d'action ou de faits ; texte
exact déjà sauvé au moment de l'affichage, monde/scène/fiche/carte et reprise
inchangés. Sans cible perceptible, la précision G2 reste vérifiée. Les parcours
de transport partagés contrôlent désormais le résultat moteur exact, sa nature
persistée et les vues après reprise, en plus de l'exécution unique.

**Limites.** Réseau et modèles simulés uniquement ; ni Luna, ni banc, ni suite
complète. Les autres contrôles transitoires restent en place. Aucun calcul
actif. Bruts : `C:/Users/msics/donjon/artifacts/suite-295/` (`avant.json`,
`apres.json`, diffs d'attribution, manifeste et `fin-cloture.json`).
