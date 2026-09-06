#!/usr/bin/env python3
"""Canonical Destiny 1 stage-part dye selector semantics.

The D1 render-mesh stage part serializes GearDyeChangeColorIndex as a byte at
+0x1E.  Bungie's archived web renderer maps that byte as follows:

    0 -> gear dye slot 0, primary color
    1 -> gear dye slot 0, secondary color
    2 -> gear dye slot 1, primary color
    3 -> gear dye slot 1, secondary color
    4 -> gear dye slot 2, primary color
    5 -> gear dye slot 2, secondary color
    6 -> gear dye slot 3, investment decal path
    7 -> gear dye slot 3, investment decal path

For D1 armor, the independently verified dye-channel table maps gear dye slots
0/1/2 to ArmorPlate / ArmorCloth / ArmorSuit respectively.

This module deliberately keeps the serialized selector byte separate from the
semantic label so asset extraction can remain lossless and fail closed.
"""
from __future__ import annotations

ARMOR_SLOT_NAMES = {
    0: "ArmorPlate",
    1: "ArmorCloth",
    2: "ArmorSuit",
}


def decode_gear_dye_change_color_index(index: int) -> dict:
    """Decode one D1 GearDyeChangeColorIndex without guessing unsupported values."""
    if not isinstance(index, int):
        raise TypeError(f"gear dye change color index must be int, got {type(index).__name__}")
    if index < 0 or index > 7:
        raise ValueError(f"unsupported D1 gear dye change color index {index}")

    if index <= 5:
        slot = index // 2
        use_primary = (index & 1) == 0
        channel_name = ARMOR_SLOT_NAMES.get(slot)
        return {
            "change_color_index": index,
            "gear_dye_slot": slot,
            "use_primary_color": use_primary,
            "use_secondary_color": not use_primary,
            "use_investment_decal": False,
            "armor_channel_name": channel_name,
            "color_role": "primary" if use_primary else "secondary",
        }

    return {
        "change_color_index": index,
        "gear_dye_slot": 3,
        "use_primary_color": True,
        "use_secondary_color": False,
        "use_investment_decal": True,
        "armor_channel_name": None,
        "color_role": "investment_decal",
    }


if __name__ == "__main__":
    import json
    print(json.dumps([decode_gear_dye_change_color_index(i) for i in range(8)], indent=2))
