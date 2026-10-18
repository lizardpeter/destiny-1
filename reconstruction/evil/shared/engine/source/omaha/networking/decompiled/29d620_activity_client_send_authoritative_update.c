
bool FUN_0029d620(long *param_1)

{
  long *plVar1;
  code *pcVar2;
  char cVar3;
  char cVar4;
  undefined1 uVar5;
  undefined8 uVar6;
  long lVar7;
  undefined1 auStack_1e018 [122632];
  undefined1 local_110 [20];
  undefined4 local_fc;
  int local_f0;
  int local_e0;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_fc = 1;
  FUN_00072240(local_110,auStack_1e018,0x1df00);
  FUN_000723b0(local_110,1);
  cVar3 = FUN_002c9d20(param_1 + 0xce9,param_1 + 0xd2d,*DAT_0191a300,local_110,param_1 + 0xd71,1);
  FUN_00072560(local_110,0);
  cVar4 = '\0';
  if (cVar3 != '\0') {
    plVar1 = (long *)param_1[0x1ca];
    pcVar2 = *(code **)(*plVar1 + 0x30);
    uVar6 = (**(code **)(*param_1 + 0x10))(param_1);
    cVar4 = (*pcVar2)(plVar1,uVar6,0x15,auStack_1e018,
                      (int)(((uint)(local_f0 + 7 + local_e0 >> 0x1f) >> 0x1d) + 7 +
                           local_f0 + local_e0) >> 3,*(undefined4 *)((long)param_1 + 0x6c6c));
    if (cVar4 != '\0') {
      lVar7 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar7 = FUN_000694d0();
      }
      param_1[0x1c9] = lVar7;
    }
  }
  if (*DAT_01a1f100 != local_38) {
    uVar5 = thunk_FUN_012aa7f6();
    return (bool)uVar5;
  }
  return cVar4 != '\0';
}

