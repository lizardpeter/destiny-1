
void FUN_00759ad0(long param_1)

{
  int *piVar1;
  undefined1 uVar2;
  char cVar3;
  long lVar4;
  undefined4 *puVar5;
  long lVar6;
  
  if (*(char *)(param_1 + 0x80) != '\0') {
    uVar2 = FUN_0010c750();
    *(undefined1 *)(param_1 + 0xac0) = uVar2;
    FUN_00759ba0(param_1);
    FUN_0029f040();
    FUN_0029f5c0();
    piVar1 = DAT_026c96f8;
    puVar5 = (undefined4 *)(param_1 + 0x4a8);
    lVar6 = 0;
    do {
      lVar4 = FUN_00768080();
      if (((lVar4 == 0) || (*(int *)(lVar4 + 0x4f0 + (long)*DAT_026c96f8 * 0x1f0) == -1)) &&
         (cVar3 = FUN_00752150(4), cVar3 == '\0')) {
        return;
      }
      if (piVar1[lVar6 * 2 + 5] != -1) {
        lVar4 = FUN_002a00c0();
        *(undefined8 *)(puVar5 + -6) = *(undefined8 *)(lVar4 + 0x1c);
        *(undefined1 *)(puVar5 + -4) = *(undefined1 *)(lVar4 + 0x24);
        *(undefined8 *)(puVar5 + -3) = *(undefined8 *)(lVar4 + 0x28);
        puVar5[-1] = *(undefined4 *)(lVar4 + 0x30);
        *puVar5 = *(undefined4 *)(lVar4 + 0x34);
      }
      puVar5 = puVar5 + 7;
      lVar6 = lVar6 + 1;
    } while ((int)lVar6 < 3);
  }
  return;
}

