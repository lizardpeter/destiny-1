
undefined8 FUN_00bb2010(undefined8 param_1,undefined1 *param_2)

{
  long *plVar1;
  char cVar2;
  long lVar3;
  undefined8 uVar4;
  undefined1 uVar5;
  undefined8 local_40;
  undefined1 local_38;
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  lVar3 = FUN_00b9f390();
  local_38 = *param_2;
  local_40 = param_1;
  cVar2 = FUN_00300230(0x16,*(undefined4 *)PTR_DAT_019b46f0,&local_40);
  uVar5 = 0;
  if ((cVar2 != '\0') && (uVar5 = 1, lVar3 != 0)) {
    FUN_00bb7550(lVar3,1);
  }
  if (*plVar1 == local_30) {
    return CONCAT71((int7)((ulong)*plVar1 >> 8),uVar5);
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

