
void FUN_0058d940(long param_1)

{
  char cVar1;
  long lVar2;
  long lVar3;
  undefined2 *puVar4;
  
  lVar2 = FUN_0057d940();
  puVar4 = (undefined2 *)(lVar2 + 0x18);
  lVar2 = 0;
  do {
    lVar3 = *(long *)(puVar4 + -4);
    if (lVar3 == 0) {
      if (*(char *)(param_1 + lVar2) != '\0') {
        FUN_009140b0(param_1 + 0xe38 + lVar2);
        FUN_009140e0(param_1 + 0xe3c + lVar2);
        *(undefined1 *)(param_1 + lVar2) = 0;
        *(undefined8 *)(param_1 + 8 + lVar2) = 0;
        FUN_0054ded0(param_1 + 0x18 + lVar2);
        *(undefined4 *)(param_1 + 0xe38 + lVar2) = 0xffffffff;
        *(undefined4 *)(param_1 + 0xe3c + lVar2) = 0xffffffff;
        *(undefined8 *)(param_1 + 0xe40 + lVar2) = 0;
        lVar3 = *(long *)(puVar4 + -4);
        if (lVar3 != 0) goto LAB_0058d9e0;
      }
    }
    else {
LAB_0058d9e0:
      if ((*(char *)(param_1 + lVar2) != '\0') && (lVar3 != *(long *)(param_1 + 8 + lVar2))) {
        FUN_009140b0(param_1 + 0xe38 + lVar2);
        FUN_009140e0(param_1 + 0xe3c + lVar2);
        *(undefined1 *)(param_1 + lVar2) = 0;
        *(undefined8 *)(param_1 + 8 + lVar2) = 0;
        FUN_0054ded0(param_1 + 0x18 + lVar2);
        *(undefined4 *)(param_1 + 0xe38 + lVar2) = 0xffffffff;
        *(undefined4 *)(param_1 + 0xe3c + lVar2) = 0xffffffff;
        *(undefined8 *)(param_1 + 0xe40 + lVar2) = 0;
      }
    }
    if ((*(char *)(param_1 + lVar2) == '\0') && (*(long *)(puVar4 + -4) != 0)) {
      *(long *)(param_1 + 8 + lVar2) = *(long *)(puVar4 + -4);
      *(undefined1 *)(param_1 + lVar2) = 1;
    }
    *(undefined2 *)(param_1 + 0x10 + lVar2) = *puVar4;
    puVar4 = puVar4 + 8;
    lVar2 = lVar2 + 0xe48;
    if ((int)lVar2 == 0x11da0) {
      lVar2 = 0;
      do {
        cVar1 = *(char *)(param_1 + lVar2);
        if (cVar1 != '\0') {
          if (cVar1 < '\x04') {
            FUN_0058dc90(param_1,param_1 + lVar2);
            cVar1 = *(char *)(param_1 + lVar2);
          }
          if (cVar1 == '\x04') {
            FUN_0058dde0();
          }
        }
        lVar2 = lVar2 + 0xe48;
      } while ((int)lVar2 != 0x11da0);
      return;
    }
  } while( true );
}

