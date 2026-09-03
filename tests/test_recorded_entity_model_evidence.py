import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(rel):
    return json.loads((ROOT/rel).read_text())

def test_xbox_entity_model_corpus_invariants():
    s=load('evidence/decoded/xbox_entity_models_resident_summary.json')
    assert s['resident_model_count']==16
    assert s['mesh_count']==23
    assert s['part_count']==284
    assert all(s['invariants'].values())
    assert s['stage_code_counts']['000-00000000-000000']==12

def test_xbox_808b3a16_model_fixture():
    d=load('evidence/decoded/xbox_entity_model_808B3A16_summary.json')
    assert d['platform']=='XboxOne'
    assert d['class_hash']=='80801AB5'
    m=d['model']
    assert m['tag_hash']=='808B3A16'
    assert m['mesh_count']==2
    a,b=m['meshes']
    assert (a['vertices1'],a['vertices2'],a['indices'])==('808B3A19','808B3A1A','808B3A1B')
    assert (b['vertices1'],b['vertices2'],b['indices'])==('808B3A1C','808B3A1D','808B3A1E')
    assert a['part_count']==7 and b['part_count']==9
    assert a['stage_part_offsets'][-1]==7 and b['stage_part_offsets'][-1]==9
    assert {(p['index_offset'],p['index_count']) for p in a['parts']}=={(0,612),(612,126),(738,12)}
    assert {(p['index_offset'],p['index_count']) for p in b['parts']}=={(0,2049),(2049,84),(2133,18)}

def test_xbox_material_reference_offsets():
    d=load('evidence/decoded/xbox_materials_80801C32_summary.json')
    assert d['material_class_hash']=='80801C32'
    assert d['total_entries']==805
    assert d['resident_entries']==411
    by={x['offset']:x for x in d['reference_offsets']}
    assert by[0x2A8]['matches']==396
    assert by[0x2A8]['target_class_hash']=='80801B7C'
    assert by[0x32C]['matches']==232
    assert by[0x32C]['target_class_hash']=='80801AA5'
    assert by[0x404]['matches']==370
    assert by[0x404]['target_type_counts']['32:1']==370
