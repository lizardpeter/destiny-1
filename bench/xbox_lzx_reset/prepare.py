#!/usr/bin/env python3
"""Build an isolated, exact 0.2.7 LZXD fork with a reusing reset."""
from pathlib import Path
import shutil

here = Path(__file__).resolve().parent
candidates = list(Path.home().glob(".cargo/registry/src/*/lzxd-0.2.7"))
if len(candidates) != 1:
    raise SystemExit(f"expected one lzxd-0.2.7 crate, got {candidates!r}")
origin = candidates[0]
target = here / "vendor" / "lzxd_fast"
if target.exists():
    shutil.rmtree(target)
shutil.copytree(origin, target)
# Keep exact upstream package metadata; Cargo aliases this path dependency
# as lzxd_fast. No need to edit its version or normalized manifest.

def patch(file, needle, replacement):
    p = target / file
    text = p.read_text(encoding="utf-8")
    assert text.count(needle) == 1, f"upstream changed {file}, count={text.count(needle)}"
    p.write_text(text.replace(needle, replacement), encoding="utf-8")

patch("src/window.rs", "impl Window {", """impl Window {
    // Preserve allocation but fully clear the 32-KiB history between
    // independent Xbox Avatar framed records. Semantically matches new().
    pub(crate) fn reset_reuse(&mut self) {
        self.pos = 0;
        self.buffer.fill(0);
    }
""")
patch("src/tree.rs", "impl CanonicalTree {", """impl CanonicalTree {
    pub(crate) fn reset_reuse(&mut self) {
        self.path_lengths.fill(0);
    }
""")
needle = """    pub fn reset(&mut self) {
        let this = Self::new(self.state.window_size);
        let _ = mem::replace(self, this);
    }"""
replacement=needle+"""

    /// Reset all decoding state without releasing the history window
    /// or canonical Huffman path-length buffers. Every bit of state is
    /// initialized identically to Self::new(window_size).
    pub fn reset_reuse(&mut self) {
        self.window.reset_reuse();
        self.state.main_tree.reset_reuse();
        self.state.length_tree.reset_reuse();
        self.r = [1, 1, 1];
        self.chunk_offset = 0;
        self.first_chunk_read = false;
        self.postprocess = None;
        self.current_block = Block {
            remaining: 0,
            size: 0,
            kind: BlockKind::Uncompressed { r: [1, 1, 1] },
        };
    }"""
patch("src/lib.rs", needle, replacement)
print(f"VENDORED exact lzxd 0.2.7 from {origin}; patched {target}")
