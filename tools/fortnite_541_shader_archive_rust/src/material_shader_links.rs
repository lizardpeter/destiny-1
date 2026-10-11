//! Authentic cooked UE4 material shader-code identity matcher.
//!
//! A UE4 material/landscape export can contain 20-byte shader-library code
//! hashes. Discover *only exact* hits against the authenticated original
//! shader archive index, recording source byte offsets for later typed
//! FMaterialShaderMap parsing. A raw hit is identity evidence, NOT proof that
//! the pass is active nor a license to pick a shader arbitrarily.
use crate::shader_archive::ShaderArchiveIndex;
use std::collections::{BTreeMap,BTreeSet,HashMap};

const MAX_SOURCE_PACKAGE_BYTES:usize=64*1024*1024;
const MAX_REFERENCES:usize=250_000;
#[derive(Debug,Clone,Copy,PartialEq,Eq)]
pub struct SourceShaderHashReference{
    pub source_byte_offset:usize,
    pub library_ordinal:usize,
    pub shader_frequency:u8,
    pub source_shader_hash:[u8;20],
}
#[derive(Debug,Clone,Default)]
pub struct ShaderHashCensus{
    pub references:Vec<SourceShaderHashReference>,
    /// Number of unique compiled shader identities, not repeated code uses.
    pub unique_library_shaders:usize,
    pub references_per_frequency:[usize;6],
}
impl ShaderHashCensus{
    pub fn source_offsets_by_shader(&self)->BTreeMap<usize,Vec<usize>>{
        let mut result=BTreeMap::new();
        for r in &self.references{
            result.entry(r.library_ordinal)
                .or_insert_with(Vec::new).push(r.source_byte_offset);
        }
        result
    }
}
/// Returns exact hash hits and their original byte positions. Hash bytes
/// are never substituted from texture or material function names.
pub fn match_material_shader_hashes(
    library:&ShaderArchiveIndex,source:&[u8],
)->Result<ShaderHashCensus,String>{
    if source.len()>MAX_SOURCE_PACKAGE_BYTES{
        return Err("cooked UE4 material source exceeds shader link scanner bound".into());
    }
    let mut by_hash=HashMap::with_capacity(library.records.len());
    for (ordinal,shader) in library.records.iter().enumerate(){
        if by_hash.insert(shader.hash,ordinal).is_some(){
            return Err(format!("duplicate source shader code hash at ordinal {ordinal}"));
        }
    }
    let mut result=ShaderHashCensus::default();
    let mut unique=BTreeSet::new();
    if source.len()<20{return Ok(result);}
    for source_byte_offset in 0..=source.len()-20{
        let mut key=[0u8;20];
        key.copy_from_slice(&source[source_byte_offset..source_byte_offset+20]);
        let Some(&library_ordinal)=by_hash.get(&key) else{continue};
        let shader_frequency=library.records[library_ordinal].frequency;
        if shader_frequency as usize>=result.references_per_frequency.len(){
            return Err(format!("source shader #{library_ordinal} has invalid frequency {shader_frequency}"));
        }
        if result.references.len()>=MAX_REFERENCES{
            return Err("original cooked UE4 material has excessive shader identity occurrences".into());
        }
        unique.insert(library_ordinal);
        result.references_per_frequency[shader_frequency as usize]+=1;
        result.references.push(SourceShaderHashReference{
            source_byte_offset,library_ordinal,shader_frequency,
            source_shader_hash:key,
        });
    }
    result.unique_library_shaders=unique.len();
    Ok(result)
}

#[cfg(test)]
mod tests{
    use super::*;
    use crate::shader_archive::ShaderCodeRecord;
    fn fixture()->ShaderArchiveIndex{
        ShaderArchiveIndex{
            version:1,archive_bytes:123,code_start:82,
            records:vec![
                ShaderCodeRecord{hash:[0xA1;20],code_offset:0,
                    compressed_bytes:12,uncompressed_bytes:30,frequency:0},
                ShaderCodeRecord{hash:[0xB2;20],code_offset:12,
                    compressed_bytes:29,uncompressed_bytes:70,frequency:3},
            ],
        }
    }
    #[test]
    fn exact_repeated_binary_source_hashes_have_offsets_and_stages(){
        let lib=fixture();
        let mut cooked=vec![0xCC;20];
        cooked.extend_from_slice(&[0xA1;20]);
        cooked.extend_from_slice(&[0xEE;5]);
        cooked.extend_from_slice(&[0xB2;20]);
        cooked.extend_from_slice(&[0xA1;20]);
        let output=match_material_shader_hashes(&lib,&cooked).unwrap();
        assert_eq!(output.references.len(),3);
        assert_eq!(output.unique_library_shaders,2);
        assert_eq!(output.references_per_frequency,[2,0,0,1,0,0]);
        assert_eq!(output.source_offsets_by_shader()[&0],[20,65]);
        assert_eq!(output.source_offsets_by_shader()[&1],[45]);
    }
    #[test]
    fn no_filename_or_shader_id_guessing(){
        let lib=fixture();
        assert_eq!(match_material_shader_hashes(&lib,b"BiomeColormap ForestFloor_D").unwrap().references.len(),0);
        assert!(match_material_shader_hashes(&lib,&[0xCC;19]).unwrap().references.is_empty());
    }
    #[test]
    fn reject_duplicate_library_hash_identity(){
        let mut lib=fixture();
        lib.records[1].hash=lib.records[0].hash;
        assert!(match_material_shader_hashes(&lib,&[0xA1;20]).is_err());
    }
}
