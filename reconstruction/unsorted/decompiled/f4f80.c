
undefined8 FUN_000f4f80(undefined4 param_1,undefined4 param_2)

{
  int *piVar1;
  long *plVar2;
  char cVar3;
  int iVar4;
  long lVar5;
  undefined8 uVar6;
  undefined1 local_40 [16];
  long local_30;
  
  plVar2 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  lVar5 = FUN_000f6ff0();
  FUN_000f7060(local_40,param_1,0xffffffff);
  cVar3 = FUN_000f5280(*(undefined8 *)(lVar5 + 0x18),param_2);
  if ((cVar3 != '\0') && (*(char *)(lVar5 + 0x20) == '\0')) {
    iVar4 = FUN_000f6ac0();
    piVar1 = (int *)(lVar5 + 0x28 + (long)iVar4 * 4);
    *piVar1 = *piVar1 + 1;
  }
  FUN_000f7070(local_40);
  if (*plVar2 == local_30) {
    return CONCAT71((int7)((ulong)*plVar2 >> 8),cVar3);
  }
  uVar6 = thunk_FUN_012aa7f6();
  return uVar6;
}

