
void FUN_00574c00(long param_1)

{
  char cVar1;
  char cVar2;
  int iVar3;
  long *plVar4;
  long lVar5;
  undefined1 *puVar6;
  long lVar7;
  long lVar8;
  
  plVar4 = (long *)FUN_005753c0(4);
  lVar5 = FUN_00775770(0);
  if (lVar5 != 0) {
    lVar5 = lVar5 + 0x9b8;
    cVar1 = FUN_00b8f690(lVar5);
    if (cVar1 != '\0') {
      puVar6 = (undefined1 *)FUN_011c3f80(lVar5);
      lVar7 = FUN_00b8e190(lVar5);
      lVar8 = FUN_00b8e1f0(lVar5);
      iVar3 = FUN_00b8e220(lVar5);
      if ((*(short *)(puVar6 + 2) != -1) &&
         ((((*(short *)(param_1 + 0x8e) != *(short *)(puVar6 + 2) ||
            (*(char *)(param_1 + 0x90) != puVar6[4])) || (*(long *)(param_1 + 0x118) != lVar7)) ||
          ((*(long *)(param_1 + 0x120) != lVar8 || (*(int *)(param_1 + 0x128) != iVar3)))))) {
        *(undefined1 *)(param_1 + 0x8c) = *puVar6;
        *(undefined2 *)(param_1 + 0x8e) = *(undefined2 *)(puVar6 + 2);
        *(undefined1 *)(param_1 + 0x90) = puVar6[4];
        lVar5 = 0;
        *(undefined2 *)(param_1 + 0x92) = *(undefined2 *)(puVar6 + 6);
        *(undefined4 *)(param_1 + 0x94) = *(undefined4 *)(puVar6 + 8);
        do {
          *(undefined2 *)(param_1 + 0x98 + lVar5 * 4) = *(undefined2 *)(puVar6 + lVar5 * 4 + 0xc);
          *(undefined2 *)(param_1 + 0x9a + lVar5 * 4) = *(undefined2 *)(puVar6 + lVar5 * 4 + 0xe);
          lVar5 = lVar5 + 1;
        } while (lVar5 != 0x20);
        *(long *)(param_1 + 0x118) = lVar7;
        *(long *)(param_1 + 0x120) = lVar8;
        *(int *)(param_1 + 0x128) = iVar3;
      }
    }
  }
  if (plVar4 != (long *)0x0) {
    cVar1 = FUN_00546f20(plVar4);
    cVar2 = (**(code **)(*plVar4 + 0x58))(plVar4);
    if ((cVar2 != '\0') &&
       (lVar5 = (**(code **)(*plVar4 + 0x10))(plVar4), *(char *)(lVar5 + 0x714c) != '\0')) {
      cVar1 = '\0';
    }
    if (cVar1 != '\0') {
      FUN_00774f70();
    }
    if (cVar1 != *(char *)(param_1 + 300)) {
      (**(code **)(*plVar4 + 0x58))(plVar4);
      (**(code **)(*plVar4 + 0x10))(plVar4);
    }
    *(char *)(param_1 + 300) = cVar1;
  }
  return;
}

