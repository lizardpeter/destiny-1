
void FUN_00ae2900(void)

{
  undefined8 *puVar1;
  long lVar2;
  undefined8 uVar3;
  undefined4 uVar4;
  
  FUN_00aeb030();
  FUN_00af1b70();
  FUN_00ada8a0(0);
  FUN_001db380();
  FUN_00ae9e60();
  FUN_002b14f0();
  uVar4 = 0xffffffff;
  if (DAT_0196b008 != (undefined4 *)0x0) {
    uVar4 = *DAT_0196b008;
  }
  FUN_0023e010(&DAT_027be860,s__network_globals_async_cache_0167d28f + 1,0x24,4,uVar4,2,3,0x19,
               thunk_FUN_001681a0);
  puVar1 = DAT_027be860;
  *(undefined4 *)(DAT_027be860 + 4) = 0;
  puVar1[3] = 0;
  puVar1[2] = 0;
  puVar1[1] = 0;
  *puVar1 = 0;
  if (puVar1 != (undefined8 *)0x0) {
    *(undefined4 *)(puVar1 + 4) = 0;
    puVar1[3] = 0;
    puVar1[2] = 0;
    puVar1[1] = 0;
    *puVar1 = 0;
  }
  uVar4 = 0xffffffff;
  if (DAT_0196aff8 != (undefined4 *)0x0) {
    uVar4 = *DAT_0196aff8;
  }
  FUN_0023e010(&DAT_027be868,s_network_private_globals_0167d2ac,0x101,4,uVar4,2,3,0x19,
               thunk_FUN_001681a0);
  lVar2 = DAT_027be868;
  thunk_FUN_012aa986(DAT_027be868,0,0x101);
  if (lVar2 != 0) {
    thunk_FUN_012aa986(lVar2,0,0x101);
  }
  uVar3 = FUN_005979a0();
  FUN_00597a10(uVar3);
  FUN_00b9bdb0();
  FUN_002dfce0();
  return;
}

