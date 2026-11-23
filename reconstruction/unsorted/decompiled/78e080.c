
void FUN_0078e080(short *param_1)

{
  char cVar1;
  undefined1 uVar2;
  short sVar3;
  int iVar4;
  long lVar5;
  undefined8 uVar6;
  undefined1 auVar7 [16];
  
  param_1[4] = 0;
  param_1[0] = 0;
  param_1[1] = 0;
  param_1[2] = 0;
  param_1[3] = 0;
  *param_1 = -1;
  param_1[1] = -1;
  param_1[2] = -0x100;
  param_1[3] = 0xff;
  *(undefined1 *)(param_1 + 4) = 0xff;
  iVar4 = FUN_0078b270();
  if ((iVar4 == 3) || (cVar1 = FUN_0075c600(), cVar1 != '\0')) {
    sVar3 = FUN_010167d0();
  }
  else {
    lVar5 = FUN_007642e0();
    sVar3 = -1;
    if (lVar5 != 0) {
      lVar5 = FUN_002a2980(lVar5);
      sVar3 = *(short *)(lVar5 + 0x680);
    }
  }
  *param_1 = sVar3;
  iVar4 = FUN_0078b270();
  sVar3 = -1;
  if ((iVar4 != 3) && (lVar5 = FUN_007642e0(), lVar5 != 0)) {
    lVar5 = FUN_002a2980(lVar5);
    sVar3 = *(short *)(lVar5 + 0x682);
  }
  if (sVar3 != *param_1) {
    param_1[1] = sVar3;
    sVar3 = *param_1;
  }
  if (sVar3 != -1) {
    lVar5 = FUN_00269050();
    cVar1 = '\0';
    if (lVar5 != 0) {
      uVar6 = FUN_005494c0();
      auVar7 = FUN_00549bf0(uVar6,*(undefined1 *)(lVar5 + 0xa2));
      if ((auVar7._0_8_ != 0) && (auVar7._8_8_ != 0)) {
        cVar1 = *(char *)(auVar7._8_8_ + 0xb0);
      }
    }
    *(char *)(param_1 + 2) = cVar1;
    uVar2 = 1;
    if (cVar1 != '\x03') {
      if (cVar1 == '\x01') {
        uVar2 = 2;
      }
      else {
        uVar2 = 0;
      }
    }
    *(undefined1 *)(param_1 + 3) = uVar2;
  }
  uVar2 = FUN_0078b270();
  *(undefined1 *)((long)param_1 + 5) = uVar2;
  uVar2 = FUN_007528d0();
  *(undefined1 *)((long)param_1 + 7) = uVar2;
  uVar2 = FUN_0078b250();
  *(undefined1 *)(param_1 + 4) = uVar2;
  return;
}

