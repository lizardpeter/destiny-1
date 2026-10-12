#!/usr/bin/env python3
"""Generate the Destiny 1 source-reconstruction skeleton from the retail eboot.

Mirrors the original Bungie source layout recovered from CUSA00219 01.33
(`d:\\bungie\\evil\\shared\\engine\\source\\...`) as `reconstruction/`, one folder
per subsystem, each with a README listing:

  * verbatim source paths proven by strings in the binary (CONFIRMED_BINARY),
  * every C++ class whose RTTI is assigned to that subsystem, with typeinfo,
    vtable, virtual-slot count and base classes (CONFIRMED_BINARY for the class
    data; folder placement of first-party classes is HYPOTHESIS),
  * decompiled functions recorded in `reconstruction/functions.json`.

The skeleton is regenerated in place. Hand-written content is preserved: only
the block between the GENERATED markers in each README is rewritten, and
reconstructed `.cpp/.h` files are never touched.

usage: d1_reconstruction_tree.py EBOOT [--root reconstruction]
"""
import argparse, hashlib, json, os, re, struct, subprocess, collections

SHA256 = "672f03411c0503dfbcda804cbb9fb27cdd9a8d73a8bcb71bf0c4f688073b0833"
BEGIN, END = "<!-- GENERATED: d1_reconstruction_tree.py -->", "<!-- /GENERATED -->"

# ---------------------------------------------------------------- subsystems
# key -> (relative dir, path evidence, role)
V, H = "CONFIRMED_BINARY", "HYPOTHESIS"
SUBSYSTEMS = {
    "engine": ("evil/shared/engine/source/engine", V, "Tiger engine core"),
    "engine.core": ("evil/shared/engine/source/engine/core", H, "allocators, containers, threading, crash reporting, input converters, character action_impl classes"),
    "engine.graphics": ("evil/shared/engine/source/engine/graphics", V, "renderer; mostly non-virtual, so nearly invisible to RTTI (seen via heaps 'Render Prepare/Submit * State', 'GPU Main Resources'); TFX VM and render context live here"),
    "engine.graphics.cloth": ("evil/shared/engine/source/engine/graphics/features/cloth", V, "Havok Cloth integration"),
    "engine.graphics.cloth.physicsbridge": ("evil/shared/engine/source/engine/graphics/features/cloth/physicsbridge/physicsclothworld", V, "cloth <-> physics world bridge"),
    "engine.physics": ("evil/shared/engine/source/engine/physics", H, "Havok physics bridge, physics components and collectors"),
    "engine.audio": ("evil/shared/engine/source/engine/audio", H, "tiger_audio / tiger_dialog, CRI and Wwise glue"),
    "engine.resourcerer": ("evil/shared/engine/source/engine/resourcerer", H, "resource loading, contexts, defrag (log 'resourcerer:*')"),
    "engine.ui": ("evil/shared/engine/source/engine/ui", H, "ui:: core containers and properties"),
    "engine.ui.cui": ("evil/shared/engine/source/engine/ui/cui", H, "cui:: screens, widgets, event-handler components"),
    "omaha": ("evil/shared/engine/source/omaha", V, "game framework layer hosting the engine via *_engine_shim classes"),
    "omaha.main": ("evil/shared/engine/source/omaha/main", V, "entry point and world-controller shim"),
    "omaha.game": ("evil/shared/engine/source/omaha/game", V, "game / game_engine; *_game_system classes derive from c_game_system_interface"),
    "omaha.networking": ("evil/shared/engine/source/omaha/networking", V, "sessions, channels, STUN, DemonWare, signon (log 'networking:*')"),
    "omaha.networking.delivery": ("evil/shared/engine/source/omaha/networking/delivery", V, "network_link"),
    "omaha.networking.bap": ("evil/shared/engine/source/omaha/networking/bap", H, "BAP connection/message queues, investment BAP messages"),
    "omaha.world_controller": ("evil/shared/engine/source/omaha/world_controller", H, "activity/state/slice_set/matchmaking managers, bootflow (log 'world_controller:*')"),
    "omaha.simulation": ("evil/shared/engine/source/omaha/simulation", H, "simulation queue, replication, determinism"),
    "omaha.incidents": ("evil/shared/engine/source/omaha/incidents", H, "incident metadata, announcement, heat"),
    "omaha.objects": ("evil/shared/engine/source/omaha/objects", H, "object components, players, weapons, vehicles, perks"),
    "omaha.ai": ("evil/shared/engine/source/omaha/ai", H, "actors, perception, path finding"),
    "omaha.camera": ("evil/shared/engine/source/omaha/camera", H, "cameras, director, cinematics, observer"),
    "omaha.platform": ("evil/shared/engine/source/omaha/platform", H, "orbis/NP platform services, DLC, SKU, trophies"),
    "spasaha": ("evil/shared/engine/source/spasaha", V, "Destiny-specific game layer; Jam target engine_source_spasaha_spasaha -> tiger_release_final.elf"),
    "spasaha.spasahalib": ("evil/shared/engine/source/spasaha/spasahalib", V, "Destiny game library"),
    "spasaha.spasahalib.profile": ("evil/shared/engine/source/spasaha/spasahalib/profile", V, "achievements"),
    "spasaha.investment": ("evil/shared/engine/source/spasaha/investment", H, "items, vendors, talent grids, rewards"),
    "spasaha.xetrov": ("evil/shared/engine/source/spasaha/xetrov", H, "xetrov client/engine shim and message queue"),
    "tp.havok": ("external_libraries/havok", V, "Havok 2012.2.0 Physics + Cloth (d:\\bungie\\external_libraries\\havok\\2012-2-0_8)"),
    "tp.demonware": ("external_libraries/demonware", V, "DemonWare 48 (D:\\bungie\\external_libraries\\DemonWare\\48)"),
    "tp.libtomcrypt": ("external_libraries/libtom", V, "libtomcrypt 1.2 (C:\\bungie\\external_libraries\\libtom\\v1.2)"),
    "tp.oodle": ("external_libraries/oodle", V, "RAD Oodle (v:\\devel\\projects\\oodle)"),
    "tp.criware": ("external_libraries/criware", H, "CRIWARE / CRI Mana (RTTI only)"),
    "tp.wwise": ("external_libraries/wwise", H, "Audiokinetic Wwise (RTTI only)"),
    "tp.speedtree": ("external_libraries/speedtree", H, "SpeedTree (RTTI only)"),
    "tp.freetype": ("external_libraries/freetype", H, "FreeType (RTTI only)"),
    "tp.sce_np_toolkit": ("external_libraries/sce_np_toolkit", H, "Sony NP Toolkit, sce::Toolkit::NP (RTTI only)"),
}

# First-party class -> subsystem: ordered name-token rules (first match wins).
RULES = [
    ("engine.ui.cui", lambda b, n: b.startswith("cui::") or "cui" in n.split("_")),
    ("engine.ui", lambda b, n: b.startswith("ui::")),
    ("spasaha", lambda b, n: "spasaha" in n),
    ("spasaha.xetrov", lambda b, n: "xetrov" in n),
    ("omaha.networking.bap", lambda b, n: "_bap" in n or n.startswith("c_bap")),
    ("spasaha.investment", lambda b, n: "investment" in n),
    ("omaha.incidents", lambda b, n: "incident" in n),
    ("engine.ui.cui", lambda b, n: "thud" in n or "_hud" in n),
    ("omaha.world_controller", lambda b, n: any(t in n for t in ("world_controller", "activity", "bootflow", "slice_set", "matchmaking", "orbit", "ui_stage"))),
    ("omaha.simulation", lambda b, n: "simulation" in n or "determinism" in n),
    ("omaha.networking", lambda b, n: any(t in n for t in ("network", "session", "channel", "stun", "demonware", "transport", "relay", "connection", "online", "leaderboard", "signon", "presence", "webstats", "http"))),
    ("omaha.platform", lambda b, n: any(t in n for t in ("orbis", "platform", "_np_", "trophy", "entitlement", "sku", "dlc", "psn"))),
    ("engine.physics", lambda b, n: any(t in n for t in ("physics", "havok", "cloth", "collector", "volume", "contact", "raycast", "shape", "phantom"))),
    ("omaha.ai", lambda b, n: any(t in n for t in ("ai_", "actor", "perception", "path_finding", "firing_point", "_ai"))),
    ("omaha.camera", lambda b, n: any(t in n for t in ("camera", "director", "cinematic", "observer"))),
    ("engine.audio", lambda b, n: any(t in n for t in ("audio", "dialog", "sound", "cri_", "music", "voice"))),
    ("omaha.objects", lambda b, n: any(t in n for t in ("component", "object", "entity", "device", "projectile", "weapon", "vehicle", "character", "player", "perk", "ability", "gear", "loot", "item", "spawn", "trigger", "teleport", "interact", "targetable"))),
    ("omaha.game", lambda b, n: n.endswith("game_system") or "globals" in n or "game_engine" in n or "game_state" in n),
    ("engine.graphics", lambda b, n: any(t in n for t in ("render", "graphics", "material", "particle", "light", "shader", "texture", "surface", "video", "bitmap", "effect", "decorator", "speedtree", "time_of_day", "sun_", "atmosphere", "fog", "exposure", "sky"))),
    ("engine.resourcerer", lambda b, n: any(t in n for t in ("resource", "allocator", "heap", "memory", "file", "loader", "stream", "pool", "cache"))),
    ("engine.core", lambda b, n: True),
]


def classify(name):
    base = name.split("<")[0]
    leaf, top = base.split("::")[-1], base.split("::")[0]
    if top == "sce":
        return "tp.sce_np_toolkit"
    if top == "AK" or leaf.startswith("IAk"):
        return "tp.wwise"
    if top == "SpeedTree":
        return "tp.speedtree"
    if leaf.startswith("FT_"):
        return "tp.freetype"
    if top == "font":
        return "engine.ui"
    if re.match(r"(hk|hcl)", leaf) or re.match(r"(hk|hcl)", top):
        return "tp.havok"
    if re.match(r"bd[A-Z]", leaf) or re.match(r"bd[A-Z]", top):
        return "tp.demonware"
    if leaf.startswith("Cri") or top.startswith("Cri"):
        return "tp.criware"
    if top == "(anonymous namespace)" and not re.match(r"[cseki]_", leaf):
        return "engine.core"
    if re.match(r"[cseki]_", leaf) or top in ("cui", "ui"):
        for key, rule in RULES:
            if rule(base, leaf):
                return key
    return None


# ---------------------------------------------------------------- ELF / RTTI
TI_IMPORTS = {"pZ9WXcClPO8#w#r": "si", "byV+FWlAnB4#w#r": "class", "9ByRMdo7ywg#w#r": "vmi"}


class Image:
    """Relocated flat image of the SCE ELF at base 0 (SCE dynamic relocations applied)."""

    def __init__(self, path):
        d = open(path, "rb").read()
        if hashlib.sha256(d).hexdigest() != SHA256:
            raise SystemExit("unexpected eboot SHA-256 (expected CUSA00219 01.33)")
        phoff, = struct.unpack_from("<Q", d, 0x20)
        phnum, = struct.unpack_from("<H", d, 0x38)
        loads, dyn, dlib = [], None, None
        for i in range(phnum):
            t, f, off, va, pa, fs, ms, al = struct.unpack_from("<IIQQQQQQ", d, phoff + i * 56)
            if t == 1:
                loads.append((va, off, fs, ms))
            elif t == 2:
                dyn = (off, fs)
            elif t == 0x61000000:
                dlib = off
        self.mem = bytearray(max(va + ms for va, off, fs, ms in loads))
        for va, off, fs, ms in loads:
            self.mem[va:va + fs] = d[off:off + fs]
        self.text_end = loads[0][0] + loads[0][3]
        tags = {}
        for i in range(0, dyn[1], 16):
            tag, val = struct.unpack_from("<qQ", d, dyn[0] + i)
            tags.setdefault(tag, val)
        symoff, symsz, stroff = dlib + tags[0x61000039], tags[0x6100003F], dlib + tags[0x61000035]
        syms = []
        for i in range(0, symsz, 24):
            nm, info, oth, shn, val, sz = struct.unpack_from("<IBBHQQ", d, symoff + i)
            syms.append((d[stroff + nm:d.index(b"\0", stroff + nm)].decode("latin1"), val))
        self.imports = {}
        for start, size in ((tags[0x6100002F], tags[0x61000031]), (tags[0x61000029], tags[0x6100002D])):
            for i in range(0, size, 24):
                off, info, add = struct.unpack_from("<QQq", d, dlib + start + i)
                typ, si = info & 0xFFFFFFFF, info >> 32
                if typ == 8:
                    struct.pack_into("<Q", self.mem, off, add & (2**64 - 1))
                elif typ in (1, 6, 7):
                    name, value = syms[si]
                    if value:
                        struct.pack_into("<Q", self.mem, off, (value + add) & (2**64 - 1))
                    else:
                        self.imports[off] = name

    def q(self, va):
        return struct.unpack_from("<Q", self.mem, va)[0]

    def cstr(self, va):
        return bytes(self.mem[va:self.mem.index(b"\0", va)]).decode("latin1")


def recover_classes(im):
    """typeinfo objects are found through their imported vptr; vtables through `0, &typeinfo` pairs."""
    ti_kind = {va: TI_IMPORTS[s] for va, s in im.imports.items() if s in TI_IMPORTS}
    back = collections.defaultdict(list)
    for off in range(im.text_end & ~7, len(im.mem) - 8, 8):
        v = im.q(off)
        if v in ti_kind:
            back[v].append(off)
    classes = {}
    for ti, kind in ti_kind.items():
        try:
            mangled = im.cstr(im.q(ti + 8))
        except ValueError:
            continue
        if not re.fullmatch(r"[\w$:<>.,* ]+", mangled):
            continue
        vt = [o + 8 for o in back.get(ti, []) if o != ti and im.q(o - 8) == 0]
        bases = []
        if kind == "si":
            bases.append((im.q(ti + 16), 0, False))
        elif kind == "vmi":
            cnt, = struct.unpack_from("<I", im.mem, ti + 20)
            for i in range(min(cnt, 32)):
                of, = struct.unpack_from("<q", im.mem, ti + 32 + 16 * i)
                bases.append((im.q(ti + 24 + 16 * i), of >> 8, bool(of & 1)))
        classes[ti] = dict(mangled=mangled, kind=kind, vtables=sorted(vt), bases=bases)
    dem = subprocess.run(["c++filt"], input="\n".join("_ZTS" + c["mangled"] for c in classes.values()),
                         capture_output=True, text=True).stdout.split("\n")
    for c, n in zip(classes.values(), dem):
        c["name"] = n.replace("typeinfo name for ", "").strip() or c["mangled"]
    for c in classes.values():
        vt, slots = (c["vtables"][0] if c["vtables"] else None), None
        if vt:
            slots = 0
            while slots < 512 and (0 < im.q(vt + 8 * slots) < im.text_end or vt + 8 * slots in im.imports):
                slots += 1
        c["vtable"], c["slots"] = vt, slots
    return classes


def source_paths(im):
    text = bytes(im.mem)
    out = set()
    for m in re.finditer(rb"[A-Za-z]:[\\/][\x20-\x7e]{4,200}?\.(?:cpp|c|h|inl)(?=\x00)", text):
        out.add(m.group().decode())
    return out


def path_owner(p):
    low = p.lower().replace("/", "\\")
    if "\\bungie\\evil\\shared\\engine\\source\\" in low:
        rel = low.split("\\engine\\source\\", 1)[1].replace("\\", "/").rsplit("/", 1)[0]
        best = None
        for k, (d, ev, role) in SUBSYSTEMS.items():
            sub = d.split("engine/source/", 1)[-1]
            if rel == sub or rel.startswith(sub + "/"):
                if best is None or len(SUBSYSTEMS[best][0]) < len(d):
                    best = k
        return best
    for frag, k in (("havok", "tp.havok"), ("perforce\\clients\\tiger", "tp.havok"), ("demonware", "tp.demonware"),
                    ("libtom", "tp.libtomcrypt"), ("oodle", "tp.oodle")):
        if frag in low:
            return k
    return None


# ---------------------------------------------------------------- output
def md_table(rows, head):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(x).replace("|", "\\|") for x in r) + " |" for r in rows]
    return "\n".join(out)


def write_readme(path, title, body):
    old = open(path).read() if os.path.exists(path) else None
    gen = f"{BEGIN}\n{body}\n{END}"
    if old and BEGIN in old and END in old:
        text = old[:old.index(BEGIN)] + gen + old[old.index(END) + len(END):]
    else:
        text = f"# {title}\n\n{gen}\n\n## Notes\n\n_Hand-written findings for this folder go here; regeneration keeps everything outside the generated block._\n"
    open(path, "w").write(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("eboot")
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), "..", "..", "reconstruction"))
    a = ap.parse_args()
    root = os.path.normpath(a.root)
    im = Image(a.eboot)
    classes = recover_classes(im)
    paths = source_paths(im)
    fn_path = os.path.join(root, "functions.json")
    functions = json.load(open(fn_path)) if os.path.exists(fn_path) else []

    by_sub = collections.defaultdict(list)
    for ti, c in classes.items():
        k = classify(c["name"])
        if k:
            c["subsystem"] = k
            by_sub[k].append(ti)
    files_by_sub = collections.defaultdict(list)
    for p in sorted(paths, key=str.lower):
        k = path_owner(p)
        if k:
            files_by_sub[k].append(p)
    fn_by_sub = collections.defaultdict(list)
    for f in functions:
        fn_by_sub[f["subsystem"]].append(f)

    manifest = {"executable_sha256": SHA256, "build": "CUSA00219 01.33",
                "generator": "tools/eboot/d1_reconstruction_tree.py", "subsystems": {}}
    for key, (rel, ev, role) in SUBSYSTEMS.items():
        d = os.path.join(root, rel)
        os.makedirs(d, exist_ok=True)
        children = sorted(k for k in SUBSYSTEMS if k.startswith(key + ".") and k.count(".") == key.count(".") + 1)
        lines = [f"**Subsystem key:** `{key}`  ", f"**Folder path evidence:** `{ev}`" +
                 ("" if ev == V else " (folder name is a proposal from RTTI/log-channel clustering, not a recovered path)") + "  ",
                 f"**Role:** {role}", ""]
        if children:
            lines += ["## Sub-folders", ""] + [f"- [`{SUBSYSTEMS[k][0].rsplit('/', 1)[-1]}/`]({os.path.relpath(os.path.join(root, SUBSYSTEMS[k][0]), d)}/README.md) — {SUBSYSTEMS[k][2]}" for k in children] + [""]
        fl = files_by_sub.get(key, [])
        lines += ["## Source files named in the binary", ""]
        if fl and key.startswith("tp."):
            lines += [f"{len(fl)} verbatim path strings (`CONFIRMED_BINARY`). Third-party code is identified, not reconstructed.", ""] + [f"- `{p}`" for p in fl] + [""]
        elif fl:
            lines += ["Verbatim path strings (`CONFIRMED_BINARY`). Each has a placeholder file here to be filled in.", ""] + [f"- `{p}` → [`{p.replace(chr(92), '/').rsplit('/', 1)[-1]}`]({p.replace(chr(92), '/').rsplit('/', 1)[-1]}) — not yet reconstructed" for p in fl] + [""]
            for p in fl:
                fn = os.path.join(d, p.replace("\\", "/").rsplit("/", 1)[-1])
                if not os.path.exists(fn):
                    open(fn, "w").write(f"// {p}\n// Evidence: CONFIRMED_BINARY (verbatim path string in CUSA00219 01.33 eboot, sha256 {SHA256[:16]}...).\n// Reconstruction status: NOT STARTED.\n")
        else:
            lines += ["_None recovered (retail build stripped most asserts)._", ""]
        fns = fn_by_sub.get(key, [])
        lines += ["## Decompiled functions", ""]
        if fns:
            lines += [md_table([(f"`{f['va']}`", f["name"], f.get("class") or "", f["evidence"], f"[`{f['file']}`](decompiled/{f['file']})" if f.get("file") else "", f["role"]) for f in sorted(fns, key=lambda f: int(f["va"], 16))],
                               ["VA", "name", "class", "evidence", "pseudo-C", "role"]), ""]
        else:
            lines += ["_None yet._", ""]
        cl = sorted(by_sub.get(key, []), key=lambda t: classes[t]["name"])
        lines += [f"## Classes ({len(cl)})", ""]
        if cl:
            lines += ["Class data (name, typeinfo, vtable, bases) is `CONFIRMED_BINARY` from Itanium RTTI. "
                      + ("Placement in this folder follows the library prefix." if key.startswith("tp.") else "Placement in this folder is `HYPOTHESIS` (name-token rule)."), ""]
            rows = []
            for t in cl:
                c = classes[t]
                bases = ", ".join((classes[b]["name"] if b in classes else hex(b)) + (f" @+{o:#x}" if o else "") + (" (virtual)" if v else "") for b, o, v in c["bases"])
                rows.append((f"`{c['name']}`", f"`{t:#x}`", f"`{c['vtable']:#x}`" if c["vtable"] else "", c["slots"] if c["slots"] is not None else "", bases))
            lines += [md_table(rows, ["class", "typeinfo", "vtable", "virtual slots", "bases"]), ""]
        write_readme(os.path.join(d, "README.md"), rel.rsplit("/", 1)[-1] + "/", "\n".join(lines))
        manifest["subsystems"][key] = {"dir": rel, "path_evidence": ev, "role": role,
                                       "source_files": fl, "functions": [f["va"] for f in fns],
                                       "classes": [{"name": classes[t]["name"], "typeinfo": hex(t),
                                                    "rtti_kind": classes[t]["kind"],
                                                    "vtable": hex(classes[t]["vtable"]) if classes[t]["vtable"] else None,
                                                    "virtual_slots": classes[t]["slots"],
                                                    "bases": [{"typeinfo": hex(b), "offset": o, "virtual": v}
                                                              for b, o, v in classes[t]["bases"]]} for t in cl]}
    json.dump(manifest, open(os.path.join(root, "manifest.json"), "w"), indent=1)
    n_cls = sum(len(v) for v in by_sub.values())
    print(f"classes {len(classes)} (placed {n_cls}), source paths {len(paths)}, functions {len(functions)} -> {root}")


if __name__ == "__main__":
    main()
