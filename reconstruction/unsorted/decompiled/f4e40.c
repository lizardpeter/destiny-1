
ulong FUN_000f4e40(undefined8 param_1,undefined1 *param_2)

{
  long *plVar1;
  char cVar2;
  int iVar3;
  long lVar4;
  ulong uVar5;
  int iVar6;
  undefined1 uVar7;
  uint local_34;
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  lVar4 = FUN_000f6ff0();
  local_34 = 0;
  cVar2 = FUN_000f5220(*(undefined8 *)(lVar4 + 0x18),&local_34);
  uVar7 = 0;
  if ((cVar2 != '\0') && (uVar7 = 1, *(char *)(lVar4 + 0x20) == '\0')) {
    iVar3 = FUN_000f6ac0();
    iVar6 = *(int *)(lVar4 + 0x28 + (long)iVar3 * 4) + -1;
    if (iVar6 < 0) {
      iVar6 = 0;
    }
    *(int *)(lVar4 + 0x28 + (long)iVar3 * 4) = iVar6;
  }
  if (param_2 != (undefined1 *)0x0) {
    *param_2 = uVar7;
  }
  if (*plVar1 == local_30) {
    return (ulong)local_34;
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

