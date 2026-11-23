
undefined8 FUN_00b49210(char *param_1,int param_2)

{
  int *piVar1;
  undefined8 uVar2;
  long lVar3;
  int iVar4;
  undefined2 *puVar5;
  long lVar6;
  
  uVar2 = 0;
  if (*param_1 != '\0') {
    if (*(int *)(DAT_0282ee90 + 0xf4) == param_2) {
      puVar5 = (undefined2 *)(DAT_0282ee90 + 0xf0);
    }
    else {
      puVar5 = (undefined2 *)0x0;
    }
    if (puVar5 != (undefined2 *)0x0) {
      *puVar5 = 0;
      *(byte *)(puVar5 + 1) = *(byte *)(puVar5 + 1) & 0xfe;
      lVar3 = DAT_0282ee90 + 0xd8;
      iVar4 = -1;
      do {
        iVar4 = iVar4 + 1;
        lVar6 = 0;
        if (3 < iVar4) break;
        piVar1 = (int *)(lVar3 + 0x40);
        lVar3 = lVar3 + 0x24;
        lVar6 = lVar3;
      } while (*piVar1 != *(int *)(puVar5 + 4));
      FUN_00b47e50(lVar6,0);
      uVar2 = 1;
    }
  }
  return uVar2;
}

