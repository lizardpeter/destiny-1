
undefined8 FUN_000fad30(undefined8 *param_1,undefined4 param_2)

{
  int *piVar1;
  int iVar2;
  long lVar3;
  ushort uVar4;
  char cVar5;
  undefined4 uVar6;
  undefined8 uVar7;
  int iVar8;
  ulong uVar9;
  ushort local_42;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_000fb030();
  FUN_000fc500(param_2);
  FUN_000fc540(param_1);
  piVar1 = (int *)((long)param_1 + 0x14);
  uVar7 = FUN_000f7c30();
  param_1[5] = uVar7;
  *(undefined2 *)((long)param_1 + 0x1c) = 0xffff;
  param_1[4] = 0xffffffffffffffff;
  if (*(int *)((long)param_1 + 0x14) == 2) {
LAB_000fae82:
    FUN_000fc500(0);
    do {
      iVar2 = *piVar1;
      LOCK();
      iVar8 = *piVar1;
      if (iVar2 == iVar8) {
        *piVar1 = 3;
        iVar8 = iVar2;
      }
      UNLOCK();
    } while (iVar2 != iVar8);
    if (*DAT_01a1f100 != local_38) {
      uVar7 = thunk_FUN_012aa7f6();
      return uVar7;
    }
    return 1;
  }
LAB_000fada0:
  FUN_000f81b0();
  FUN_000fe910(DAT_025d1270,param_2);
  do {
    iVar8 = 0;
    while( true ) {
      local_42 = 0xffff;
      FUN_000fefd0(DAT_025d1270);
      cVar5 = FUN_000fa750(*param_1,param_1 + 1,&local_42);
      uVar4 = local_42;
      if (cVar5 != '\0') break;
      iVar8 = iVar8 + 1;
      if (9 < iVar8) {
        if (*piVar1 != 2) goto LAB_000fada0;
        goto LAB_000fae82;
      }
    }
    uVar9 = (ulong)local_42;
    uVar6 = FUN_000fc560();
    FUN_000fc460(uVar9);
    *(undefined1 *)(DAT_025d1270 + 0x10008 + uVar9 * 0x10) = 5;
    *(ushort *)((long)param_1 + 0x1c) = uVar4;
    lVar3 = DAT_025d1270;
    FUN_000fd8f0(&local_40,DAT_025d1270 + 0x10000 + uVar9 * 0x10);
    FUN_000fa980(uVar9 * 0x80 + lVar3,param_2,local_40);
    *(undefined2 *)((long)param_1 + 0x1c) = 0xffff;
    FUN_000fc460(uVar6);
  } while( true );
}

