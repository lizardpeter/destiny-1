
void FUN_002b4420(void)

{
  long *plVar1;
  long lVar2;
  char cVar3;
  int iVar4;
  undefined1 local_a8 [8];
  undefined8 local_a0;
  ulong uStack_98;
  undefined8 uStack_90;
  undefined8 uStack_88;
  undefined8 local_80;
  undefined8 local_78;
  undefined8 local_70;
  long local_58;
  
  lVar2 = DAT_0266d6a0;
  plVar1 = DAT_01a1f100;
  local_58 = *DAT_01a1f100;
  if (((*(char *)(DAT_0266d6a0 + 0x312) != '\0') && (*(char *)(DAT_0266d6a0 + 0x27f) == '\0')) &&
     (cVar3 = FUN_00244ee0(local_a8), cVar3 != '\0')) {
    FUN_002b4600(lVar2,local_a8,lVar2 + 0x314);
    *(undefined1 *)(lVar2 + 0x312) = 0;
  }
  lVar2 = DAT_0266d6a0;
  if ((*(char *)(DAT_0266d6a0 + 0x27d) == '\0') &&
     (FUN_002b4af0(DAT_0266d6a0), *(char *)(lVar2 + 0x27d) != '\0')) {
    if (*(char *)(lVar2 + 0x27e) != '\0') {
      thunk_FUN_012aa7c6(lVar2 + 0x280,lVar2 + 0x1c0,0x8c);
      FUN_00294a00(0x25,lVar2 + 0x1c0);
    }
    cVar3 = FUN_002ba070(lVar2 + 0x128);
    if (cVar3 != '\0') {
      FUN_002ba080(lVar2 + 0x128);
    }
    cVar3 = FUN_002ba070(lVar2 + 0x90);
    if (cVar3 != '\0') {
      FUN_002ba080(lVar2 + 0x90);
    }
    FUN_002ba150(lVar2);
    *(undefined2 *)(lVar2 + 0x27d) = 1;
    *(undefined1 *)(lVar2 + 0x27f) = 0;
  }
  lVar2 = DAT_0266d6a0;
  if ((*(char *)(DAT_0266d6a0 + 0x310) != '\0') && (iVar4 = thunk_FUN_012ab7a6(), iVar4 == 3)) {
    local_a0 = 0;
    uStack_98 = 0;
    uStack_90 = 0;
    uStack_88 = 0;
    local_70 = 0;
    local_78 = 0;
    local_80 = 0;
    thunk_FUN_012ab7b6(&local_a0);
    if ((int)uStack_98 == 0) {
      *(bool *)(lVar2 + 0x311) = uStack_98 >> 0x20 == 0;
    }
    else {
      *(undefined1 *)(lVar2 + 0x311) = 0;
    }
  }
  iVar4 = thunk_FUN_012ab7c6();
  if (iVar4 == 3) {
    if (*(char *)(lVar2 + 0x311) != '\0') {
      FUN_002949c0(0x29);
    }
    thunk_FUN_012ab7d6();
    *(undefined1 *)(lVar2 + 0x310) = 0;
  }
  if (*plVar1 != local_58) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

