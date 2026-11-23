
undefined8 * FUN_008da760(long param_1)

{
  long lVar1;
  long *plVar2;
  undefined8 *puVar3;
  undefined2 *local_40;
  long local_38;
  long local_30;
  
  plVar2 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  puVar3 = (undefined8 *)FUN_008d9820(&DAT_0273bf78,0x50,8);
  if (puVar3 != (undefined8 *)0x0) {
    *(undefined4 *)(puVar3 + 3) = 0;
    puVar3[2] = 0;
    puVar3[1] = 0;
    *puVar3 = 0;
    *(undefined8 *)((long)puVar3 + 0x1c) = 0x3f8000003f800000;
    *(undefined4 *)((long)puVar3 + 0x24) = 0x3f800000;
    *(undefined4 *)(puVar3 + 5) = 0x3f800000;
    puVar3[7] = 0;
    puVar3[6] = 0;
    puVar3[9] = puVar3 + 9;
    *(int *)(puVar3 + 8) = (int)param_1;
    local_38 = FUN_008d9820(&DAT_0273bf78,param_1 * 2 + 2,2);
    local_40 = &DAT_0273bf78;
    if (local_38 == 0) {
      if (puVar3[7] != 0) {
        FUN_008dd4c0(puVar3 + 6);
      }
      FUN_008d9950(&DAT_0273bf78,puVar3);
      puVar3 = (undefined8 *)0x0;
    }
    else {
      local_40 = (undefined2 *)puVar3[6];
      puVar3[6] = &DAT_0273bf78;
      lVar1 = puVar3[7];
      puVar3[7] = local_38;
      local_38 = lVar1;
    }
    if (local_38 != 0) {
      FUN_008dd4c0(&local_40);
    }
  }
  if (*plVar2 == local_30) {
    return puVar3;
  }
  puVar3 = (undefined8 *)thunk_FUN_012aa7f6();
  return puVar3;
}

