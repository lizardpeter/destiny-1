
void FUN_007db340(undefined4 *param_1,long param_2)

{
  int iVar1;
  ulong uVar2;
  ulong uVar3;
  long lVar4;
  ulong uVar5;
  ulong uVar6;
  long lVar7;
  ulong local_38;
  
  if (*(int *)(param_2 + 0x18) != 0) {
    lVar4 = FUN_007e3a00(DAT_026e2be8);
    uVar6 = (ulong)*(int *)(param_2 + 0x18);
    uVar2 = *(ulong *)(param_2 + 8);
    uVar3 = *(ulong *)(param_2 + 0x10);
    local_38 = uVar6;
    if ((uVar2 <= uVar3) && (local_38 = uVar3 - uVar2, uVar6 + uVar2 <= uVar3)) {
      local_38 = uVar6;
    }
    if (0 < *(int *)(param_2 + 0x18)) {
      lVar7 = 0;
      do {
        if ((param_1[2] == 0) && (*(char *)(param_1 + 3) != '\0')) {
          FUN_007dcaa0(lVar4);
          FUN_007dcce0(lVar4);
          FUN_007dcaf0(lVar4);
          *(undefined2 *)(param_1 + 3) = 0;
          *(undefined1 *)((long)param_1 + 0xe) = 1;
        }
        uVar5 = uVar6;
        if ((long)local_38 < (long)uVar6) {
          uVar5 = local_38;
        }
        FUN_00f8f3a0(*(undefined8 *)(lVar4 + 0x50),lVar7 + uVar2,lVar7 + uVar3,uVar5 & 0xffffffff,
                     (long)uVar6 <= (long)local_38);
        iVar1 = param_1[1];
        param_1[1] = iVar1 + 1;
        if (3999 < iVar1) {
          *(undefined1 *)((long)param_1 + 0xd) = 1;
        }
        if ((param_1[2] == 0) && (*(char *)((long)param_1 + 0xd) != '\0')) {
          FUN_007dcec0(lVar4,0,0);
          FUN_007dd060(lVar4);
          *(undefined1 *)((long)param_1 + 0xd) = 0;
          param_1[1] = 0;
          FUN_007dcaa0(lVar4);
          FUN_007dcce0(lVar4);
          FUN_007dcaf0(lVar4);
          *(undefined1 *)(param_1 + 3) = 0;
          *(undefined1 *)((long)param_1 + 0xe) = 1;
        }
        lVar7 = lVar7 + (int)uVar5;
        uVar6 = uVar6 - (long)(int)uVar5;
      } while (0 < (long)uVar6);
    }
  }
  *(undefined1 *)(param_2 + 0x3c) = 1;
  *(undefined4 *)(param_2 + 0x38) = *param_1;
  return;
}

