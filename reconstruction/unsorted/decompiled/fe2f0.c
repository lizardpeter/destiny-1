
undefined8 FUN_000fe2f0(long param_1,long param_2,byte param_3,undefined1 param_4)

{
  int *piVar1;
  int iVar2;
  byte bVar3;
  ushort uVar4;
  int iVar5;
  short extraout_var;
  undefined8 uVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  uint uVar10;
  long lVar11;
  long lVar12;
  ulong uVar13;
  undefined4 local_40;
  undefined2 uStack_3c;
  undefined2 uStack_3a;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar4 = FUN_000fe110();
  uVar13 = (ulong)uVar4;
  lVar11 = uVar13 * 0x10;
  *(undefined1 *)(param_1 + 0x10008 + lVar11) = 1;
  *(undefined1 *)(param_1 + 0x1000a + lVar11) = param_4;
  *(undefined2 *)(param_1 + 0x10006 + lVar11) = 0xffff;
  LOCK();
  piVar1 = (int *)(param_1 + 0x10000 + lVar11);
  *piVar1 = *piVar1 + 1;
  UNLOCK();
  uVar6 = FUN_00001df0();
  uVar10 = (int)*(uint *)(param_2 + 0x68) >> 0xd;
  lVar9 = (ulong)((uVar10 >> 0x12 | 0x3ff) & uVar10) * 0x40;
  lVar8 = *DAT_01a238a0;
  lVar12 = *(long *)(lVar8 + 0x10 + lVar9);
  uVar7 = (ulong)((*(uint *)(param_2 + 0x68) & 0x1fff) * *(int *)(lVar8 + 0x30 + lVar9));
  lVar8 = FUN_00057f80((lVar12 + uVar7) -
                       ((long)*(int *)(lVar8 + 0x34 + lVar9) & *(ulong *)(lVar12 + 8 + uVar7)),0xa0,
                       0,1);
  lVar12 = uVar13 * 0x80;
  piVar1 = (int *)(param_1 + lVar12);
  do {
    do {
    } while (*piVar1 != 0);
    LOCK();
    iVar5 = *piVar1;
    if (iVar5 == 0) {
      *piVar1 = 1;
      iVar5 = 0;
    }
    UNLOCK();
  } while (iVar5 != 0);
  FUN_000f9110(piVar1,param_2);
  do {
    iVar2 = *piVar1;
    LOCK();
    iVar5 = *piVar1;
    if (iVar2 == iVar5) {
      *piVar1 = 0;
      iVar5 = iVar2;
    }
    UNLOCK();
  } while (iVar2 != iVar5);
  FUN_00011ea0(1);
  FUN_000fd8f0(&local_40,param_1 + 0x10000 + lVar11);
  if (((param_3 & 4) != 0) && (thunk_FUN_000fc480(), extraout_var != -1)) {
    FUN_000ff490(param_1,extraout_var,uStack_3c,local_40,1);
  }
  if ((param_3 & 1) == 0) {
    LOCK();
    piVar1 = (int *)(param_1 + 0x58 + lVar12);
    *piVar1 = *piVar1 + 1;
    UNLOCK();
  }
  else {
    *(undefined1 *)(param_1 + 0x10008 + lVar11) = 2;
  }
  FUN_00011ea0(1);
  bVar3 = 0x10;
  if (*(char *)(lVar8 + 0x9a) == '\0') {
    bVar3 = 0;
  }
  if (*(char *)(lVar8 + 0x9b) != '\0') {
    bVar3 = bVar3 | 0x20;
  }
  bVar3 = param_3 & 0x4a | bVar3;
  *(byte *)(param_1 + 0x10009 + lVar11) = bVar3;
  *(byte *)(param_1 + 0x5c + lVar12) = bVar3;
  FUN_0001cf60();
  FUN_000fefd0(param_1);
  if (((uVar4 != 0xffff) && (*(char *)(param_1 + 0x10008 + lVar11) == '\x02')) &&
     (*(int *)(param_1 + 0x58 + lVar12) == 0)) {
    piVar1 = (int *)(param_1 + 0x58 + lVar12);
    LOCK();
    iVar5 = *piVar1;
    if (iVar5 == 0) {
      *piVar1 = 0x10000;
      iVar5 = 0;
    }
    UNLOCK();
    if (iVar5 == 0) {
      FUN_000fe9f0(param_1,uVar13);
      FUN_0100c790(param_1 + 0x14080,0);
    }
  }
  FUN_00011ea0(uVar6);
  if (*DAT_01a1f100 != local_38) {
    uVar6 = thunk_FUN_012aa7f6();
    return uVar6;
  }
  return CONCAT26(uStack_3a,CONCAT24(uStack_3c,local_40));
}

