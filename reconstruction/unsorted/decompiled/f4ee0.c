
void FUN_000f4ee0(undefined4 param_1)

{
  int *piVar1;
  long *plVar2;
  char cVar3;
  int iVar4;
  long lVar5;
  undefined1 local_38 [16];
  long local_28;
  
  plVar2 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  lVar5 = FUN_000f6ff0();
  FUN_000f7060(local_38,param_1,0xffffffff);
  cVar3 = FUN_000f5240(*(undefined8 *)(lVar5 + 0x18));
  if ((cVar3 != '\0') && (*(char *)(lVar5 + 0x20) == '\0')) {
    iVar4 = FUN_000f6ac0();
    piVar1 = (int *)(lVar5 + 0x28 + (long)iVar4 * 4);
    *piVar1 = *piVar1 + 1;
  }
  FUN_000f7070(local_38);
  if (*plVar2 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

