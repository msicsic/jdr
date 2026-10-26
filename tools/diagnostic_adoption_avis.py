"""Lot 125 : observation seule, six nuits, sans Luna (un processus réduit).

Usage : python tools/diagnostic_adoption_avis.py
Les empreintes comparent chaque nuit instrumentée à son rejeu sans sonde.
"""
import copy
import csv
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path = [p for p in sys.path if Path(p).resolve() != Path(__file__).resolve().parent]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from donjon import banc_pnj as banc, esprits, social, eau
from donjon.monde import Monde
from donjon.voix import source_dite
from donjon.relations import envers
from donjon.rendu import regarder

SORTIE = Path('artifacts/adoption-125')


def empreinte(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def nuit(graine, heures, observe):
    from donjon import planification
    # Le banc vide mémoire et graphes ; vider aussi les impossibilités entre nuits.
    planification._IMPOSSIBLES.clear()
    receptions, paroles, captures = [], [], []
    monde_final = []
    creer, recevoir, contradiction = banc.creer, esprits.recevoir_prevision, social._contradiction

    def creation(*a, **k):
        m = creer(*a, **k)
        monde_final.append(m)
        return m

    def reception(m, id, locuteur, avis, rang, **kw):
        avant = empreinte(m.data)
        propre = copy.deepcopy(esprits.prevision_propre(m, id))
        actuelle = copy.deepcopy(esprits.prevision(m, id, avis['objet']))
        meme = eau.menacee(m, id, avis['objet']) == avis['valeur']
        poids = social._poids_dit(m, id, locuteur, avis)
        acquis = round(esprits.poids_source(m, id, actuelle) * actuelle['confiance'], 12) if actuelle else 0
        recent = bool(actuelle and actuelle['source'] in ('vu', 'essai') and actuelle['minute'] > avis['observe'])
        ligne = dict(minute=m.data['minutes'], dixiemes=m.data.get('dixiemes', 0),
                     locuteur=locuteur, auditeur=id, lieu=m.objets[locuteur]['lieu'],
                     avis=copy.deepcopy(avis), propre=propre, actuelle=actuelle,
                     relation=copy.deepcopy(envers(m, id, locuteur)), source=source_dite(m, id, locuteur),
                     poids_recu=poids, poids_acquis=acquis, meme_avis=meme, propre_plus_recent=recent)
        ligne['classe'] = ('même avis déjà tenu' if meme else
                           'constat propre plus récent et plus fort' if propre and recent and acquis > poids else
                           'poids inférieur malgré l’absence de constat' if not propre and poids < acquis else 'autre')
        assert empreinte(m.data) == avant, 'La sonde a modifié le monde'
        # Deux états complets avant réception, deux graines distinctes, sans sauver le monde vivant.
        if graine in (500, 2024) and heures == 12 and not captures:
            captures.append((copy.deepcopy(m.data), ligne, rang))
        issue = recevoir(m, id, locuteur, avis, rang, **kw)
        ligne['issue'] = issue
        ligne['apres'] = copy.deepcopy(esprits.prevision(m, id, avis['objet']))
        receptions.append(ligne)
        return issue

    def opposer(m, locuteur, avis, entendus):
        avant = empreinte(m.data)
        auditeurs = []
        for id, c in entendus.items():
            a = social._avis_de(m, id, avis['objet'], c) if c else None
            auditeurs.append(dict(id=id, prevision=copy.deepcopy(c), avis=a,
                                  contraire=bool(a and a['valeur'] != avis['valeur']),
                                  poids_recu=social._poids_dit(m, id, locuteur, avis)))
        assert empreinte(m.data) == avant
        resultat = contradiction(m, locuteur, avis, entendus)
        paroles.append(dict(minute=m.data['minutes'], locuteur=locuteur, avis=copy.deepcopy(avis),
                            auditeurs=auditeurs, opposition=copy.deepcopy(resultat)))
        return resultat

    with patch.object(banc, 'creer', creation):
        if observe:
            with patch.object(esprits, 'recevoir_prevision', reception), patch.object(social, '_contradiction', opposer):
                _, _, donnees = banc.nuit('crue', graine, heures, 'chambre_cloche')
        else:
            _, _, donnees = banc.nuit('crue', graine, heures, 'chambre_cloche')
    m = monde_final[0]
    resultat = dict(graine=graine, heures=heures, etat_final=empreinte(m.data),
                    chronique=empreinte(donnees['chronique']), empreintes=donnees['empreintes'],
                    mesures=donnees['mesures'], avis_dits=[c for c in donnees['chronique'] if c.get('avis_exprime')],
                    receptions=receptions, contradictions=paroles)
    for data, ligne, rang in captures:
        nom = SORTIE / f'capture-{graine}.json'
        Monde(data).sauver(nom)
        essais = []
        for _ in range(2):
            recharge = Monde.charger(nom)
            issue = recevoir(recharge, ligne['auditeur'], ligne['locuteur'], ligne['avis'], rang)
            rendu = regarder(recharge)
            apres = SORTIE / f'apres-{graine}.json'
            recharge.sauver(apres)
            relu = Monde.charger(apres)
            assert regarder(relu) == rendu
            assert esprits.prevision(relu, ligne['auditeur'], ligne['avis']['objet']) == ligne['apres']
            essais.append(dict(issue=issue, etat=empreinte(relu.data), rendu=rendu))
        assert essais[0] == essais[1] and essais[0]['issue'] == ligne['issue']
        resultat['recharge'] = essais
    return resultat


def main():
    banc.ceder()
    SORTIE.mkdir(parents=True, exist_ok=True)
    for graine, heures in ((1985, 4), (7, 4), (42, 4), (2024, 4), (500, 12), (2024, 12)):
        if (SORTIE / f'nuit-{graine}-{heures}h.json').exists():
            print(graine, heures, 'déjà mesurée', flush=True)
            continue
        instrumente = nuit(graine, heures, True)
        temoin = nuit(graine, heures, False)
        for cle in ('etat_final', 'chronique', 'empreintes', 'mesures'):
            if instrumente[cle] != temoin[cle]:
                (SORTIE / f'ecart-{graine}-{heures}h.json').write_text(json.dumps([instrumente, temoin], ensure_ascii=False, indent=2), encoding='utf8')
            assert instrumente[cle] == temoin[cle], (graine, heures, cle)
        instrumente['identique_sans_sonde'] = True
        (SORTIE / f'nuit-{graine}-{heures}h.json').write_text(json.dumps(instrumente, ensure_ascii=False, indent=2), encoding='utf8')
        print(graine, heures, len(instrumente['receptions']), 'réceptions ; empreintes identiques', flush=True)


def verifier_captures():
    """Captures historiques : parole entière, monde et perception après recharge.

    Chemin fixe dans artifacts : contourne les ACL TemporaryDirectory du bac Windows.
    """
    import unittest
    import tests.test_social as support
    banc.ceder()
    SORTIE.mkdir(parents=True, exist_ok=True)

    def recharger(m):
        chemin = SORTIE / 'recharge-tests.json'
        m.sauver(chemin)
        return Monde.charger(chemin)

    with patch.object(support, 'recharger', recharger):
        import tests.test_avis_reels as tests
        with patch.object(tests, 'recharger', recharger):
            resultat = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    assert resultat.wasSuccessful()


def tableau():
    """Une ligne par réception (destinataire et témoins), détail complet dans les JSON."""
    lignes = []
    for chemin in sorted(SORTIE.glob('nuit-*.json')):
        nuit = json.loads(chemin.read_text(encoding='utf8'))
        for r in nuit['receptions']:
            c = r['actuelle'] or {}
            lignes.append(dict(graine=nuit['graine'], heures=nuit['heures'], minute=r['minute'],
                               dixiemes=r['dixiemes'], locuteur=r['locuteur'], auditeur=r['auditeur'],
                               lieu=r['lieu'], objet=r['avis']['objet'], valeur=r['avis']['valeur'],
                               conviction_dite=r['avis']['conviction'], observe=r['avis']['observe'],
                               source=c.get('source'), minute_acquise=c.get('minute'),
                               conviction_acquise=c.get('confiance'), prevision=c.get('valeur'),
                               poids_recu=r['poids_recu'], poids_acquis=r['poids_acquis'],
                               classe=r['classe'], issue=r['issue']))
    with (SORTIE / 'receptions.csv').open('w', encoding='utf-8-sig', newline='') as f:
        ecrivain = csv.DictWriter(f, fieldnames=list(lignes[0]))
        ecrivain.writeheader()
        ecrivain.writerows(lignes)
    print(len(lignes), 'réceptions exportées')


if __name__ == '__main__':
    if '--captures' in sys.argv:
        verifier_captures()
    elif '--tableau' in sys.argv:
        tableau()
    else:
        main()
        tableau()
