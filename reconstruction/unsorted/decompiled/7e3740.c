
char FUN_007e3740(int *param_1)

{
  int *piVar1;
  int iVar2;
  char cVar3;
  char cVar4;
  undefined4 uVar5;
  int iVar6;
  undefined8 uVar7;
  ushort uVar8;
  int *piVar9;
  
  cVar3 = '\x01';
  if (*param_1 == 0) {
    piVar1 = param_1 + 0x46d4;
    thunk_FUN_012aa986(piVar1,0,0x13438);
    param_1[0x46da] = 0x10;
    uVar5 = FUN_00f8a980(0x10);
    uVar7 = FUN_000b4a60(uVar5,0xe);
    *(undefined8 *)(param_1 + 0x46d6) = uVar7;
    uVar7 = FUN_000b4a60(uVar5,0xe);
    *(undefined8 *)(param_1 + 0x46d8) = uVar7;
    param_1[0x4701] = 0;
    do {
      iVar2 = *param_1;
      LOCK();
      iVar6 = *param_1;
      if (iVar2 == iVar6) {
        *param_1 = 1;
        iVar6 = iVar2;
      }
      UNLOCK();
    } while (iVar2 != iVar6);
    cVar3 = FUN_007e40a0(param_1 + 4,piVar1);
    if (cVar3 == '\0') {
      cVar3 = '\0';
    }
    else {
      uVar8 = 0xffff;
      piVar9 = param_1 + 0xa44;
      do {
        uVar8 = uVar8 + 1;
        if (5 < uVar8) {
          FUN_0005a940(thunk_FUN_007e5a70);
          return cVar3;
        }
        cVar4 = FUN_007e5d50(piVar9,piVar1);
        piVar9 = piVar9 + 0xa18;
      } while (cVar4 != '\0');
      cVar3 = '\0';
    }
  }
  return cVar3;
}

