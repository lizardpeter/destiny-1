
void FUN_0063e6c0(long param_1)

{
  undefined4 uVar1;
  undefined *puVar2;
  long lVar3;
  int iVar4;
  ulong uVar5;
  undefined8 uVar6;
  uint uVar7;
  undefined1 local_50 [24];
  long local_38;
  
  lVar3 = DAT_02692228;
  puVar2 = PTR_DAT_019b1bb8;
  local_38 = *DAT_01a1f100;
  uVar7 = 0x1fff;
  if (*(uint *)(param_1 + 4) != 0xffffffff) {
    uVar5 = (ulong)((*(uint *)(param_1 + 4) & 0x1fff) * DAT_02689800);
    uVar7 = *(uint *)(((DAT_026897f8 + uVar5) -
                      ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar5))) + 0x2c) & 0x1fff;
  }
  uVar7 = uVar7 * DAT_02692230;
  uVar1 = *(undefined4 *)PTR_DAT_019b1bb8;
  uVar6 = FUN_00328240(local_50);
  iVar4 = FUN_00327f40(lVar3 + (ulong)uVar7,uVar1,0,0,uVar6);
  if (iVar4 != -1) {
    FUN_003283d0(iVar4);
  }
  lVar3 = DAT_02692228;
  uVar7 = 0x1fff;
  if (*(uint *)(param_1 + 4) != 0xffffffff) {
    uVar5 = (ulong)((*(uint *)(param_1 + 4) & 0x1fff) * DAT_02689800);
    uVar7 = *(uint *)(((DAT_026897f8 + uVar5) -
                      ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar5))) + 0x2c) & 0x1fff;
  }
  uVar7 = *(uint *)((ulong)(uVar7 * DAT_02692230) + 0x44 + DAT_02692228);
  if (uVar7 != 0xffffffff) {
    uVar7 = (uVar7 & 0x1fff) * DAT_02692230;
    uVar1 = *(undefined4 *)puVar2;
    uVar6 = FUN_00328240(local_50);
    iVar4 = FUN_00327f40(lVar3 + (ulong)uVar7,uVar1,0,0,uVar6);
    if (iVar4 != -1) {
      FUN_003283d0(iVar4);
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

