
void FUN_00586000(long param_1)

{
  long lVar1;
  undefined1 uVar2;
  char cVar3;
  long *plVar4;
  undefined8 uVar5;
  long *plVar6;
  undefined8 uVar7;
  long lVar8;
  
  plVar6 = (long *)(param_1 + 0x10);
  lVar1 = param_1 + 0x30;
  plVar4 = (long *)FUN_00057f80(lVar1);
  lVar8 = *(long *)(param_1 + 0x10);
  if (lVar8 == *plVar4) {
    if ((lVar8 != 0) && (*(char *)(param_1 + 0x29) != '\0')) {
      uVar5 = FUN_0056b260();
      FUN_0056bd50(uVar5,3,plVar6);
      uVar5 = FUN_0056b260();
      FUN_0056bcd0(uVar5,3,plVar6,0);
      *(undefined1 *)(param_1 + 0x29) = 0;
    }
  }
  else {
    if (*plVar4 != 0) {
      uVar5 = FUN_0056b260();
      FUN_0056bd50(uVar5,4,plVar4);
      uVar5 = FUN_0056b260();
      FUN_0056bd50(uVar5,3,plVar4);
      lVar8 = *plVar6;
    }
    if (lVar8 == 0) {
      FUN_0058bcf0(lVar1);
    }
    else {
      uVar5 = FUN_0056b260();
      FUN_0056bcd0(uVar5,4,plVar6,1);
      uVar5 = FUN_0056b260();
      FUN_0056bcd0(uVar5,3,plVar6,0);
      *(undefined1 *)(param_1 + 0x29) = 0;
      lVar8 = FUN_0034e490();
      FUN_0058bd10(lVar1,plVar6,*(undefined4 *)(lVar8 + 0x34));
    }
  }
  plVar6 = (long *)FUN_00057f80(lVar1);
  if (*plVar6 != 0) {
    uVar5 = FUN_0056b260();
    uVar7 = FUN_00057f80(lVar1);
    uVar2 = FUN_0056bf10(uVar5,4,uVar7);
    lVar8 = FUN_0034e490();
    FUN_0058bd40(lVar1,uVar2,*(undefined4 *)(lVar8 + 0x34));
    lVar8 = FUN_0034e490();
    if (*(char *)(lVar8 + 0x30) != '\0') {
      cVar3 = FUN_0058bd30(lVar1);
      if (cVar3 != '\0') {
        *(undefined1 *)(param_1 + 0x41c) = 1;
      }
    }
  }
  return;
}

