
void FUN_007ad360(long param_1)

{
  long *plVar1;
  char cVar2;
  int iVar3;
  long lVar4;
  long lVar5;
  undefined8 uVar6;
  undefined2 uVar7;
  undefined2 uVar8;
  undefined4 local_3c;
  undefined2 local_38;
  undefined2 uStack_36;
  int iStack_34;
  undefined4 local_30;
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  lVar4 = FUN_00775770(0);
  local_30 = 0;
  uStack_36 = 0;
  iStack_34 = 0;
  local_38 = 0xffff;
  local_3c = 0;
  if ((*(int *)(param_1 + 0x30) - 5U < 2) || (*(int *)(param_1 + 0x30) == 0x119)) {
    cVar2 = FUN_00b8f690(lVar4 + 0x5a8);
    if (cVar2 != '\0') {
      lVar5 = FUN_011c4190(lVar4 + 0x5a8);
      if (*(short *)(lVar5 + 2) != -1) goto LAB_007ad3e5;
    }
    uVar6 = FUN_00574ef0();
    FUN_0078b550(uVar6);
  }
LAB_007ad3e5:
  cVar2 = FUN_00785300(0);
  if (cVar2 == '\0') {
LAB_007ad435:
    iStack_34 = 2;
    local_30 = 0;
  }
  else {
    cVar2 = FUN_00777570(0);
    if (cVar2 == '\0') goto LAB_007ad435;
    cVar2 = FUN_00b8f690(lVar4 + 0x5a8);
    uVar8 = 0xffff;
    uVar7 = 0xffff;
    if (cVar2 != '\0') {
      lVar5 = FUN_011c4190(lVar4 + 0x5a8,0xffff);
      uVar7 = *(undefined2 *)(lVar5 + 6);
      uVar8 = *(undefined2 *)(lVar5 + 2);
    }
    FUN_00547250(uVar8,uVar7,&local_38,&local_3c);
  }
  cVar2 = FUN_00b8f690(lVar4 + 0x5a8);
  if (cVar2 == '\0') {
LAB_007ad465:
    if (iStack_34 == 0) {
      iStack_34 = 1;
      local_30 = 0;
    }
  }
  else {
    lVar5 = FUN_011c4190(lVar4 + 0x5a8);
    if (*(short *)(lVar5 + 2) == -1) goto LAB_007ad465;
  }
  lVar5 = lVar4 + 0x8b8;
  cVar2 = FUN_00b8f6c0(lVar5);
  if (cVar2 != '\0') {
    iVar3 = thunk_FUN_012aa826(lVar4 + 0x99c,&local_38,0xc);
    if (iVar3 == 0) {
      cVar2 = FUN_00b8f690(lVar5);
      if (cVar2 != '\0') goto LAB_007ad4d0;
    }
    *(undefined2 *)(lVar4 + 0x99c) = local_38;
    *(ulong *)(lVar4 + 0x9a0) = CONCAT44(local_30,iStack_34);
    FUN_00b8f880(lVar5);
  }
LAB_007ad4d0:
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

