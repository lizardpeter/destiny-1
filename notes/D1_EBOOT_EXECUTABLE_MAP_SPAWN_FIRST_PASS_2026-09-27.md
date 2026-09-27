# Destiny 1 PS4 eboot first-pass executable map and spawn evidence (2026-09-27)

## Input identity

- User-provided `eboot.bin`; SHA-256 `672f03411c0503dfbcda804cbb9fb27cdd9a8d73a8bcb71bf0c4f688073b0833`; 29,249,016 bytes.
- ELF64 little-endian x86-64, FreeBSD/Orbis ABI, type `0xFE10`, entry virtual address `0xC2E200`; ten program headers and no section headers.
- First executable LOAD has file offset `0x4000`, virtual address zero, size `0x18D4394`. Entry bytes at file offset `0xC32200` disassemble as ordinary x86-64 instructions. This establishes accessible code bytes in this file; it does not by itself establish the exact retail patch/build or a complete decrypted dependency set.
- Strings include `CUSA00219_00`, activity and world-controller diagnostics, spawn and bubble systems. The path from which the user obtained the file reportedly refers to CUSA00219 01.33, but that version is not independently proven by the ELF fields inspected here.

## Exact first-pass string references

For addresses within executable LOAD, file offset = virtual address + `0x4000`. The listed references are RIP-relative LEA matches validated by disassembly:

| String | File offset | LEA file offset | Observation |
| --- | ---: | ---: | --- |
| `spawn point globals` | `0x161B968` | `0x135B23` | Constructor passes name to registration call at `0x242010`, allocates `0x7030` bytes. This is registry setup, not a spawn selector. |
| `activity loader` | `0x162F2CF` | `0x3449F3` | Constructor passes name to same registration call and allocates `0x3DC` bytes. |
| `Change world (activity_name='%s', symbol='%s', rebuild_omaha_options='%s', random_seed='%c 0x%08X').` | `0x164E4A5` | `0x75975A` | World transition diagnostic reference. |
| `Change slice-set (slice-set='%d', spawn='%s').` | `0x164E521` | `0x758BF2` | Diagnostic formatter call at file `0x758BE0`; spawn identifier is an explicit argument. |
| `payload spawn identifier unavailable in this build` | `0x164E550` | `0x758BF9` | Same formatter uses this fallback string. The caller and the source of the identifier still need proof. |
| `activities:spawn_volumes: fp_ref list overflow in activity 0x%08X` | `0x161CD82` | `0x17A6D4`, `0x17A6FF` | Runtime diagnostic in spawn-volume path, not a decoded asset schema. |

The executable exposes distinct Activity, slice-set, bubble, spawn-point, and spawn-volume machinery. A static D912 location group is not enough to select a live NPC or a player spawn. The next reverse pass should trace the call chain feeding the slice-set/spawn identifier and relate it to serialized source records. No arbitrary D912 group or map-origin spawn is promoted to retail runtime behavior by this first pass.

## Reproduction

```sh
sha256sum eboot.bin
readelf -h -l eboot.bin
objdump -D -b binary -m i386:x86-64 --start-address=0x758be0 --stop-address=0x758c12 eboot.bin
```
