
void FUN_001e55b0(long param_1)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  undefined8 uVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  
  *(undefined4 *)(param_1 + 0x18) = 0xffffffff;
  iVar3 = *(int *)(param_1 + 0x1c);
  lVar7 = 0;
  if (iVar3 != -1) {
    lVar7 = 0;
    do {
      if (*(long *)(param_1 + 0x10) != 0) break;
      iVar3 = FUN_000b83e0(iVar3);
      if (iVar3 == 2) {
        uVar4 = FUN_000b89f0();
        lVar5 = FUN_000ba9f0(uVar4,0,0,0x368);
        lVar6 = 0;
        if (lVar5 != 0) {
          FUN_001e5ec0(lVar5);
          lVar6 = lVar5;
        }
        uVar1 = *(undefined4 *)(param_1 + 0x1c);
        uVar4 = FUN_001e8640(param_1 + 0x48);
        FUN_001e5fb0(lVar6,uVar1,uVar4);
        *(long *)(param_1 + 0x10) = lVar6;
        lVar6 = FUN_000b7d80(*(undefined4 *)(param_1 + 0x1c));
        uVar2 = *(uint *)(*(long *)(lVar6 + 0x10) + 0x88);
        *(undefined4 *)(param_1 + 0x18) = *(undefined4 *)(param_1 + 0x1c);
        lVar7 = lVar7 + (ulong)uVar2;
      }
      iVar3 = FUN_000b9880(param_1 + 0x20);
      *(int *)(param_1 + 0x1c) = iVar3;
    } while (iVar3 != -1);
  }
  *(long *)(param_1 + 0x68) = lVar7;
  return;
}

