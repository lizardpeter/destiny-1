
void FUN_0091adb0(void)

{
  long lVar1;
  undefined8 *puVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  uVar3 = 0xffffffff;
  uVar4 = 0xffffffff;
  if (DAT_0194b538 != (undefined4 *)0x0) {
    uVar4 = *DAT_0194b538;
  }
  FUN_0023e010(&DAT_0273eb28,s_player_control_globals_0166b7cc,0x290,4,uVar4,7,3,0x17,
               thunk_FUN_001681a0);
  if (DAT_0194b528 != (undefined4 *)0x0) {
    uVar3 = *DAT_0194b528;
  }
  FUN_0023e010(&DAT_0273eb30,s_player_control_globals_determini_0166b7e3,0x50,4,uVar3,7,0,0x17,
               thunk_FUN_001681a0);
  lVar1 = DAT_0273eb28;
  thunk_FUN_012aa986(DAT_0273eb28,0,0x290);
  puVar2 = DAT_0273eb30;
  DAT_0273eb30[9] = 0;
  puVar2[8] = 0;
  puVar2[7] = 0;
  puVar2[6] = 0;
  puVar2[5] = 0;
  puVar2[4] = 0;
  puVar2[3] = 0;
  puVar2[2] = 0;
  puVar2[1] = 0;
  *puVar2 = 0;
  *(undefined1 *)(lVar1 + 0x28b) = 0;
  lVar1 = DAT_0273eb28;
  *(undefined4 *)(DAT_0273eb28 + 0x14) = 0x3f800000;
  *(undefined4 *)(lVar1 + 0x18) = 0x3f800000;
  return;
}

