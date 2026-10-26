# Tâche Codex 133 : une promesse acceptée est tenable au moment où elle est acceptée

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus 2 processus de calcul,
priorité réduite. Ce lot touche `echanges.py`, `agendas.py` et si besoin `planification.py` (devis) ; **pas** `signes.py`
(lot 129), ni `deliberation.py`, `pnj.py`, `banc_pnj.py` (lot 130), ni le MJ. Termine ton dernier message par `LOT TERMINÉ`
(résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, le rapport du lot 131 (`docs/taches/rapport-codex-131-verif-integ.md`, défaut nouveau), les rapports des lots 57
(devis validé par les livraisons communes), 97 (devis sans profil), 115 (tâche promise en contrepartie), puis
`echanges.promesse_autonome`, `echanges.proposer`, `echanges.devis_service`, `echanges.empeche`, `agendas.echoir`,
`planification.devis_pulsion`.

## Le défaut (vérification d'intégration 057766f, lot 131)
Crue **11**, **Ilse → Aubin à 210 min** : Ilse promet de verrouiller la porte contre le pied-de-biche ; l'offre est acceptée à
l'instant 126226 (dixièmes), puis l'engagement est abandonné pour impossibilité à 126336, **11 s plus tard**, sans aucun geste
sur la porte entre les deux. La porte avait été forcée par Aubin à 86. Souvenirs : engagement pris, proposition acceptée,
engagement abandonné, abandon annoncé. Le marché n'existe pas dans la même nuit sur `590653e`. Bruts sur le portable
(`artifacts/verif-integ-057766f/audit-12h/crue_11.json.gz`, analyse `analyse-131/`) : **rejoue la nuit crue 11, 12 h, départ
de l'audit** (`tools/audit_nuits.py`, mêmes options que `campagnes.ps1` du lot 131, recopiées dans le rapport) pour capturer
l'état juste avant 210.

## L'invariant
**Le devis qui fait proposer ou accepter une promesse et le contrôle qui la déclare impossible partagent les mêmes
préconditions, lues sur le même état.** Une impossibilité préexistante (ici, probablement une porte forcée qui ne se verrouille
plus) ne peut pas devenir une promesse acceptée puis annulée aussitôt. Établis d'abord la cause exacte du désaccord entre
`promesse_autonome`/`devis_service` et `empeche`, puis corrige le contrat commun (une seule fonction de faisabilité, ou les
mêmes lectures), sans règle propre aux portes, au verrouillage ou à Ilse. Si le désaccord vient d'une croyance (le promettant
ignore que la porte est forcée), dis-le : promettre sur une croyance fausse peut rester légitime, et l'invariant devient alors
« l'abandon suit une découverte réelle » ; ne masque pas ce cas.

## Vérification
- Capture réelle juste avant 210 et un autre cas de même nature (autre tâche promise dont la précondition est fausse avant
  l'accord) : plus d'acceptation suivie d'un abandon sans fait nouveau ; état, souvenirs et rendu après rechargement, même laps
  d'un bloc ou découpé ; une promesse réellement tenable reste proposée, acceptée et tenue.
- Banc rapide 4 h, quatre scénarios × quatre graines contre la base (cache) : propositions/acceptées/tenues/rompues, aucune
  usurpation ni boucle nouvelle. Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-promesse-tenable` poussée (pas `main`).
`docs/etat-dev.md` (« Branche `codex-promesse-tenable`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-133-promesse-tenable.md`.
