
void FUN_0079bda0(long param_1)

{
  char cVar1;
  byte bVar2;
  int iVar3;
  undefined8 uVar4;
  long lVar5;
  int iVar6;
  undefined8 uVar7;
  undefined1 local_250 [40];
  char local_228 [512];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  FUN_0078e520(FUN_00754410,FUN_00754410,0,0,0);
  if (*(int *)(param_1 + 0x30) == 2) {
    iVar3 = FUN_002b01b0();
    if (iVar3 == 1) {
      iVar3 = FUN_002b01c0();
      uVar7 = 0x7c;
      if (iVar3 != -1) {
        switch(iVar3) {
        case 4:
          uVar7 = 0x7f;
          break;
        case 6:
          uVar7 = 0x80;
          break;
        case 7:
switchD_0079be87_caseD_7:
          uVar7 = 0x7d;
          iVar3 = 7;
          break;
        case 8:
          uVar7 = 0x7e;
        }
switchD_0079be87_caseD_5:
        uVar4 = FUN_002b01d0(iVar3);
        FUN_00783ee0(0x19,uVar7,uVar4);
        *(undefined8 *)(param_1 + 0x30) = 0;
      }
    }
    else if (iVar3 - 2U < 2) {
LAB_0079bee4:
      *(undefined4 *)(param_1 + 0x30) = 3;
      if (*(char *)(param_1 + 0x38) != '\0') {
        FUN_00788e10(10);
      }
    }
  }
  else if (*(int *)(param_1 + 0x30) == 1) {
    cVar1 = FUN_002a93a0(&DAT_02655df8,local_228);
    if (cVar1 == '\0') {
      cVar1 = FUN_007525a0();
      if (cVar1 != '\0') {
        iVar3 = 0;
        uVar7 = 0x7c;
        goto switchD_0079be87_caseD_5;
      }
      cVar1 = FUN_001e8e90();
      if (cVar1 == '\0') {
        FUN_00783ee0(0x19,0x42,s_Could_not_obtain_content_manifes_0165b8fb);
        *(undefined4 *)(param_1 + 0x30) = 0;
      }
      else {
        FUN_00783ed0(0xe);
        *(undefined4 *)(param_1 + 0x30) = 0;
      }
    }
    else {
      if (local_228[0] == '\0') {
        cVar1 = FUN_007525a0();
        if (cVar1 != '\0') goto switchD_0079be87_caseD_7;
        goto LAB_0079bee4;
      }
      uVar7 = FUN_002a9430(&DAT_02655df8);
      FUN_002b08f0(local_228,uVar7,DAT_018dcaec);
      *(undefined4 *)(param_1 + 0x30) = 2;
    }
  }
  switch(*(undefined4 *)(param_1 + 0x34)) {
  case 1:
    iVar3 = FUN_000b9080();
    if (iVar3 == 0) {
      FUN_000b9350(0);
      FUN_000b9350(1);
      FUN_000b9350(2);
      FUN_000b9350(3);
      FUN_000b9350(4);
      *(undefined4 *)(param_1 + 0x34) = 2;
    }
    break;
  case 2:
    iVar3 = FUN_000b9080();
    if ((iVar3 != 0) || (*(int *)(param_1 + 0x30) != 3)) break;
    iVar3 = FUN_000b9710(2,local_250);
    if (iVar3 != -1) {
      iVar6 = 0;
      do {
        bVar2 = FUN_000b8320(iVar3);
        iVar6 = iVar6 + (bVar2 ^ 1);
        iVar3 = FUN_000b9880(local_250);
      } while (iVar3 != -1);
      if (iVar6 != 0) {
        FUN_00784e50(0x19,0x112);
        goto LAB_0079c1ac;
      }
    }
    FUN_001e3500();
    FUN_001e35a0(DAT_015c3bac);
    FUN_001e35a0(DAT_015c3bb0);
    FUN_001e3990(0);
    FUN_001e3990(1);
    FUN_001e3990(2);
    FUN_001e3990(3);
    FUN_001e3990(4);
    *(undefined4 *)(param_1 + 0x34) = 3;
    break;
  case 3:
    FUN_001e35f0();
    iVar3 = FUN_001e3970();
    if (iVar3 == 1) {
      FUN_001e35c0();
      FUN_001eaf60();
      FUN_001eb230(0);
      FUN_001eb230(1);
      FUN_001eb230(2);
      FUN_001eb230(3);
      FUN_001eb230(4);
      *(undefined4 *)(param_1 + 0x34) = 4;
      break;
    }
    if (iVar3 != 3) break;
    FUN_001e35c0();
LAB_0079c150:
    *(undefined4 *)(param_1 + 0x34) = 1;
    FUN_000b91b0();
    break;
  case 4:
    FUN_001eb050();
    iVar3 = FUN_001eb210();
    if (iVar3 != 1) {
      if (iVar3 != 3) break;
      FUN_001eafa0();
      goto LAB_0079c150;
    }
    FUN_001eafa0();
    FUN_001e8c80();
    iVar3 = FUN_001e8e60();
    if (iVar3 != 2) {
      *(undefined4 *)(param_1 + 0x34) = 5;
      if (*(char *)(param_1 + 0x38) != '\0') {
        FUN_00788e10(0xc);
      }
      break;
    }
    FUN_00784e50(0x19,0x82);
    goto LAB_0079c1ac;
  case 5:
    FUN_001e8e40();
    iVar3 = FUN_001e8e60();
    if (iVar3 != 0) break;
    FUN_000ba160();
    lVar5 = FUN_001e8e70();
    if (lVar5 == 0) {
      iVar3 = FUN_002f10c0();
      if (iVar3 == 0) {
        FUN_002f1080();
        *(undefined4 *)(param_1 + 0x34) = 6;
        if (*(char *)(param_1 + 0x38) != '\0') {
          FUN_00788e10(0xb);
        }
      }
      else {
        *(undefined4 *)(param_1 + 0x34) = 7;
      }
      break;
    }
    FUN_00784e50(0x19,0x111);
    goto LAB_0079c1ac;
  case 6:
    iVar3 = FUN_002f10c0();
    if ((iVar3 != 1) && (*(undefined4 *)(param_1 + 0x34) = 7, *(char *)(param_1 + 0x38) != '\0')) {
      FUN_00788e10(10);
    }
    break;
  case 7:
    cVar1 = FUN_001e8e90();
    if (cVar1 != '\0') {
      FUN_00783ed0(0xe);
      break;
    }
    iVar3 = FUN_002a8fa0(&DAT_02655df8);
    if (iVar3 == 3) {
      uVar7 = 0x12;
    }
    else {
      cVar1 = FUN_002a9080(&DAT_02655df8);
      if (cVar1 == '\0') break;
      uVar7 = 0x11;
    }
    FUN_00783ed0(uVar7);
LAB_0079c1ac:
    *(undefined4 *)(param_1 + 0x34) = 8;
  }
  if (*DAT_01a1f100 != local_28) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

