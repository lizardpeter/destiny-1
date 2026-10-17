
void FUN_002b4270(undefined8 param_1,int param_2)

{
  long lVar1;
  byte bVar2;
  char cVar3;
  undefined8 uVar4;
  undefined1 local_38 [8];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  if (param_2 == 0x24) {
    uVar4 = FUN_002956c0();
    lVar1 = DAT_0266d6a0;
    bVar2 = FUN_00244ee0(local_38);
    if (*(char *)(lVar1 + 0x27f) != '\0') {
      cVar3 = FUN_002ba070(lVar1);
      if (cVar3 != '\0') {
        FUN_002ba270(lVar1);
      }
      cVar3 = FUN_002ba070(lVar1 + 0x90);
      if (cVar3 != '\0') {
        FUN_002ba270(lVar1 + 0x90);
      }
      cVar3 = FUN_002ba070(lVar1 + 0x128);
      if (cVar3 != '\0') {
        FUN_002ba270(lVar1 + 0x128);
      }
    }
    *(undefined1 *)(lVar1 + 0x312) = 1;
    *(byte *)(lVar1 + 0x313) = bVar2 ^ 1;
    thunk_FUN_012aa7c6(lVar1 + 0x314,uVar4,0x8c);
  }
  if (*DAT_01a1f100 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

