
void FUN_00922cf0(void)

{
  undefined2 *puVar1;
  undefined8 *puVar2;
  undefined4 uVar3;
  
  uVar3 = 0xffffffff;
  if (DAT_0194b548 != (undefined4 *)0x0) {
    uVar3 = *DAT_0194b548;
  }
  FUN_0023e010(&DAT_0273eb80,s_player_mapping_globals_0166b808,0xdc,4,uVar3,7,3,0x17,
               thunk_FUN_001681a0);
  *DAT_0273eb80 = 0;
  DAT_0273eb80[1] = 0;
  *(undefined4 *)(DAT_0273eb80 + 2) = 0xffffffff;
  *(undefined4 *)(DAT_0273eb80 + 4) = 0xffffffff;
  puVar1 = DAT_0273eb80;
  *(undefined8 *)(DAT_0273eb80 + 10) = 0xffffffffffffffff;
  *(undefined8 *)(puVar1 + 6) = 0xffffffffffffffff;
  puVar1 = DAT_0273eb80;
  thunk_FUN_012aa986(DAT_0273eb80 + 0xe,0xff,0xa0);
  puVar1[0x5e] = 0;
  *(undefined4 *)(DAT_0273eb80 + 0x60) = 0xffffffff;
  *(undefined4 *)(DAT_0273eb80 + 0x62) = 0xffffffff;
  puVar1 = DAT_0273eb80;
  puVar2 = (undefined8 *)(DAT_0273eb80 + 100);
  *(undefined4 *)(DAT_0273eb80 + 0x6c) = 0;
  *(undefined8 *)(puVar1 + 0x68) = 0;
  *puVar2 = 0;
  FUN_008dd4e0();
  return;
}

