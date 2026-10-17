
undefined8 FUN_00bc3af0(long *param_1,undefined8 param_2,undefined4 param_3)

{
  int iVar1;
  long lVar2;
  long lVar3;
  char cVar4;
  undefined4 uVar5;
  long lVar6;
  undefined8 uVar7;
  ulong uVar8;
  long lVar9;
  uint local_50 [2];
  long local_48;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar4 = FUN_001071d0(param_2,0,local_50);
  lVar3 = local_48;
  uVar7 = 0;
  if ((cVar4 != '\0') && (local_50[0] != 0xffffffff)) {
    lVar6 = (ulong)(((uint)((int)local_50[0] >> 0xd) >> 0x12 | 0x3ff) & (int)local_50[0] >> 0xd) *
            0x40;
    lVar9 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar9 + 0x10 + lVar6);
    uVar8 = (ulong)((local_50[0] & 0x1fff) * *(int *)(lVar9 + 0x30 + lVar6));
    lVar9 = (lVar2 + uVar8) - ((long)*(int *)(lVar9 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar8))
    ;
    iVar1 = *(int *)(local_48 + 600 + lVar9);
    if (iVar1 != -1) {
      (**(code **)(*param_1 + 0xb8))(param_1,iVar1);
      FUN_00ba8010(iVar1,0xffffffff);
    }
    uVar5 = FUN_00105e30(local_50[0],local_48);
    FUN_00ba8010(param_3,uVar5);
    *(undefined4 *)(lVar9 + 600 + lVar3) = param_3;
    uVar7 = 1;
  }
  if (*DAT_01a1f100 == local_38) {
    return uVar7;
  }
  uVar7 = thunk_FUN_012aa7f6();
  return uVar7;
}

