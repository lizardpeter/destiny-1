#!/usr/bin/env python3
"""Recover the exact current PS4 Tower dependency corpus from the split public TAR.

This centralizes the package identities already proven by earlier Tower workflows.
Every recovered member is SHA-256 pinned.  Current archive family membership is
also checked against the expected sibling set before any bytes are used.

This tool does NOT infer semantic ownership from package names.  The package set
was established by serialized FileHash/static-table dependency closure; this script
only reproduces those exact physical archive members.
"""
from __future__ import annotations

import argparse, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_split_tar_extract import SplitHttpTar

CORE = [
    ('ps4_arch_human_earth_city_009f_0.pkg',2870153216,269680640,'7446d5c4b8c2ca3fed6bb0b13a649ff68052a8a2fcfa3aae1b38bf8356c54813'),
    ('ps4_arch_human_earth_city_009f_1.pkg',3139834368,32270336,'e5907ac4b5ba8256c23b667b5f1b237b729db824503a225c9b39daad993d7719'),
    ('ps4_arch_human_earth_city_009f_2.pkg',3172105216,203638784,'467047bcfab0281f0f1a69ea2e43038c9e1bc616b0214f1cdc62eb7666844b24'),
    ('ps4_arch_human_earth_city_009f_4.pkg',3375744512,116736,'0f58f8042d96852a1641e4b4378d2b6f7316b15ba8c6294cd5674e5ac61dc504'),
    ('ps4_city_tower_destination_024c_0.pkg',7542949376,137527296,'ffb2e3cbb9777956384063e3c0fc5636200df51ae82a35a6aad06850dbf1fff2'),
    ('ps4_city_tower_destination_024c_1.pkg',7680477184,12226560,'21e75033fcba2f85b5d22b7377a7122c5135ce2c3f10f8453fc54a1d304c10f8'),
    ('ps4_city_tower_destination_024c_2.pkg',7692704256,13574144,'681349e0d32c213cae4bdef839bee8a6fa5aa3a5989c4a5344ee342cbe9d6e45'),
    ('ps4_city_tower_destination_024c_3.pkg',7706278912,2134016,'c6846bbe0bdf9aaf9ba194ed8a2a3b2c7e26178bd79218134e909fa460ebcaef'),
    ('ps4_city_tower_destination_024c_4.pkg',7708413440,6987776,'12dfe5e7dc65a8477d5ceabba5bb921b07c83110151a57b86a52ba3eb7d82018'),
    ('ps4_city_tower_destination_024c_5.pkg',7715401728,1687552,'b404bacccf44a4bf6859bf3b867ae02f5dc840432bdaa081c341439c2ae83311'),
    ('ps4_city_tower_destination_0250_0.pkg',7882616320,294875136,'beb269a2673f1106e2eff20ff577d0221d7fa56a8b71f5f8763cf34272114b32'),
    ('ps4_city_tower_destination_0250_1.pkg',8177491968,17983488,'87904a97ce9899305b6bdba9df960d220749b3b2398c4ba8bd97e6efb8f81f91'),
    ('ps4_city_tower_destination_0250_2.pkg',8195475968,11143168,'7543c1926023ec76ff8949618e04e1d0a93609f8448a1f8f875fcfc505a6b219'),
    ('ps4_city_tower_destination_0250_3.pkg',8206619648,206848,'1db9423081f922b78cce256641dfab195e6a4b4afb6020e4e0c5029234f19375'),
    ('ps4_city_tower_destination_0250_4.pkg',8206827008,17901568,'5a9370d60724622fb6592a7bcfa2fc4dbb40a4fca5cd696ce8db086a5756e84f'),
    ('ps4_city_tower_destination_0250_5.pkg',8224729088,1677312,'2066afe09503eee4c35d948f6749a6e7b7b02572dcd41d1d3ca679fa523ea22c'),
    ('ps4_globals_0157_0.pkg',18974578176,206192640,'e4f0844d75dde0d062ddf42f6a13b82d00689b76543c28255aefa28785d3f7b6'),
    ('ps4_globals_0157_1.pkg',19180771328,30326784,'91c19b8c392f8f12c98ec6527306190fe2a59012abfe016a975b54b42a7dad2f'),
    ('ps4_globals_0157_2.pkg',19211098624,30464000,'c8f71e22a37d2feed68178dbb60aed245bfbbe5d342c70d0e11dfd580684573f'),
    ('ps4_globals_0157_3.pkg',19241563136,268288,'d06814d03e9b00d9df8ed683bff036627cd3195edb8fe58fcf80566c13d3f79a'),
    ('ps4_globals_0157_4.pkg',19241831936,546816,'98b0e7abdfd88eabe7a3d6534b8f487dbbaa4ea0bf8e87b2d0fe6ec29c229077'),
    ('ps4_globals_0157_5.pkg',19242379264,380928,'723b1d79ed9904474bd737f9af6065dc6b6266eaf2c59d123e3452434550089c'),
    ('ps4_globals_0157_6.pkg',19242760704,356352,'51cb4f9bdb8a10e0fc25de757a9885641cce0c887549019831b9a0687a44b089'),
    ('ps4_env_skies_01cf_0.pkg',14216130048,277645312,'f45d85c89f46e5ba9585073f105b8a1c1229c4d543b56e38ccc840a0010d297a'),
    ('ps4_env_skies_01cf_1.pkg',14493775872,3885056,'16a54200f04680d06ed3936afc44aac1eaea8f111cc44acac2fa18cdd394b34f'),
    ('ps4_env_skies_01cf_2.pkg',14497661440,87631872,'1999fa9d728ef75393f59171325b397cb1356d94322694b6fedd60e339f171f9'),
]
EXTRA_IDS = {'00ef','013a','0169','01c5','01d1','01e3'}
ALL_IDS = {'009f','024c','0250','0157','01cf'} | EXTRA_IDS


def pkg_id(name: str) -> str | None:
    m = re.search(r'_([0-9a-fA-F]{4})_[0-9]+\.pkg$', name)
    return m.group(1).lower() if m else None


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-list',type=Path,required=True)
    ap.add_argument('--dependency-offset-catalog',type=Path,default=Path('evidence/d1_tower_dependency_member_catalog.json'))
    ap.add_argument('--dependency-sha-catalog',type=Path,default=Path('evidence/d1_tower_dependency_sha256_catalog.json'))
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    a=ap.parse_args()

    dep=json.loads(a.dependency_offset_catalog.read_text())
    sha_doc=json.loads(a.dependency_sha_catalog.read_text())
    sha_by_name={x['name']:x['sha256'].lower() for x in sha_doc['members']}
    extras=[]
    for row in dep['members']:
        if pkg_id(row['name']) in EXTRA_IDS:
            name=row['name']
            if name not in sha_by_name:
                raise SystemExit(f'missing pinned SHA-256 for dependency member {name}')
            extras.append((name,int(row['data_offset']),int(row['size']),sha_by_name[name]))

    members=CORE+extras
    expected_names={x[0] for x in members}
    listed={Path(x.strip()).name for x in a.package_list.read_text(errors='replace').splitlines() if x.strip()}
    current={i:sorted(n for n in listed if pkg_id(n)==i) for i in ALL_IDS}
    expected={i:sorted(n for n in expected_names if pkg_id(n)==i) for i in ALL_IDS}
    mismatch={i:{'expected':expected[i],'current':current[i]} for i in sorted(ALL_IDS) if expected[i]!=current[i]}
    if mismatch:
        raise SystemExit('current archive family membership differs from pinned corpus: '+json.dumps(mismatch,indent=2))

    a.out_dir.mkdir(parents=True,exist_ok=True)
    arc=SplitHttpTar([f'{a.base_url}/packages.tar.{i:03d}' for i in range(1,11)],retries=6,timeout=120)
    rows=[]
    for name,off,size,expected_sha in members:
        got=arc.copy_to(off,size,a.out_dir/name)
        if got.lower()!=expected_sha.lower():
            raise SystemExit(f'{name}: SHA mismatch {got} != {expected_sha}')
        rows.append({'name':name,'data_offset':off,'size':size,'sha256':got,'sha_pinned':True})
        print('RECOVERED',name,size,got,flush=True)

    report={
        'schema_version':1,
        'evidence_status':'EXACT_CURRENT_TOWER_DEPENDENCY_CORPUS_SHA256_VERIFIED',
        'package_ids':sorted(ALL_IDS),
        'member_count':len(rows),
        'family_membership':current,
        'members':rows,
        'policy':'Physical package selection is reproduced from previously proven serialized dependency closure; filenames are not semantic ownership evidence.',
    }
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,indent=2)+'\n')
    return 0

if __name__=='__main__': raise SystemExit(main())
