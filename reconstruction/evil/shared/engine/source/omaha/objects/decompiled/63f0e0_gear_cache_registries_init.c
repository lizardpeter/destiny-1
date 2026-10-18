
void FUN_0063f0e0(void)

{
  undefined4 *puVar1;
  
  FUN_0063b650(DAT_026bea78,s__player_gear_cache_registry_01643c2f + 1,0x13,8,1);
  FUN_0063b650(DAT_026bea80,s_weapon_gear_cache_registry_01643c4b,0x2a,8,2);
  FUN_0063b650(DAT_026bea88,s_ship_gear_cache_registry_01643c66,0x12,8,0);
  FUN_0063b650(DAT_026bea90,s_ghost_gear_cache_registry_01643c7f,0x12,8,0);
  FUN_0063b650(DAT_026bea98,s_vehicle_gear_cache_registry_01643c99,0x12,8,0);
  FUN_00641230(DAT_026beaa0,s_player_emote_registry_01643cb5,0x12,8);
  puVar1 = DAT_026bea70;
  *DAT_026bea70 = 0xffffffff;
  *(undefined1 *)(puVar1 + 1) = 0;
  *(undefined1 *)(puVar1 + 3) = 0;
  puVar1[2] = 0;
  puVar1[8] = 0;
  puVar1[9] = 0x12;
  puVar1[10] = 3;
  puVar1[0xb] = 0;
  *(undefined1 *)(puVar1 + 0xc) = 1;
  FUN_00070530(&DAT_026beab0,s_gear_component_registry_01643ccb,DAT_01942f40,8,4,0xffffffff,0x4f,8,0
               ,0xd,0);
  return;
}

