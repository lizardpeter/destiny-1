
undefined8 FUN_00299b00(long *param_1,code *param_2,uint param_3)

{
  long lVar1;
  long lVar2;
  int iVar3;
  long lVar4;
  undefined8 uVar5;
  undefined1 uVar6;
  long lVar7;
  ulong uVar8;
  undefined1 local_170 [320];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  if (param_3 == 0xffffffff) {
    *(undefined1 *)(param_1 + 0x1cc) = 1;
  }
  else {
    lVar7 = (ulong)(((uint)((int)param_3 >> 0xd) >> 0x12 | 0x3ff) & (int)param_3 >> 0xd) * 0x40;
    uVar5 = FUN_00021860(param_1[0x1cb]);
    lVar4 = FUN_002a2980(uVar5);
    lVar1 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar1 + 0x10 + lVar7);
    uVar8 = (ulong)((param_3 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar7));
    if (*(int *)(lVar4 + 0x5c) !=
        *(int *)(((lVar2 + uVar8) -
                 ((long)*(int *)(lVar1 + 0x34 + lVar7) & *(ulong *)(lVar2 + 8 + uVar8))) + 0xc +
                (long)(int)param_1[3] * 4)) {
      if (DAT_02655408 == '\0') {
        iVar3 = thunk_FUN_012aa7d6(&DAT_02655408);
        if (iVar3 != 0) {
          DAT_02655400 = FUN_000e4a10(s_networking_activity_client____s__01621d0a);
          thunk_FUN_012aa7e6(&DAT_02655408);
        }
      }
      uVar5 = (**(code **)(*param_1 + 0x30))(param_1);
      uVar6 = 0;
      FUN_01008290(local_170,s_networking_activity_client____s__01621d0a,uVar5);
      FUN_000e4aa0(DAT_02655400,local_170);
      (*param_2)(5,0,s_activity_checksum_mismatch_01621d47);
      goto LAB_00299c29;
    }
    *(undefined1 *)(param_1 + 0x1cc) = 0;
  }
  uVar6 = 1;
LAB_00299c29:
  if (*DAT_01a1f100 == local_30) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar6);
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

