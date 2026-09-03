import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(name): return json.loads((ROOT/'evidence/decoded'/name).read_text())

def test_xbox_material_shader_binding_regression():
    d=load('xbox_material_dxbc_bindings_regression.json'); s=d['summary']
    assert s['resident_materials_selected']==411 and s['pixel_shader_compared']==11
    assert s['texture_register_exact']==11 and s['texture_register_mismatch']==0
    assert s['sampler_count_exact']==11 and s['sampler_count_mismatch']==0
    assert s['b0_count_exact']==11 and s['b0_count_mismatch']==0
    assert len(d['compared'])==11
    for x in d['compared']:
        assert x['material_texture_indices']==x['shader_texture_registers']
        assert x['material_sampler_count']==len(x['shader_sampler_registers'])
        assert x['shader_sampler_registers']==list(range(1,x['material_sampler_count']+1))
        assert x['material_b0_vec4_count']==x['shader_b0_vec4_count'] or (x['material_b0_vec4_count']==0 and x['shader_b0_vec4_count'] is None)

def test_xbox_vector_container_regression():
    d=load('xbox_vector_container_80801AA5_regression.json')
    assert d['total_entries']==595 and d['resident_entries']==276
    assert all(d['all_resident_invariants'].values())
