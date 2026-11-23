
void FUN_009cdd30(long param_1)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  long *plVar4;
  long lVar5;
  byte bVar6;
  
  FUN_009438f0();
  plVar4 = (long *)FUN_0078e990();
  if (plVar4 != (long *)0x0) {
    lVar5 = (**(code **)(*plVar4 + 0x60))(plVar4);
    *(byte *)(param_1 + 0x290) = *(byte *)(param_1 + 0x290) & 0xfe;
    uVar2 = (**(code **)(*plVar4 + 0x50))(plVar4);
    *(undefined4 *)(param_1 + 0x288) = uVar2;
    iVar3 = (**(code **)(*plVar4 + 0x58))(plVar4);
    *(int *)(param_1 + 0x28c) = iVar3;
    if (iVar3 == -1) {
      bVar6 = *(byte *)(param_1 + 0x290) & 0xfd;
    }
    else {
      bVar6 = *(byte *)(param_1 + 0x290) | 2;
    }
    *(byte *)(param_1 + 0x290) = bVar6;
    cVar1 = (**(code **)(*plVar4 + 0x48))(plVar4);
    if (cVar1 == '\0') {
      bVar6 = *(byte *)(param_1 + 0x290) & 0xfb;
    }
    else {
      bVar6 = *(byte *)(param_1 + 0x290) | 4;
    }
    *(byte *)(param_1 + 0x290) = bVar6;
    if (lVar5 != 0) {
      FUN_000663a0(lVar5,param_1 + 0x88,0x100,0);
      return;
    }
  }
  return;
}

