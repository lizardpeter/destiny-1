
undefined1 FUN_00953940(int *param_1)

{
  char cVar1;
  long lVar2;
  int *piVar3;
  undefined1 uVar4;
  char cVar5;
  int iVar6;
  long lVar7;
  int *piVar8;
  uint uVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined4 local_3c;
  undefined8 local_38;
  
  lVar2 = DAT_0274bfa0;
  if ((*DAT_0265b510 & 2) != 0) {
    uVar4 = FUN_002b1670(DAT_0265b510,s_user_interface_networking_handle_0166d369,param_1,0x20,
                         thunk_FUN_00953940);
    return uVar4;
  }
  uVar9 = 0xffffffff;
  uVar4 = 0;
  piVar3 = &DAT_0274be90;
  do {
    piVar8 = piVar3;
    uVar9 = uVar9 + 1;
    if (4 < uVar9) goto LAB_00953aea;
    piVar3 = piVar8 + 4;
  } while (*piVar8 != *param_1);
  if (piVar8 + 4 == (int *)(s__libexec_ld_elf_so_1_00000000 + 0x10)) goto LAB_00953aea;
  uVar4 = 1;
  if (piVar8[(long)param_1[6] + 1] == 2) {
    local_38 = *(undefined8 *)(DAT_0274bfa0 + 0x110);
    local_3c = *(undefined4 *)(DAT_0274bfa0 + 0xb8);
    cVar1 = *(char *)(DAT_0274bfa0 + 0xb4);
    cVar5 = FUN_00b21010();
    if ((cVar5 == '\0') && (cVar5 = FUN_00b21030(), cVar5 == '\0')) goto LAB_00953aea;
    uVar11 = 3;
    if (cVar1 == '\0') {
      uVar11 = 2;
    }
    lVar7 = FUN_007756e0(1);
    uVar10 = uVar11;
    if (lVar7 != 0) {
      iVar6 = FUN_00b81560(lVar7,lVar2 + 0xc4);
      uVar10 = 1;
      if (iVar6 == -1) {
        uVar10 = uVar11;
      }
    }
    uVar11 = 0;
  }
  else {
    if (piVar8[(long)param_1[6] + 1] != 1) goto LAB_00953aea;
    local_38 = *(undefined8 *)(DAT_0274bfa0 + 0x110);
    local_3c = *(undefined4 *)(DAT_0274bfa0 + 0xb8);
    cVar1 = *(char *)(DAT_0274bfa0 + 0xb4);
    cVar5 = FUN_00b21010();
    if ((cVar5 == '\0') && (cVar5 = FUN_00b21030(), cVar5 == '\0')) goto LAB_00953aea;
    uVar11 = 3;
    if (cVar1 == '\0') {
      uVar11 = 2;
    }
    lVar7 = FUN_007756e0(1);
    uVar10 = uVar11;
    if (lVar7 != 0) {
      iVar6 = FUN_00b81560(lVar7,lVar2 + 0xc4);
      uVar10 = 1;
      if (iVar6 == -1) {
        uVar10 = uVar11;
      }
    }
    uVar11 = 1;
  }
  FUN_00b21600(0,uVar11,uVar10,local_3c,lVar2 + 0xbc,local_38);
LAB_00953aea:
  *(undefined4 *)(lVar2 + 0xb0) = 0x811c9dc5;
  return uVar4;
}

