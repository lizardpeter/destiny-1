#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_windows_foundation.py PATH_TO_FALKORDB")

root = Path(sys.argv[1]).resolve()

def patch_module_init():
    p = root / "src/module_init.rs"
    s = p.read_text(encoding="utf-8")

    old = '''unsafe extern "C" {
    fn pthread_atfork(
        prepare: Option<unsafe extern "C" fn()>,
        parent: Option<unsafe extern "C" fn()>,
        child: Option<unsafe extern "C" fn()>,
    ) -> c_int;
}'''
    new = '''#[cfg(unix)]
unsafe extern "C" {
    fn pthread_atfork(
        prepare: Option<unsafe extern "C" fn()>,
        parent: Option<unsafe extern "C" fn()>,
        child: Option<unsafe extern "C" fn()>,
    ) -> c_int;
}'''
    if old in s and new not in s:
        s = s.replace(old, new, 1)

    old_call = '''        pthread_atfork(
            Some(crate::redis_type::pre_fork_prepare),
            None,
            Some(on_fork_child),
        );'''
    new_call = '''        #[cfg(unix)]
        pthread_atfork(
            Some(crate::redis_type::pre_fork_prepare),
            None,
            Some(on_fork_child),
        );'''
    if old_call in s and new_call not in s:
        s = s.replace(old_call, new_call, 1)

    p.write_text(s, encoding="utf-8")

def patch_graph_build():
    p = root / "graph/build.rs"
    s = p.read_text(encoding="utf-8")

    old = '        std::os::unix::fs::symlink(src, &main_a).expect("failed to create libredisearch.a symlink");'
    new = '        create_archive_alias(&src, &main_a).expect("failed to create libredisearch.a alias");'
    if old in s:
        s = s.replace(old, new, 1)

    marker = "/// RediSearch's Rust archive carries a second copy of the `redis-module` crate"
    helper = '''
#[cfg(unix)]
fn create_archive_alias(src: &std::path::Path, dst: &std::path::Path) -> std::io::Result<()> {
    std::os::unix::fs::symlink(src, dst)
}

#[cfg(windows)]
fn create_archive_alias(src: &std::path::Path, dst: &std::path::Path) -> std::io::Result<()> {
    std::fs::copy(src, dst).map(|_| ())
}

'''
    if "fn create_archive_alias" not in s:
        idx = s.find(marker)
        if idx < 0:
            raise RuntimeError("graph/build.rs: helper insertion marker not found")
        s = s[:idx] + helper + s[idx:]

    rs_marker = "    // ---- RediSearch 8.6, embedded as a static library ----"
    skip = '''    // Native Windows bring-up: non-index smoke tests link a fail-closed
    // compatibility archive instead of the real RediSearch backend. Every
    // symbol in that archive aborts if called, so an accidental index path can
    // never silently return incorrect data.
    println!("cargo:rerun-if-env-changed=FALKORDB_NATIVE_REDISEARCH_SHIM_DIR");
    if let Ok(dir) = std::env::var("FALKORDB_NATIVE_REDISEARCH_SHIM_DIR") {
        println!("cargo:rustc-link-search=native={dir}");
        println!("cargo:rustc-link-lib=static=redisearch_shim");
        println!("cargo:warning=native bring-up: RediSearch index operations are disabled");
        return;
    }

    // Type-check-only fallback. This intentionally emits no RediSearch library.
    println!("cargo:rerun-if-env-changed=FALKORDB_SKIP_REDISEARCH");
    if std::env::var_os("FALKORDB_SKIP_REDISEARCH").is_some() {
        println!("cargo:warning=FALKORDB_SKIP_REDISEARCH set: skipping RediSearch link discovery");
        return;
    }

'''
    if "FALKORDB_NATIVE_REDISEARCH_SHIM_DIR" not in s:
        idx = s.find(rs_marker)
        if idx < 0:
            raise RuntimeError("graph/build.rs: RediSearch marker not found")
        s = s[:idx] + skip + s[idx:]

    old_lagraph = '''    let lagraph_dir = std::path::Path::new(&manifest_dir).join("../lagraph_lib");
    println!("cargo:rustc-link-search=native={}", lagraph_dir.display());
    println!("cargo:rustc-link-search=native=/data/lagraph_lib");'''
    new_lagraph = '''    let lagraph_dir = std::env::var("LAGRAPH_LIB_DIR")
        .map(std::path::PathBuf::from)
        .unwrap_or_else(|_| std::path::Path::new(&manifest_dir).join("../lagraph_lib"));
    println!("cargo:rerun-if-env-changed=LAGRAPH_LIB_DIR");
    println!("cargo:rustc-link-search=native={}", lagraph_dir.display());
    #[cfg(not(windows))]
    println!("cargo:rustc-link-search=native=/data/lagraph_lib");'''
    if old_lagraph in s:
        s = s.replace(old_lagraph, new_lagraph, 1)

    old_omp = '''    if libomp_static {
        println!("cargo:rustc-link-lib=static=omp");
    } else {
        println!("cargo:rustc-link-lib=omp");
    }'''
    new_omp = '''    println!("cargo:rerun-if-env-changed=FALKORDB_NATIVE_NO_OPENMP");
    if std::env::var_os("FALKORDB_NATIVE_NO_OPENMP").is_none() {
        if libomp_static {
            println!("cargo:rustc-link-lib=static=omp");
        } else {
            #[cfg(windows)]
            {
                let name = std::env::var("OPENMP_LIB_NAME")
                    .unwrap_or_else(|_| "libomp".to_string());
                println!("cargo:rerun-if-env-changed=OPENMP_LIB_NAME");
                println!("cargo:rustc-link-lib={name}");
            }
            #[cfg(not(windows))]
            println!("cargo:rustc-link-lib=omp");
        }
    }'''
    if old_omp in s:
        s = s.replace(old_omp, new_omp, 1)

    p.write_text(s, encoding="utf-8")

patch_module_init()
patch_graph_build()
print("Windows foundation patches applied")
