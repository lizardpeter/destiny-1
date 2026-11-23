
void FUN_00769da0(int *param_1)

{
  undefined4 uVar1;
  char *pcVar2;
  long *plVar3;
  undefined8 uVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  uint uVar8;
  ushort uVar9;
  int iVar10;
  bool bVar11;
  long local_c0;
  undefined1 local_b8 [8];
  undefined4 local_b0;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  if ((char)param_1[2] == '\0') {
    local_c0 = FUN_00775180(param_1[1]);
  }
  else {
    local_c0 = FUN_00772ec0();
  }
  FUN_00768bc0(param_1);
  if (*param_1 != 2) goto switchD_00769e27_caseD_4;
  uVar8 = *(uint *)(local_c0 + 0x8c48);
  if ((uVar8 < 0xb) && ((0x7f0U >> (uVar8 & 0x1f) & 1) != 0)) {
    switch(uVar8) {
    case 3:
    case 5:
    case 7:
      goto switchD_00769e27_caseD_3;
    default:
      goto switchD_00769e27_caseD_4;
    case 8:
      pcVar2 = (char *)(local_c0 + 0x8c50);
      break;
    case 9:
      pcVar2 = (char *)(local_c0 + 0x8c54);
    }
    if (*pcVar2 == '\0') goto switchD_00769e27_caseD_4;
  }
switchD_00769e27_caseD_3:
  plVar3 = (long *)FUN_0075d560(0,0);
  if (plVar3 != (long *)0x0) {
    uVar4 = (**(code **)(*plVar3 + 0x10))(plVar3);
    lVar5 = FUN_00b0c560(*param_1);
    if ((*(byte *)(lVar5 + 0x1b9) & 1) == 0) {
      iVar10 = 1;
      lVar5 = FUN_007756e0(1);
      if (lVar5 != 0) {
        iVar10 = *(int *)(&DAT_00001c50 + lVar5);
      }
    }
    else {
      iVar10 = *(int *)(lVar5 + 0x28);
    }
    uVar1 = FUN_00b0c580(*param_1);
    FUN_00774690(uVar4,iVar10 + -1,uVar1,&local_c0);
    if (local_c0 != 0) {
      lVar6 = FUN_007757d0(2);
      local_b0 = 0;
      lVar5 = *(long *)(PTR_DAT_0197e288 + 8);
      uVar4 = FUN_000e8680(lVar5,0,0xffffffff);
      thunk_FUN_012aa986(local_b8,0,uVar4);
      uVar9 = *(ushort *)(lVar5 + 0x1c) & 0x78;
      bVar11 = uVar9 != 0;
      if (uVar9 == 0) {
        uVar8 = *(uint *)(lVar5 + 0x20);
        if ((*(ushort *)(lVar5 + 0x1c) & 0x40) != 0) {
          lVar7 = FUN_000e8a90(lVar5,local_b8);
          if (lVar7 == 0) {
            uVar8 = uVar8 | 0x5488bf;
          }
          else {
            uVar8 = *(uint *)(lVar7 + 0x20) & 0x5488bf | uVar8;
          }
        }
        bVar11 = (uVar8 & 0xc08070) != 0;
      }
      if (bVar11) {
        FUN_000e6730(lVar5,local_b8,0,0xffffffff,0);
      }
      FUN_00b8e0b0(lVar6 + 0x9b8);
      FUN_00b8dcf0(lVar6 + 0x9b8,local_b8);
      FUN_00774b10(3,3);
    }
  }
switchD_00769e27_caseD_4:
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

