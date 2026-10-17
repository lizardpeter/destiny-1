
void FUN_00913a90(uint param_1,long *param_2)

{
  long lVar1;
  uint uVar2;
  uint uVar3;
  long *plVar4;
  undefined1 local_140 [16];
  long local_130;
  undefined1 local_128 [8];
  undefined4 local_120;
  uint local_118 [20];
  long local_c8 [20];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  uVar3 = *(uint *)(DAT_0273ea90 + 4);
  thunk_FUN_012aa7c6(local_c8,DAT_0273ea90 + 8,0xa0);
  lVar1 = 0;
  local_118[0x12] = 0xffffffff;
  local_118[0x13] = 0xffffffff;
  local_118[0x10] = 0xffffffff;
  local_118[0x11] = 0xffffffff;
  local_118[0xe] = 0xffffffff;
  local_118[0xf] = 0xffffffff;
  local_118[0xc] = 0xffffffff;
  local_118[0xd] = 0xffffffff;
  local_118[10] = 0xffffffff;
  local_118[0xb] = 0xffffffff;
  local_118[8] = 0xffffffff;
  local_118[9] = 0xffffffff;
  local_118[6] = 0xffffffff;
  local_118[7] = 0xffffffff;
  local_118[4] = 0xffffffff;
  local_118[5] = 0xffffffff;
  local_118[2] = 0xffffffff;
  local_118[3] = 0xffffffff;
  local_118[0] = 0xffffffff;
  local_118[1] = 0xffffffff;
  do {
    if ((uVar3 >> ((uint)lVar1 & 0x1f) & 1) != 0) {
      uVar2 = 0;
      plVar4 = param_2;
      do {
        if (((param_1 >> (uVar2 & 0x1f) & 1) != 0) && (*plVar4 == local_c8[lVar1])) {
          local_118[lVar1] = uVar2;
          break;
        }
        plVar4 = plVar4 + 1;
        uVar2 = uVar2 + 1;
      } while ((int)uVar2 < 0x14);
    }
    lVar1 = lVar1 + 1;
  } while ((int)lVar1 != 0x14);
  FUN_00074a80(local_128,DAT_0273ea80);
  local_130 = 0;
  while (local_130 = FUN_00074a90(local_128), local_130 != 0) {
    if (((long)*(int *)(local_130 + 0x628) != -1) &&
       (local_118[*(int *)(local_130 + 0x628)] == 0xffffffff)) {
      FUN_0090e5a0(local_120,0);
    }
  }
  *(uint *)(DAT_0273ea90 + 4) = param_1;
  thunk_FUN_012aa7c6(DAT_0273ea90 + 8,param_2,0xa0);
  FUN_00074a80(local_140,DAT_0273ea80);
  while (lVar1 = FUN_00074a90(local_140), lVar1 != 0) {
    if (((long)*(int *)(lVar1 + 0x628) != -1) && (local_118[*(int *)(lVar1 + 0x628)] != 0xffffffff))
    {
      *(uint *)(lVar1 + 0x628) = local_118[*(int *)(lVar1 + 0x628)];
    }
  }
  if (*(char *)(DAT_0273ea90 + 0xa8) != '\0') {
    uVar3 = 0;
    do {
      if (((param_1 >> (uVar3 & 0x1f) & 1) != 0) && (*param_2 == *(long *)(DAT_0273ea90 + 0xa9))) {
        if (uVar3 != 0xffffffff) {
          if (*(int *)(DAT_0273ea90 + 0xb4) == -1) {
            FUN_00913d20();
            FUN_0090e120(1);
          }
          else {
            *(uint *)(DAT_0273ea90 + 0xb4) = uVar3;
          }
        }
        break;
      }
      param_2 = param_2 + 1;
      uVar3 = uVar3 + 1;
    } while ((int)uVar3 < 0x14);
  }
  if (*DAT_01a1f100 != local_28) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

