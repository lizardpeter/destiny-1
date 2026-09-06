#!/usr/bin/env python3
"""Canonical Destiny 1 armor dye-channel semantics.

The channel *indices and hashes* are retail data.  The semantic names below are
kept separate because one historical Charm dictionary swaps the two non-plate
armor names.

Independent consistency evidence:

* retail Spektar equipping blocks pair channel 1 with dye 8753 and channel 2
  with dye 8754;
* the exact SDye_D1 records serialize SlotTypeIndex 1 for 8753 and 2 for 8754;
* Charm's own DyeSlot enum is Armor=0, Cloth=1, Suit=2;
* SolUnshadowed/tgxm-loader maps 1367384683 -> ArmorCloth and
  218592586 -> ArmorSuit;
* Destiny-Collada-Generator independently uses the same two mappings.

Therefore the canonical armor mapping is 0 Plate, 1 Cloth, 2 Suit.
"""

D1_DYE_CHANNEL_NAMES = {
    662199250: "ArmorPlate",       # 0x27785BD2
    1367384683: "ArmorCloth",     # 0x5180A26B
    218592586: "ArmorSuit",       # 0x0D07754A
    1667433279: "Weapon1",
    1667433278: "Weapon2",
    1667433277: "Weapon3",
    3073305669: "ShipUpper",
    3073305668: "ShipDecals",
    3073305671: "ShipLower",
    1971582085: "SparrowUpper",
    1971582084: "SparrowEngine",
    1971582087: "SparrowLower",
    373026848: "GhostMain",
    373026849: "GhostHighlights",
    373026850: "GhostDecals",
}

D1_ARMOR_CHANNELS = {
    0: {"hash_u32": 662199250, "hash": "27785BD2", "name": "ArmorPlate"},
    1: {"hash_u32": 1367384683, "hash": "5180A26B", "name": "ArmorCloth"},
    2: {"hash_u32": 218592586, "hash": "0D07754A", "name": "ArmorSuit"},
}
