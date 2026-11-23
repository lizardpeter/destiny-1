
undefined8 FUN_00bb1d30(undefined8 param_1,undefined8 param_2)

{
  undefined8 *puVar1;
  char cVar2;
  int iVar3;
  long lVar4;
  undefined8 uVar5;
  undefined1 uVar6;
  long local_180;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar2 = FUN_00906f70();
  uVar6 = 0;
  if (cVar2 == '\0') {
    local_180 = 0;
    FUN_00300b00(0x14,0x750,&local_180);
    if (local_180 == 0) {
      cVar2 = FUN_000e4d70(0x10,4);
      if (cVar2 != '\0') {
        if (DAT_028a6438 == '\0') {
          iVar3 = thunk_FUN_012aa7d6(&DAT_028a6438);
          if (iVar3 != 0) {
            DAT_028a6430 = FUN_000e4a10(s_networking_simulation_queue_simu_01697e46);
            thunk_FUN_012aa7e6(&DAT_028a6438);
          }
        }
        uVar6 = 0;
        FUN_01008290(local_178,s_networking_simulation_queue_simu_01697e46);
        FUN_000e4aa0(DAT_028a6430,local_178);
      }
    }
    else {
      puVar1 = *(undefined8 **)(local_180 + 8);
      lVar4 = FUN_00b9f390();
      *puVar1 = param_1;
      thunk_FUN_012aa986(puVar1 + 1,0,0x140);
      thunk_FUN_012aa7c6(puVar1 + 0x29,param_2,0x605);
      FUN_00300b90(local_180);
      uVar6 = 1;
      if (lVar4 != 0) {
        FUN_00bb7550(lVar4,1);
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar6);
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

