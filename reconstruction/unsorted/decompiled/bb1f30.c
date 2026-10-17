
undefined8 FUN_00bb1f30(undefined8 param_1,undefined1 *param_2)

{
  char cVar1;
  long lVar2;
  undefined8 uVar3;
  undefined1 uVar4;
  undefined8 local_730;
  undefined1 local_728;
  undefined1 local_724 [1536];
  undefined1 local_124 [240];
  undefined1 local_34;
  long local_30;
  
  local_30 = *DAT_01a1f100;
  thunk_FUN_012aa986(local_724,0,0x600);
  lVar2 = FUN_00b9f390();
  local_728 = *param_2;
  local_730 = param_1;
  thunk_FUN_012aa7c6(local_724,param_2 + 4,0x600);
  local_34 = param_2[1];
  thunk_FUN_012aa986(local_124,0,0xf0);
  cVar1 = FUN_00300230(0x15,*(undefined4 *)PTR_DAT_019b46e8,&local_730);
  uVar4 = 0;
  if ((cVar1 != '\0') && (uVar4 = 1, lVar2 != 0)) {
    FUN_00bb7550(lVar2,1);
  }
  if (*DAT_01a1f100 == local_30) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar4);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

