# engine/

<!-- GENERATED: d1_reconstruction_tree.py -->
**Subsystem key:** `engine`  
**Folder path evidence:** `CONFIRMED_BINARY`  
**Role:** Tiger engine core

## Sub-folders

- [`audio/`](audio/README.md) — tiger_audio / tiger_dialog, CRI and Wwise glue
- [`core/`](core/README.md) — allocators, containers, threading, crash reporting, input converters, character action_impl classes
- [`graphics/`](graphics/README.md) — renderer; mostly non-virtual, so nearly invisible to RTTI (seen via heaps 'Render Prepare/Submit * State', 'GPU Main Resources'); TFX VM and render context live here
- [`physics/`](physics/README.md) — Havok physics bridge, physics components and collectors
- [`resourcerer/`](resourcerer/README.md) — resource loading, contexts, defrag (log 'resourcerer:*')
- [`ui/`](ui/README.md) — ui:: core containers and properties

## Source files named in the binary

_None recovered (retail build stripped most asserts)._

## Decompiled functions

_None yet._

## Classes (0)

<!-- /GENERATED -->

## Notes

_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._
