#!/usr/bin/env python3
"""Registration/trigger sentinel for the Crota R4 Blender export workflow.

The production logic lives in the source-closed exporter/adapters.  This file exists
only so a no-semantic-change commit can trigger the already-registered workflow after
a decoder correction without perturbing evidence code.
"""
print('D1_CROTA_R4_TRIGGER_EXACT_ROI_VERTEX_PAIR_V2')
