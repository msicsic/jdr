# Lot 341 — A5.9, le joueur mandant et mandaté

Branche **codex-mandat-joueur, non fusionnée**, base fournie fff9aab.
**Reprise terminée**, code validé 1a52135. Origin/integration **4379616**
fusionnée sans rebase par **417e67f**, parents a54b3f2 et 4379616 :
conflit documentaire seul, invariants 340/341 conservés. Jeu.py inchangé.

**Contrat commun.** Les actes mandat, reponse_mandat et bilan_mandat passent
par le jugement, la filiation, les attributions et le compte rendu existants.
Offre entendue et accord distincts ; aucune exécution forcée de Corvus.
Réponses moteur admises G15/G17 avant publication ; « Compris », fiche et
comptes persistants. Voix inconnue/prétendue et agendas privés gardés.
La façade des agendas valide la recharge, sans esprit autonome du joueur.

**Corrections générales de la reprise.** Les définitions partagées du
compilateur et de la revue distinguent l'acte immédiat du fait confié à un
tiers ; une information représentable reste typée même visible ou déjà
connue. Le contrôle de couverture demeure strict. La revue nomme maintenant
les références à toute profondeur du contenu par le registre commun, sans
réécrire la prose. Aucun mot-clé, objet ou lieu particulier au moteur.
Deux témoins rouges puis verts sur informer et amener contrôlent le
jugement, les mots et l'état après recharge.

**Validation finale : 185/185 tests, vingt fichiers, 248,170 s**, aucun échec,
erreur ou saut. Ascendant 340 **13/13**, socle **6/6**, douze méthodes joueur ;
désignations et fidélité comptable comprises. Sources/tests encore identiques
aux empreintes de validation à la clôture.

**Dernière passe Luna, saisie par saisie** : cinq tours, quatre avec MJ,
dix appels, seul modèle gpt-6-luna. Les cartes d'opérations sont cohérentes.

| Saisie | Typage de Luna | Issue constatée dans la sauvegarde rechargée |
| --- | --- | --- |
| « Aubin, je te confie la charge d'amener Brune dans l'échoppe. » | mandat/amener ; qui=[brune], lieu=l'échoppe | Lieu inconnu : rejet moteur avant parole, aucun jugement PNJ. |
| « Aubin, je te confie la charge d'informer Brune que le brasero est dans l'antichambre. » | mandat/informer ; fait={affirmation, brasero, lieu, antichambre} | Parole prononcée, issue=impossible, raison=impossible, avant jet ; abus honnetete/prix 37,142857 enregistré. |
| « Aubin, Brune est ici, dans le refuge du relais. » | affirmation ; sujet=brune, attribut=lieu, valeur=antichambre | Information transmise ; aucun mandat créé. |
| « Aubin, je te confie la charge d'informer Brune que le fanal est dans le refuge du relais. » | mandat/informer ; fait={affirmation, fanal, lieu, antichambre} | **Accepté**, raison=adhesion, total=6, DD=4,033333, coût=0,166667 ; parent j2 → Aubin/a1, attribution active. Réplique moteur « J'accepte cette charge ». |
| fiche | Commande directe, aucun appel Luna | Même jugement et même filiation relus. |

Zéro erreur technique, mention sans fondement, arrêt ou erreur de recharge.
Le validateur contrôle types, couverture **et admission au jugement réel** :
un repli en parole libre ne vaut plus validation du cas réalisable.

**Acquis et limites.** Les huit paires initiales 2 h Relais/hameau restent
identiques (fff9aab → 9a8c204, avant les corrections de revue) ; références
absentes calculées une fois puis mises au cache, aucune référence relancée.
Pas de nouvelles nuits pour les seules définitions/données de revue du
joueur. Choix autonome PNJ inchangé ; informer joueur limité aux faits de
lieu/verrouillage. Aucune échéance inventée ni garantie de toute formulation.
Cette passe prouve l'accord ; exécution et compte rendu restent attestés par
les scènes avec MJ simulé.

Les étapes antérieures restent archivées : 169 tests consolidés, puis
174 et 175 tests ; erreurs d'archive 86/87 et défauts Luna non effacés.
La première reprise neutralisait une affirmation en propos ; la suivante
typait correctement mais refusait à tort un identifiant de lieu non nommé.
Leurs bilans techniques verts et analyses sémantiques rouges sont conservés.

Bruts : **C:/Users/msics/donjon/artifacts/mandat-joueur-341/reprise-integration/**.
Validation-references/fin.json : **ok=true**, codes tests/Luna 0,
sémantique vraie, **un accord accepté**, sources inchangées, **317,267 s**.
Deux travailleurs réduits au plus, aucun calcul actif, aucune suite complète.
Analyse-cloture.json et fin-cloture.json : lecture des preuves, sans rejeu.
