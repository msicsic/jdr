# Tâche Codex 83 : un segment que l'auditeur dit contredit ou non établi n'est pas admis comme établi

Branche `codex-verdict-coherent` (elle porte ce fichier, issue de l'intégration **3ffd72d**), worktree dans `tmp-worktrees/`.
**Lot de 30 à 45 minutes**. **Luna disponible** (copies seulement ; `tools/banc_multi.py --connexion chatgpt`). Un seul
poste : priorité réduite, au plus 3 processus. **À lancer après le lot 82** (mêmes fichiers du récit) ;
`git merge origin/integration` au début.

Lis `AGENTS.md`, le **rapport du lot 79** (défauts **N2, N3, N4**), `docs/etat-dev.md` (entrées `codex-contenu-vide` 59
(`portee_mecanique`), `codex-gardes-justes` 74, `codex-comptes-issue` 73), `docs/contrat-mj.md`, puis `donjon/narration.py`
(schéma du rapport d'audit, `controler`, `consigner`, contrôle des comptes et de leurs références).

## Le constat (vérification Luna 882907c)
- **N2** (`signes-noir` p2 n° 2) : « elle n'est pas là pour que tu le lui demandes » alors qu'Ilse est dans l'antichambre ;
  l'audit écrit que l'absence n'est pas établie, mais classe la phrase `mecanique`/`etablie` ; elle est affichée.
- **N3** (`crypte` p2 n° 26) : « Gorm est […] face à toi » alors qu'il est au sud-ouest, orienté sud-est ; l'audit dit
  l'assertion contredite, tout en renvoyant `mecanique`/`etablie`.
- **N4** (`comptes` p1 n° 1) : « Gorm te rend les deux pièces » rejeté parce que l'extraction des comptes donne `gorm`/`Corvus`
  au lieu de `marchand`/`joueur` ; mêmes rôles, faux rejet dû aux références.

## L'invariant
**Le rapport d'audit doit être cohérent avant d'être cru** : un segment dont le motif de l'auditeur dit lui-même qu'il est
contredit ou non établi ne peut pas être classé `mecanique`/`etablie` ; une telle incohérence est un rapport illisible, redemandé
une fois à l'auditeur (règle existante des rapports illisibles), et jamais affiché tel quel. Et **les références d'un compte
extrait se résolvent comme toutes les références du récit** (noms publics, identifiants, « Corvus » → `joueur`) avant la
comparaison déterministe des comptes. Pas de liste de mots : la cohérence se lit sur les champs typés du rapport (verdict,
portée, sources, contradiction signalée) ; si le motif libre est la seule trace, dis la limite.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : un rapport incohérent (verdict établi, contradiction signalée)
  redemandé puis corrigé ; un rapport cohérent inchangé ; le remboursement de Gorm nommé « Gorm »/« Corvus » accepté.
- Luna, **une passe** : `signes-noir`, `crypte`, `comptes`, référence 882907c lue du cache ; textes affichés.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-verdict-coherent`,
non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-83-verdict-coherent.md`.
