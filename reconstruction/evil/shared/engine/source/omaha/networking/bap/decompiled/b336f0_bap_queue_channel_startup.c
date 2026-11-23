
ulong FUN_00b336f0(long param_1)

{
  undefined8 *puVar1;
  int iVar2;
  long lVar3;
  long *plVar4;
  ulong uVar5;
  int iVar6;
  long lVar7;
  undefined8 local_b8;
  undefined2 auStack_b0 [64];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  iVar2 = *(int *)(param_1 + 0x1c) + *(int *)(param_1 + 0x20);
  iVar6 = iVar2 % *(int *)(param_1 + 0x18);
  *(int *)(param_1 + 0x20) = *(int *)(param_1 + 0x20) + 1;
  uVar5 = (long)iVar2 / (long)*(int *)(param_1 + 0x18) & 0xffffff00;
  if (iVar6 != -1) {
    lVar3 = (long)iVar6;
    puVar1 = (undefined8 *)(param_1 + 0x24 + lVar3 * 0x18);
    puVar1[2] = 0;
    puVar1[1] = 0;
    *puVar1 = 0;
    *(undefined4 *)puVar1 = 5;
    *(undefined4 *)(param_1 + 0x28 + lVar3 * 0x18) = 0x1e;
    plVar4 = (long *)FUN_0055af60(0x1e);
    local_b8 = 0x1594e4954534544;
    lVar7 = 4;
    iVar2 = FUN_000911d0();
    do {
      iVar2 = iVar2 * 0x19660d + 0x3c6ef35f;
      auStack_b0[lVar7 + -4] = (short)((uint)iVar2 >> 0x10);
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 != 0x40);
    uVar5 = (**(code **)(*plVar4 + 0x10))
                      (plVar4,0x80,&local_b8,param_1 + 0x3c,0x800,param_1 + 0x2c + lVar3 * 0x18);
  }
  if (*DAT_01a1f100 == local_30) {
    return uVar5;
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

