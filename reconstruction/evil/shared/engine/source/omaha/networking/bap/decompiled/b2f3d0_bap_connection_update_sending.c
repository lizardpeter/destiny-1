
ulong FUN_00b2f3d0(long param_1,undefined4 *param_2)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  ulong uVar4;
  long lVar5;
  char local_3d;
  undefined4 local_3c;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_3c = 0;
  bVar1 = 1;
  lVar5 = 0;
LAB_00b2f410:
  do {
    if ((((bVar1 & 1) == 0) || (*(int *)(param_1 + 0x16a8) != 0)) ||
       (bVar1 = FUN_00b31830(param_1,param_1 + 0x1850 + lVar5 * 0x198,&local_3c), bVar1 != 0)) {
      lVar5 = lVar5 + 1;
      if ((int)lVar5 < 2) goto LAB_00b2f410;
    }
    if ((bVar1 & 1) != 0) {
      if (*(int *)(param_1 + 0x16a8) == 0) goto LAB_00b2f483;
      if (*(int *)(param_1 + 0x16a8) == 1) {
        local_3d = '\0';
        bVar1 = FUN_00b31950(param_1,&local_3d,&local_3c);
        if (local_3d != '\0') goto LAB_00b2f483;
      }
    }
    lVar5 = 0;
    if ((bVar1 & 1) == 0) {
LAB_00b2f483:
      if ((bVar1 & 1) != 0) {
        iVar2 = 0;
        if (*(undefined8 **)(param_1 + 0x80) != (undefined8 *)0x0) {
          iVar2 = (**(code **)**(undefined8 **)(param_1 + 0x80))();
        }
        if (*(undefined8 **)(param_1 + 0x88) != (undefined8 *)0x0) {
          iVar3 = (**(code **)**(undefined8 **)(param_1 + 0x88))();
          iVar2 = iVar3 + iVar2;
        }
        if (0 < iVar2) {
          FUN_00297fe0(&DAT_00002378 + param_1,iVar2);
        }
        if (0 < *(int *)(param_1 + 0x1a78) + *(int *)(param_1 + 0x18e0)) {
          FUN_00297fe0(param_1 + 0x2458);
        }
      }
      *param_2 = local_3c;
      if (*DAT_01a1f100 != local_38) {
        uVar4 = thunk_FUN_012aa7f6();
        return uVar4;
      }
      return (ulong)CONCAT31((int3)((uint)local_3c >> 8),(bVar1 & 1) != 0);
    }
  } while( true );
}

