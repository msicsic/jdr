# Tâche Codex 286 : une demande close sur un moyen démenti ne renaît pas par la seule perception

Reprise du lot 273 selon l'option B, décidée par l'utilisateur le 29 octobre. Les deux réalisations du lot 273 (Sol et
DeepSeek, `docs/comparaison-deepseek-sol.md`) gardaient la demande adoptée après l'échec d'un moyen. Elles échouent de
la même façon : suspects 219 de 1 à 3 et richesse de la mine hors de l'étendue de référence. **On garde donc la clôture
actuelle** (la sortie `dementie` de `choisir` sur `e["manque"]`). On corrige seulement la renaissance.

Lis `AGENTS.md`, le rapport 272 (`docs/taches/rapport-codex-272-retour-aubin.md`, bruts
`C:\Users\msics\donjon\artifacts\retour-272\`, capture rechargeable à 117503), le brief 273 et la section 273 de
`docs/comparaison-deepseek-sol.md`. Ne reprends aucun code des branches 273 (`codex-demande-adoptee`,
`ds-demande-adoptee`).

## Le constat (rapport 272)
Relais 2024, départ tiré, joueur passif. Aubin adopte `pulsion {objet: vivres, servir: ilse}` (motif `empathie`, palier
12). Son plan : demander une part à Gorm. Ce geste a déjà échoué à 117170 (refus `necessaire`). À 117503, `choisir`
lit ce geste dans `manque`, clôt la demande en `dementie`, et Ilse sort du champ de vision. À 117518, Ilse redevient
perçue : le candidat `secours` recrée **le même plan, avec le même geste manqué**. Aucune entrée liée à ce geste n'a
changé (ressource, refus, porte, présence du donneur). Seuls la perception et la provenance de `ilse.lieu`
(`entendu` → `vu`) changent. Le rapport relève aussi que le refus du 117170 « ne tient déjà plus » aux trois
relevés : `moyens_crus` y voit `[ouvert, reserve, null, null]`.

## L'invariant
**Un moyen dont l'échec a clos une demande n'est pas repris pour la même raison tant que la cause de cet échec tient,
d'après les croyances du PNJ. Revoir le bénéficiaire ou le donneur n'est pas une entrée qui lève cette cause.** La
demande peut renaître par un autre moyen admissible, ou par le même moyen si une entrée pertinente à sa cause a changé
(juge commun des refus retenus, lots 57/110 : `tient`, `moyens_crus` ; renoncements du lot 225). La clôture `dementie`
reste celle d'aujourd'hui. Aucun délai, aucune exception de personnage, d'objet, de scénario ou de but. Une perception
nouvelle d'une autre nature (le donneur vu avec un bien nouveau, la réserve vue ouverte pour la première fois) reste une
entrée valable.

**Commence par établir**, sur la capture 117503 et l'état à 117518 rechargés, pourquoi le refus de 117170 ne tient plus.
Deux cas :
- `[ouvert, reserve]` était déjà cru à 117170, avant le refus : le juge des refus le compte à tort comme moyen nouveau,
  et c'est là, dans le contrat commun, qu'il faut corriger ;
- cette croyance est apprise après 117170 : la renaissance est justifiée selon les croyances d'Aubin. Rapporte-le
  (`QUESTION : …`) au lieu de corriger.

Lot de 30 à 45 minutes. Pas de Luna, pas de suite complète (le superviseur la lance). **Poste : le PC fixe.** Le lot 285
y tourne, et une suite complète du superviseur jusqu'à sa fin (`C:\Users\msics\donjon\artifacts\suite-essai283-22990c7\FIN.txt`) :
un seul processus à priorité réduite tant qu'elle n'est pas finie, deux ensuite.

**Fichiers attendus** : `donjon/deliberation.py` (le juge des refus et des renoncements, la création du candidat de
secours ou la reprise). Le lot 285 modifie `planification.py` : n'y touche qu'en raccord minimal, et dis-le. Le lot 283
modifie `agendas.py`, `echanges.py`, `social.py` et `paroles.py` : n'y touche pas.

## Vérification
- **Capture réelle rechargée** (117503, puis 117518) : la demande close ne renaît pas avec le geste refusé quand seule
  la perception d'Ilse change. Contre-épreuve : avec une entrée pertinente nouvelle (la réserve vue ouverte pour la
  première fois, ou un autre donneur), elle renaît.
- **Autre cas de même nature** (autre PNJ ou autre scénario), même contre-épreuve. Monde, rendu et scène identiques après
  recharge et laps entier/découpé.
- Fichiers de tests qui exercent les fonctions modifiées (trouve-les par recherche des appelants), dont
  `test_refus_retenus`, `test_reessai*`, `test_empathie*`, `test_rester_pres*`, `test_echelle_choix`.
- **Banc rapide** 4 h, cinq scénarios (`relais`, `mine`, `auberge`, `crue`, `crue_hameau`) × quatre graines, référence
  de l'intégration à ta base (en cache si présente, sinon calculée une fois), sonde actuelle (lots 265, 271, 276).
  Critères :
  - suspects 219 sans hausse par nuit, et le renouvellement perceptif d'Aubin (Relais 2024, 117518) disparu ou
    expliqué ;
  - richesse S/F/D (fonction `cats` du lot 183) dans l'étendue de la référence, la mine en particulier.

  Calcul long détaché, priorité réduite.

## Livraison
- Branche `codex-demande-sans-renaissance` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur). Si la poussée échoue, laisse le commit local, donne son hash et l'erreur exacte, sans passer par l'API
  GitHub.
- Rapport d'une page `docs/taches/rapport-codex-286-demande-sans-renaissance.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\renaissance-286\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
