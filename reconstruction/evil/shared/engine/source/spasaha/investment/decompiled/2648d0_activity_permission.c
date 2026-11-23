
void FUN_002648d0(undefined4 param_1,long *param_2,undefined4 param_3,undefined1 *param_4,
                 undefined1 *param_5,undefined1 *param_6)

{
  char cVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined1 uVar4;
  long *plVar5;
  undefined8 extraout_RDX;
  undefined8 uVar6;
  bool bVar7;
  undefined1 auVar8 [16];
  
  plVar5 = (long *)FUN_0025a550();
  (**(code **)(*plVar5 + 0x38))(plVar5);
  cVar1 = (**(code **)(*param_2 + 0x58))(param_2);
  bVar7 = false;
  uVar6 = extraout_RDX;
  if (cVar1 != '\0') {
    auVar8 = (**(code **)(*param_2 + 0x10))(param_2);
    uVar6 = auVar8._8_8_;
    bVar7 = *(char *)(auVar8._0_8_ + 0x714c) != '\0';
  }
  uVar2 = FUN_002680a0(param_1,param_3,bVar7,uVar6,bVar7);
  uVar3 = FUN_00267ca0(param_2,param_3);
  uVar4 = FUN_00267b50(param_2,param_3);
  *param_4 = uVar2;
  *param_5 = uVar3;
  *param_6 = uVar4;
  return;
}

