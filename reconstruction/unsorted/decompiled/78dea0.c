
int FUN_0078dea0(void)

{
  code *pcVar1;
  char cVar2;
  byte bVar3;
  int iVar4;
  uint uVar5;
  long lVar6;
  long *plVar7;
  undefined8 uVar8;
  
  lVar6 = FUN_005753c0(4);
  if (lVar6 != 0) {
    plVar7 = (long *)FUN_0025cbd0();
    pcVar1 = *(code **)(*plVar7 + 0x328);
    iVar4 = FUN_0078b270();
    if ((iVar4 == 3) || (cVar2 = FUN_0075c600(), cVar2 != '\0')) {
      uVar5 = FUN_010167d0();
    }
    else {
      lVar6 = FUN_007642e0();
      uVar5 = (uint)CONCAT62((int6)((ulong)lVar6 >> 0x10),0xffff);
      if (lVar6 != 0) {
        lVar6 = FUN_002a2980(lVar6);
        uVar5 = (uint)*(ushort *)(lVar6 + 0x680);
      }
    }
    lVar6 = (*pcVar1)(plVar7,uVar5);
    iVar4 = 4;
    if (lVar6 != 0) {
      uVar8 = FUN_00078970(&DAT_026bc3b8);
      bVar3 = FUN_0057ced0(uVar8);
      iVar4 = bVar3 + 5;
    }
    return iVar4;
  }
  return 7;
}

