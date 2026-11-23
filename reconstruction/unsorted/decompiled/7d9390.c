
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_007d9390(long param_1)

{
  long *plVar1;
  char cVar2;
  long lVar3;
  undefined8 local_38;
  undefined8 uStack_30;
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  local_38 = _DAT_0165fd60;
  uStack_30 = uRam000000000165fd68;
  *(undefined4 *)(*(long *)(param_1 + 0x1010) + 0x70) = 0;
  lVar3 = FUN_0082cb90(0);
  if (lVar3 != 0) {
    cVar2 = FUN_00820480(param_1,lVar3,&local_38,*(undefined8 *)(param_1 + 0x15c0));
    if (cVar2 != '\0') {
      *(byte *)(param_1 + 0x15ac) = *(byte *)(param_1 + 0x15ac) | 1;
    }
  }
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

