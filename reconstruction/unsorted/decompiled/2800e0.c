
ulong FUN_002800e0(short param_1)

{
  char cVar1;
  long *plVar2;
  int *piVar3;
  long lVar4;
  int iVar5;
  undefined8 unaff_R12;
  ulong uVar6;
  undefined6 uVar7;
  
  cVar1 = FUN_0025cc10();
  uVar7 = (undefined6)((ulong)unaff_R12 >> 0x10);
  uVar6 = CONCAT62(uVar7,0xffff);
  if (cVar1 != '\0') {
    plVar2 = (long *)FUN_0025cbd0();
    piVar3 = (int *)(**(code **)(*plVar2 + 0x248))(plVar2);
    uVar6 = CONCAT62(uVar7,0xffff);
    do {
      iVar5 = (int)uVar6 + 1;
      if (*piVar3 <= (int)(short)iVar5) {
        uVar6 = 0xffff;
        break;
      }
      plVar2 = (long *)FUN_0025cbd0();
      lVar4 = (**(code **)(*plVar2 + 0x4d0))(plVar2,iVar5);
      uVar6 = (ulong)((int)uVar6 + 1);
    } while (*(short *)(lVar4 + 0x10) != param_1);
  }
  return uVar6 & 0xffff;
}

