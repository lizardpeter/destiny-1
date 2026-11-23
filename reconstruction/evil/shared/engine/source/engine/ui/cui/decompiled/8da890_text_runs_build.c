
long * FUN_008da890(long *param_1,long *param_2,undefined8 param_3,undefined8 param_4)

{
  char cVar1;
  long lVar2;
  long *plVar3;
  long lVar4;
  long local_48;
  long local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  param_1[1] = 0;
  *param_1 = 0;
  lVar2 = FUN_008d9820(&DAT_0273bf78,8,8);
  if (lVar2 != 0) {
    *(long *)lVar2 = lVar2;
    FUN_01078340(&local_48,lVar2,&DAT_0273bf78);
    lVar2 = 0;
    if (local_48 != 0) {
      if (local_40 != 0) {
        *(int *)(local_40 + 8) = *(int *)(local_40 + 8) + 1;
      }
      *param_1 = local_48;
      param_1[1] = local_40;
      lVar2 = local_48;
    }
    if (local_40 != 0) {
      FUN_008dd4f0();
    }
    if (lVar2 != 0) {
      lVar2 = 0;
      if (*param_2 != 0) {
        lVar2 = *param_2 + (long)param_2;
      }
      lVar4 = (ulong)*(uint *)(param_2 + 1) << 5;
      do {
        if (lVar4 == 0) {
          if (*param_1 != 0) {
            FUN_008dd280();
          }
          goto LAB_008da9a0;
        }
        cVar1 = FUN_008da9d0(lVar2,param_1,param_3,param_4);
        lVar4 = lVar4 + -0x20;
        lVar2 = lVar2 + 0x20;
      } while (cVar1 != '\0');
      *param_1 = 0;
      lVar2 = param_1[1];
      param_1[1] = 0;
      if (lVar2 != 0) {
        FUN_008dd4f0();
      }
    }
  }
LAB_008da9a0:
  if (*DAT_01a1f100 == local_38) {
    return param_1;
  }
  plVar3 = (long *)thunk_FUN_012aa7f6();
  return plVar3;
}

