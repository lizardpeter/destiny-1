
undefined8 FUN_0097dc10(long param_1,undefined8 *param_2,long *param_3)

{
  short sVar1;
  short sVar2;
  undefined1 uVar3;
  int iVar4;
  long lVar5;
  undefined8 uVar6;
  long local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  sVar1 = ((short *)*param_2)[1];
  sVar2 = *(short *)*param_2;
  if (sVar2 < 2) {
    uVar3 = 0;
    if ((sVar1 == 0) && (uVar3 = 1, sVar2 == 0)) {
      local_40 = param_1;
      if ((undefined *)*param_3 == PTR_DAT_01a1f678) {
        FUN_0107cc70(param_3,&local_40);
        param_3[5] = local_40;
      }
      else {
        if ((param_3[1] != 0) && ((char)param_3[3] == '\0')) {
          (**(code **)param_3[4])(param_3 + 4);
        }
        *param_3 = (long)&DAT_02786d08;
        param_3[1] = (long)&DAT_02786d08;
        FUN_0107cc70(param_3,&local_40);
        *(undefined1 *)(param_3 + 3) = 1;
        param_3[4] = (long)&PTR_thunk_FUN_00a94060_0194d790;
        param_3[5] = local_40;
      }
    }
  }
  else {
    lVar5 = FUN_0097e560(*(undefined8 *)(param_1 + 0x90));
    uVar3 = 0;
    if (lVar5 != 0) {
      iVar4 = 1;
      if (*(code **)(lVar5 + 0x38) != (code *)0x0) {
        iVar4 = (**(code **)(lVar5 + 0x38))(param_1);
      }
      if ((-1 < sVar1) && (sVar1 < iVar4)) {
        uVar3 = (**(code **)(lVar5 + 0x28))(param_1,(int)sVar1,param_3);
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar3);
  }
  uVar6 = thunk_FUN_012aa7f6();
  return uVar6;
}

