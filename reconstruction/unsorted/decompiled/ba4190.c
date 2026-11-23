
char FUN_00ba4190(undefined8 param_1,uint *param_2)

{
  undefined1 uVar1;
  char cVar2;
  char cVar3;
  uint uVar4;
  bool bVar5;
  
  uVar4 = FUN_00072c70(param_1,5);
  *param_2 = uVar4;
  FUN_000730b0(param_1,param_2 + 1,0x40);
  uVar4 = FUN_00072c70(param_1,3);
  cVar3 = '\0';
  param_2[3] = uVar4;
  if (((*param_2 < 0x14) && (-1 < (int)uVar4)) && ((int)uVar4 < 5)) {
    if (uVar4 == 0) {
      uVar1 = FUN_00073430(param_1);
      *(undefined1 *)(param_2 + 4) = uVar1;
      uVar4 = param_2[3];
    }
    cVar3 = true;
    if (uVar4 == 3) {
      uVar1 = FUN_00073430(param_1);
      *(undefined1 *)(param_2 + 0xe) = uVar1;
      uVar1 = FUN_00073430(param_1);
      *(undefined1 *)((long)param_2 + 0x39) = uVar1;
      if ((char)param_2[0xe] == '\0') {
        FUN_000730b0(param_1,(long)param_2 + 0x11,0x40);
        uVar4 = FUN_00072c70(param_1,DAT_028a5ea0);
        param_2[7] = uVar4;
        uVar4 = FUN_00072c70(param_1,2);
        param_2[8] = uVar4;
        FUN_000730b0(param_1,param_2 + 10,0x40);
        FUN_000730b0(param_1,param_2 + 0xc,0x40);
        cVar3 = false;
        if (param_2[7] == 0) {
          cVar3 = param_2[8] < 4;
        }
      }
      else {
        *(undefined8 *)((long)param_2 + 0x11) = 0;
        param_2[7] = 0xffffffff;
        param_2[8] = 0xffffffff;
      }
    }
    uVar4 = param_2[3];
    if (uVar4 - 3 < 2) {
      bVar5 = (bool)cVar3 != false;
      cVar3 = '\0';
      if ((bVar5) && (cVar2 = FUN_00ae1760(param_1,param_2 + 0x10,0), cVar2 != '\0')) {
        cVar3 = FUN_00ae17a0(param_1,param_2 + 0x34,0);
      }
      uVar4 = param_2[3];
    }
    if (uVar4 == 1) {
      uVar4 = FUN_00072c70(param_1,5);
      param_2[0x3e] = uVar4;
      FUN_000730b0(param_1,param_2 + 0x3f,0x40);
      bVar5 = cVar3 != '\0';
      cVar3 = '\0';
      if ((bVar5) && (param_2[0x3e] < 0x14)) {
        cVar3 = param_2[0x3e] != *param_2;
      }
    }
  }
  return cVar3;
}

