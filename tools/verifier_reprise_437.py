"""Campagne détachée du lot 437 : empreintes puis nuit renforcée, sans Luna."""
import argparse
import gzip
import json
from pathlib import Path
import subprocess
import sys
import traceback
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tools')]
from priorite import ceder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dossier', type=Path, required=True)
    parser.add_argument('--reference', required=True)
    args = parser.parse_args()
    ceder()
    dossier = args.dossier.resolve()
    dossier.mkdir(parents=True, exist_ok=True)
    bilan = {'reference': args.reference, 'succes': False}
    try:
        commande = [sys.executable, str(ROOT / 'tools/comparer_bancs.py'), '--reference', args.reference,
                    '--empreintes', '--scenarios', 'auberge', 'relais', '--graines', '1985', '7', '42', '2024',
                    '--heures', '2', '--processus', '2', '--sortie', str(dossier / 'empreintes.json')]
        with (dossier / 'empreintes.log').open('w', encoding='utf8') as flux:
            code = subprocess.run(commande, cwd=ROOT, stdout=flux, stderr=subprocess.STDOUT).returncode
        bilan['empreintes_code'] = code
        if code:
            return
        from donjon import banc_pnj as banc, planification as p, spatial
        from donjon.monde import Monde
        from donjon.rendu import regarder
        from donjon.scene import scene_percue
        monde_final = []
        creer, verifier = banc.creer, p._verifier
        def creation(*a, **kw):
            m = creer(*a, **kw)
            monde_final.append(m)
            return m
        def controle(*a, **kw):
            resultat = verifier(*a, **kw)
            if a[1] == 'lucien' and a[12] == 'placer:ballot' and a[0].data['minutes'] == 303:
                capture = dossier / 'placer-303.json.gz'
                if not capture.exists():
                    capture.write_bytes(gzip.compress(json.dumps(a[0].data).encode(), mtime=0))
                    (dossier / 'placer-303.json').write_text(json.dumps({
                        'borne_jouee': a[14], 'reprise': a[15], 'signal': p.BORNES[-1:]}, indent=2), encoding='utf8')
            return resultat
        with patch.object(p, 'VERIFIER', True), patch.object(spatial, 'VERIFICATION', .2), \
                patch.object(banc, 'creer', creation), patch.object(p, '_verifier', controle):
            _, _, data = banc.nuit('auberge', 42, 8, 'dortoir', diagnostic=True)
        (dossier / 'auberge-42-8h.json.gz').write_bytes(gzip.compress(json.dumps(data).encode(), mtime=0))
        m = monde_final[0]
        chemin = dossier / 'etat-final.json'
        m.sauver(chemin)
        recharge = Monde.charger(chemin)
        assert (m.data, regarder(m), scene_percue(m)) == (recharge.data, regarder(recharge), scene_percue(recharge))
        bilan.update(succes=True, minute_finale=m.data['minutes'], bornes=p.BORNES,
                     recharge_et_rendu_identiques=True)
    except Exception:
        bilan['erreur'] = traceback.format_exc()
    finally:
        (dossier / 'FIN.json').write_text(json.dumps(bilan, indent=2), encoding='utf8')


if __name__ == '__main__':
    main()
