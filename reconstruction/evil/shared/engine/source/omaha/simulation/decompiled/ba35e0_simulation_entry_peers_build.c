
/* WARNING: Type propagation algorithm not settling */

void FUN_00ba35e0(long *param_1,long param_2)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  long lVar4;
  long lVar5;
  undefined8 *puVar6;
  ulong uVar7;
  long local_108 [27];
  
  local_108[0x15] = *DAT_01a1f100;
  if (*param_1 != 0) {
    FUN_00ba27e0(param_1[1]);
    if (param_1[2] != 0) {
      param_1[2] = 0;
    }
  }
  *(undefined4 *)(param_1 + 0x1b) = 0xffffffff;
  *param_1 = param_2;
  if (param_2 != 0) {
    lVar4 = FUN_0029c3b0(param_2);
    local_108[0] = 0;
    FUN_007770f0(local_108);
    param_1[2] = local_108[0];
    lVar5 = FUN_0029c3b0(*param_1);
    uVar1 = FUN_002a55c0(lVar5 + 8);
    uVar7 = 0;
    local_108[0x11] = 0;
    local_108[0x12] = 0;
    local_108[0x13] = 0;
    local_108[0x14] = 0;
    local_108[0xd] = 0;
    local_108[0xe] = 0;
    local_108[0xf] = 0;
    local_108[0x10] = 0;
    local_108[9] = 0;
    local_108[10] = 0;
    local_108[0xb] = 0;
    local_108[0xc] = 0;
    local_108[5] = 0;
    local_108[6] = 0;
    local_108[7] = 0;
    local_108[8] = 0;
    local_108[1] = 0;
    local_108[2] = 0;
    local_108[3] = 0;
    local_108[4] = 0;
    do {
      if ((uVar1 >> ((uint)uVar7 & 0x1f) & 1) != 0) {
        puVar6 = (undefined8 *)FUN_002a54b0(lVar4 + 8,uVar7 & 0xffffffff);
        local_108[uVar7 + 1] = *puVar6;
      }
      uVar7 = uVar7 + 1;
    } while ((int)uVar7 != 0x14);
    uVar2 = FUN_00057e60(lVar4 + 8);
    *(undefined4 *)(param_1 + 3) = uVar2;
    *(uint *)((long)param_1 + 0x1c) = uVar1;
    thunk_FUN_012aa7c6((long)param_1 + 0x2c,local_108 + 1,0xa0);
    iVar3 = FUN_002a0870(lVar4);
    *(int *)(param_1 + 5) = iVar3;
    param_1[4] = *(long *)((long)param_1 + (long)iVar3 * 8 + 0x2c);
    *(undefined1 *)((long)param_1 + 0xcc) = 1;
  }
  if (*DAT_01a1f100 == local_108[0x15]) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

