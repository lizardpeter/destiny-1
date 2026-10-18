
void FUN_00ba32d0(long *param_1)

{
  char cVar1;
  undefined1 uVar2;
  byte bVar3;
  uint uVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  long lVar9;
  long lVar10;
  long lVar11;
  byte bVar12;
  long local_48;
  undefined1 local_40 [8];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (*param_1 != 0) {
    lVar9 = FUN_0029c3b0();
    lVar10 = FUN_0029c3b0(*param_1);
    uVar4 = FUN_002a55c0(lVar10 + 8);
    FUN_00ba2590(param_1[1],local_40);
    cVar1 = FUN_00ba25a0(param_1[1],local_40,&local_48);
    lVar10 = lVar9 + 8;
    if (cVar1 != '\0') {
      do {
        uVar5 = FUN_002a5520(lVar10,(long)param_1 + (long)*(int *)(local_48 + 0x5c) * 8 + 0x2c);
        if (*(int *)(local_48 + 0x70) == 0) {
          cVar1 = FUN_002a5450(lVar10,uVar5);
          lVar11 = param_1[1];
          if (cVar1 != '\0') goto LAB_00ba3394;
        }
        else {
          lVar11 = param_1[1];
LAB_00ba3394:
          FUN_00ba2490(lVar11,local_48);
          lVar11 = param_1[1];
        }
        cVar1 = FUN_00ba25a0(lVar11,local_40,&local_48);
      } while (cVar1 != '\0');
    }
    uVar6 = FUN_002a0870(lVar9);
    uVar7 = FUN_002a54d0(lVar10);
    if (uVar7 != 0xffffffff) {
      bVar12 = 1;
      do {
        bVar3 = bVar12;
        if (((uVar7 != uVar6) && ((uVar4 >> (uVar7 & 0x1f) & 1) != 0)) &&
           (cVar1 = FUN_002a5450(lVar10,uVar7), cVar1 == '\0')) {
          uVar2 = FUN_002a5490(lVar10,uVar7);
          bVar3 = FUN_00ba3770(param_1,uVar7,uVar2);
          if (bVar3 != 0) {
            bVar3 = bVar12;
          }
        }
        bVar12 = bVar3;
        uVar7 = FUN_002a5500(lVar10,uVar7);
      } while (uVar7 != 0xffffffff);
      if ((bVar12 & 1) == 0) goto LAB_00ba345c;
    }
    iVar8 = FUN_00057e60(lVar10);
    if (iVar8 != (int)param_1[0x1b]) {
      lVar9 = *param_1;
      uVar5 = FUN_00057e60(lVar10);
      FUN_0029b9f0(lVar9,uVar5);
      uVar5 = FUN_00057e60(lVar10);
      *(undefined4 *)(param_1 + 0x1b) = uVar5;
    }
  }
LAB_00ba345c:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

