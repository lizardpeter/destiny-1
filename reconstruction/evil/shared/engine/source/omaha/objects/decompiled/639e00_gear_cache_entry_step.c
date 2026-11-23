
int FUN_00639e00(long param_1,undefined4 param_2)

{
  long lVar1;
  byte bVar2;
  char cVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  int *piVar7;
  int iVar8;
  
  iVar6 = 0;
  iVar8 = 0;
  switch(param_2) {
  case 1:
    lVar1 = param_1 + 0xd4;
    if (*(int *)(param_1 + 0xd4) == -1) {
      cVar3 = FUN_0063c3a0(lVar1);
      iVar6 = iVar8;
      if (cVar3 != '\0') {
        FUN_0063b2b0(param_1 + 8,lVar1);
        FUN_0063b2b0(param_1 + 0x20,lVar1);
        FUN_0063b2b0(param_1 + 0x38,lVar1);
        FUN_0063b2b0(param_1 + 0x50,lVar1);
        FUN_0063b2b0(param_1 + 0x68,lVar1);
        FUN_0063b2b0(param_1 + 0x80,lVar1);
        FUN_0063b2b0(param_1 + 0x98,lVar1);
        FUN_0063b2b0(param_1 + 0xb0,lVar1);
        FUN_0063c3d0(lVar1,*(undefined4 *)(param_1 + 200),2);
        FUN_0063c3d0(lVar1,*(undefined4 *)(param_1 + 0xcc),2);
      }
    }
    else {
      iVar4 = FUN_0063c730(lVar1);
      if (iVar4 == 3) {
        iVar6 = 7;
      }
      else {
        iVar6 = iVar8;
        if ((iVar4 == 2) && (iVar6 = 6, *(int *)(param_1 + 4) != 3)) {
          iVar6 = 2;
        }
      }
    }
    break;
  case 2:
    bVar2 = FUN_006403f0(*(undefined8 *)(param_1 + 0x110),*(undefined8 *)(param_1 + 0x118));
    iVar6 = (uint)bVar2 + (uint)bVar2 * 2;
    break;
  case 3:
    if (*(int *)(param_1 + 0xd4) == -1) {
      cVar3 = FUN_0063c3a0();
      iVar6 = iVar8;
      if (cVar3 != '\0') {
        FUN_0063a5f0(param_1);
      }
    }
    else {
      iVar6 = FUN_0063c730(param_1 + 0xd4);
      if (iVar6 != 0) {
        if (iVar6 == 3) {
          FUN_00640460();
          FUN_00640480(0,*(undefined8 *)(param_1 + 0x110));
          FUN_00640480(1,*(undefined8 *)(param_1 + 0x118));
          *(undefined8 *)(param_1 + 0x118) = 0;
          *(undefined8 *)(param_1 + 0x110) = 0;
          return 7;
        }
        if (iVar6 != 2) {
          return 0;
        }
      }
      iVar6 = 4;
    }
    break;
  case 4:
    piVar7 = (int *)(param_1 + 0xdc);
    iVar8 = 0;
    do {
      iVar6 = 0;
      piVar5 = piVar7;
      do {
        if ((*piVar5 != -1) && (cVar3 = FUN_000e4050(), cVar3 == '\0')) {
          return 0;
        }
        piVar5 = piVar5 + 1;
        iVar6 = iVar6 + 1;
      } while (iVar6 < 4);
      piVar7 = piVar7 + 4;
      iVar8 = iVar8 + 1;
      iVar6 = 5;
    } while (iVar8 < 3);
    break;
  case 5:
    if ((*(int *)(param_1 + 0xd4) == -1) && (cVar3 = FUN_0063c3a0(param_1 + 0xd4), cVar3 != '\0')) {
      FUN_0063a3f0(param_1);
      FUN_00640460();
      FUN_00640480(1,*(undefined8 *)(param_1 + 0x118));
      *(undefined8 *)(param_1 + 0x118) = 0;
      iVar6 = 6;
    }
  }
  return iVar6;
}

