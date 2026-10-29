# Lot 306 — responsabilité d'évacuation dans le hameau

Branche `codex-a5-agenda-hameau`, **non fusionnée**, base intégration
`7ec839e`, 29 octobre 2026. Données et tests seulement ; aucun moteur
ni MJ modifié. **Vérification détachée lancée sur `8145e48`**, résultats longs
encore à établir. Ni Luna ni suite complète.

**Invariant.** Le dérivé du hameau déclare la responsabilité d'évacuation
de Gorm déjà présente dans la crue : même identifiant `evacuer_crue`, même
sorte `amener`, même destination `chambre_cloche` (la galerie). Seule la
liste des personnes s'étend : **Ilse, Brune, Maël, Sève**. Aucun mandat,
engagement, coût, statut, lien ou connaissance supplémentaire.

Ilse et Brune reprennent la charge d'origine. Maël et Sève sont des
évacués dont la maison est noyée, accueillis au Relais, ignorants de ses
salles basses. Gorm est décrit comme protecteur des évacués et reste pour
les accueillir ; Maël le connaît et lui fait confiance. Sève connaît
Aubin et Ilse, qui la relient à cet accueil. Sa responsabilité ne suppose
pas qu'elle connaisse déjà le statut de Gorm : aucune connaissance de
statut ni relation n'est inventée. Aubin garde son rôle de passeur qui
surveille les vannes et renseigne Gorm, comme dans la crue d'origine ; il
n'est pas ajouté à la liste. Aucune seconde charge `informer` justifiée
par les données, donc aucune ajoutée. Liste fixée avant les mesures.

**45 tests distincts / sept fichiers verts**, au plus deux travailleurs
réduits. Trois nouveaux tests : parité de déclaration avec la crue,
activation unique sur quatre graines sans mouvement ni attribution,
deux scènes d'auteur Maël/Sève avec route ouverte et besoins calmes.
La demande est réellement acceptée, puis le destinataire marche par son
propre choix ; le groupe n'est pas transporté. Monde complet, scène,
rendu et écoute vérifiés après sauvegarde/recharge ; temps continu et
découpé identiques. Le test 302 est adapté à la responsabilité déclarée :
il contrôle toujours l'absence de mandat initial. Tests voisins : hameau,
autorité, déplacement social Ilse/Brune, faire/confier, compte rendu et
réaffectation. Les premières erreurs des nouvelles scènes (mauvais
import de support et placements superposés) sont corrigées ; aucun oracle
du moteur affaibli. Temporaires Windows refusés sous sandbox ; passes
retenues hors sandbox. `git diff --check` vert.

**Vérification longue en cours.** Crue d'origine : empreintes 2 h × quatre
graines ; hameau : banc 4 h × quatre graines, référence figée `7ec839e`,
cache commun, référence puis branche, deux travailleurs réduits maximum.
Captures latérales du premier choix et de l'état final, sans changer les
résultats du comparateur ; rechargement et rendu contrôlés, devis chiffrés
conservés. Compteurs A5 publics, états d'évacuation, présences finales à
la galerie, suspects 219 par nuit, boucles et usurpations à lire avant
clôture. Lanceur détaché PID **41884**, priorité `BelowNormal`. Une
présence initiale ou finale ne prouve pas à elle seule une
évacuation causée par Gorm. Aucune donnée ne sera ajustée après mesure.

Bruts : `C:/Users/msics/donjon/artifacts/agenda-hameau-306/` ; lanceur,
tests, `crue-empreintes.json`, `hameau-banc.json`, `analyse.json`, captures
et `fin.json` écrit en dernier même en cas d'échec. **Limites actuelles :
aucune réussite générale d'évacuation ni stabilité des nuits revendiquée
avant lecture du banc.** Compte rendu et réaffectation naturels ne sont
pas garantis par la seule déclaration d'agenda.
