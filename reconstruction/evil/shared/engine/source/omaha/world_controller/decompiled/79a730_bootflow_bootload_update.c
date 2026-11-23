
/* WARNING: Type propagation algorithm not settling */

void FUN_0079a730(long param_1)

{
  code *pcVar1;
  undefined1 uVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  char *pcVar7;
  undefined8 in_R9;
  ulong local_260 [3];
  undefined4 local_248 [2];
  ulong local_240;
  undefined8 local_238;
  undefined1 local_138 [256];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  switch(*(undefined4 *)(param_1 + 0x30)) {
  case 0:
    cVar3 = FUN_000014d0();
    if (cVar3 == '\0') {
      *(undefined4 *)(param_1 + 0x30) = 5;
      goto switchD_0079a771_caseD_5;
    }
    *(undefined4 *)(param_1 + 0x30) = 1;
  case 1:
    FUN_00087ad0(&local_240);
    FUN_00087c90(&local_240,3,s_unpatchable_packages_0165b4f6);
    cVar3 = FUN_0008adb0(&local_240);
    if (cVar3 == '\0') {
      if (DAT_01a231f0 == (code *)0x0) {
        FUN_0005c750(s_unable_to_create_unpatchable_pac_0165b50b);
        s__libexec_ld_elf_so_1_00000000[1] = '*';
        s__libexec_ld_elf_so_1_00000000[2] = '\0';
        s__libexec_ld_elf_so_1_00000000[3] = '\0';
        s__libexec_ld_elf_so_1_00000000[4] = '\0';
      }
      else {
        (*DAT_01a231f0)(1,s_unable_to_create_unpatchable_pac_0165b50b);
      }
    }
    FUN_00088af0(&local_240,0x1d,local_138,0x100);
    uVar5 = FUN_00087f90(&local_240);
    uVar5 = FUN_00082d50(uVar5,local_138);
    *(undefined4 *)(param_1 + 0x110) = uVar5;
    FUN_00084750(uVar5);
    *(undefined4 *)(param_1 + 0x30) = 2;
    break;
  case 2:
    iVar4 = FUN_00084750(*(undefined4 *)(param_1 + 0x110));
    if (iVar4 == 1) break;
    if (iVar4 == 4) {
      *(undefined4 *)(param_1 + 0x30) = 3;
      break;
    }
    if (DAT_01a231f0 != (code *)0x0) {
      pcVar7 = s_unable_to_open_async_unpatchable_0165b53a;
LAB_0079ad87:
      uVar6 = 1;
      goto LAB_0079ad8c;
    }
    pcVar7 = s_unable_to_open_async_unpatchable_0165b53a;
    goto LAB_0079ae51;
  case 3:
    local_238 = CONCAT44(DAT_025d11c8._4_4_,(undefined4)DAT_025d11c8);
    local_240 = DAT_025d11c0;
    uVar6 = FUN_000fb400(8,*(undefined4 *)(param_1 + 0x100),DAT_025d12ae,DAT_025d11c0,
                         (undefined4)DAT_025d11c8,in_R9,DAT_025d11c0,local_238,DAT_025d11c0,
                         CONCAT44(DAT_025d11c8._4_4_,(undefined4)DAT_025d11c8),DAT_025d11c0,
                         CONCAT44(DAT_025d11c8._4_4_,(undefined4)DAT_025d11c8));
    *(undefined8 *)(param_1 + 0x108) = uVar6;
    *(undefined4 *)(param_1 + 0x30) = 4;
    break;
  case 4:
    cVar3 = FUN_000fba50(*(undefined8 *)(param_1 + 0x108));
    if (cVar3 != '\0') {
      *(undefined4 *)(param_1 + 0x108) = 0;
      *(undefined4 *)(param_1 + 0x10c) = 0xffff;
      iVar4 = FUN_000837f0(*(undefined4 *)(param_1 + 0x110));
      if (iVar4 == 0) {
        if (DAT_01a231f0 != (code *)0x0) {
          (*DAT_01a231f0)(1,s_unabled_to_close_async_unpatchab_0165b56c);
          *(undefined4 *)(param_1 + 0x30) = 5;
          break;
        }
        FUN_0005c750(s_unabled_to_close_async_unpatchab_0165b56c);
        s__libexec_ld_elf_so_1_00000000[1] = '*';
        s__libexec_ld_elf_so_1_00000000[2] = '\0';
        s__libexec_ld_elf_so_1_00000000[3] = '\0';
        s__libexec_ld_elf_so_1_00000000[4] = '\0';
      }
      *(undefined4 *)(param_1 + 0x30) = 5;
    }
    break;
  case 5:
switchD_0079a771_caseD_5:
    uVar6 = FUN_0034cbb0();
    cVar3 = FUN_0034c960(uVar6);
    if (cVar3 == '\0') {
      FUN_000cdba0();
      local_240 = local_240 & 0xffffffffffffff00;
      FUN_000652e0(&local_240,0x100,&DAT_01616f06);
      local_138[0] = 0;
      FUN_010080a0(local_138,s__s__s_0165b7df,&local_240,PTR_s_client_bootstrap_unp4_0_01945e00);
      local_248[0] = 0x40;
      FUN_000cdbd0(local_138,local_248,0xffffffff,0);
      local_138[0] = 0;
      FUN_010080a0(local_138,s__s__s_0165b7df,&local_240,PTR_s_ui_startup_unp4_0_01945e08);
      local_248[0] = 0x40;
      FUN_000cdbd0(local_138,local_248,0xffffffff,0);
      local_138[0] = 0;
      FUN_010080a0(local_138,s__s__s_0165b7df,&local_240,PTR_s_ui_bootflow_unp4_0_01945e10);
      local_248[0] = 0x40;
      FUN_000cdbd0(local_138,local_248,0xffffffff,0);
      *(undefined4 *)(param_1 + 0x30) = 6;
    }
    break;
  case 6:
    iVar4 = FUN_000cdbb0();
    if (iVar4 != 3) {
      cVar3 = FUN_007525a0();
      pcVar1 = DAT_01a231f0;
      if ((iVar4 != 1) && (cVar3 == '\x01')) {
        uVar6 = FUN_000cfcb0(iVar4);
        if (pcVar1 == (code *)0x0) {
          FUN_0005c750(s_Unpatchable_package_registration_0165b5a0,uVar6,iVar4);
          s__libexec_ld_elf_so_1_00000000[1] = '*';
          s__libexec_ld_elf_so_1_00000000[2] = '\0';
          s__libexec_ld_elf_so_1_00000000[3] = '\0';
          s__libexec_ld_elf_so_1_00000000[4] = '\0';
        }
        else {
          (*pcVar1)(3,s_Unpatchable_package_registration_0165b5a0,uVar6,iVar4);
        }
      }
      FUN_00788db0(0);
      *(undefined4 *)(param_1 + 0x30) = 7;
    }
    break;
  case 7:
    uVar6 = FUN_00752ef0();
    local_260[2] = 0;
    FUN_007536f0(uVar6,local_260 + 2);
    if ((local_260[2] & 0x400000000) == 0) {
      *(undefined4 *)(param_1 + 0x30) = 8;
    }
    break;
  case 8:
    uVar6 = FUN_00752ef0();
    local_260[1] = 0;
    FUN_007536f0(uVar6,local_260 + 1);
    FUN_00752f10(uVar6,2);
    *(undefined4 *)(param_1 + 0x30) = 9;
    break;
  case 9:
    uVar6 = FUN_00752ef0();
    local_260[0] = 0;
    FUN_007536f0(uVar6,local_260);
    if ((local_260[0] & 0x4000000000000) == 0) {
      if (((local_260[0] & 0x400000000) == 0) && (cVar3 = FUN_00788df0(), cVar3 != '\0')) {
        cVar3 = FUN_00001f70();
        if (cVar3 == '\0') {
          *(undefined4 *)(param_1 + 0x30) = 0xe;
        }
        else {
          *(undefined4 *)(param_1 + 0x30) = 10;
        }
      }
      break;
    }
    if (DAT_01a231f0 != (code *)0x0) {
      pcVar7 = s_failed_to_load_bootstrap_unpatch_0165b5dc;
      uVar6 = 3;
LAB_0079ad8c:
      (*DAT_01a231f0)(uVar6,pcVar7);
      break;
    }
    pcVar7 = s_failed_to_load_bootstrap_unpatch_0165b5dc;
    goto LAB_0079ae51;
  case 10:
    FUN_00087ad0(&local_240);
    uVar2 = FUN_00001f70();
    FUN_00ab8090(&local_240,uVar2);
    cVar3 = FUN_0008adb0(&local_240);
    if (cVar3 == '\0') {
      if (DAT_01a231f0 == (code *)0x0) {
        FUN_0005c750(s_Unable_to_create_directory_0165b601);
        s__libexec_ld_elf_so_1_00000000[1] = '*';
        s__libexec_ld_elf_so_1_00000000[2] = '\0';
        s__libexec_ld_elf_so_1_00000000[3] = '\0';
        s__libexec_ld_elf_so_1_00000000[4] = '\0';
      }
      else {
        (*DAT_01a231f0)(1,s_Unable_to_create_directory_0165b601);
      }
    }
    FUN_00088af0(&local_240,0x1d,local_138,0x100);
    uVar5 = FUN_00087f90(&local_240);
    uVar5 = FUN_00082d50(uVar5,local_138);
    *(undefined4 *)(param_1 + 0xf8) = uVar5;
    iVar4 = FUN_00084750(uVar5);
    if ((iVar4 != 1) && (iVar4 != 4)) {
      FUN_000837f0(*(undefined4 *)(param_1 + 0xf8));
      uVar5 = FUN_00087f90(&local_240);
      uVar5 = FUN_00082d50(uVar5,local_138);
      *(undefined4 *)(param_1 + 0xf8) = uVar5;
    }
    *(undefined4 *)(param_1 + 0x30) = 0xb;
    break;
  case 0xb:
    iVar4 = FUN_00084750(*(undefined4 *)(param_1 + 0xf8));
    if (iVar4 == 1) break;
    if (iVar4 == 4) {
      cVar3 = FUN_00788df0();
      if (cVar3 != '\0') {
        *(undefined4 *)(param_1 + 0x30) = 0xc;
      }
      break;
    }
    if (DAT_01a231f0 != (code *)0x0) {
      pcVar7 = s_Unable_to_open_async_location_0165b61c;
      goto LAB_0079ad87;
    }
    pcVar7 = s_Unable_to_open_async_location_0165b61c;
LAB_0079ae51:
    FUN_0005c750(pcVar7);
    s__libexec_ld_elf_so_1_00000000[1] = '*';
    s__libexec_ld_elf_so_1_00000000[2] = '\0';
    s__libexec_ld_elf_so_1_00000000[3] = '\0';
    s__libexec_ld_elf_so_1_00000000[4] = '\0';
    break;
  case 0xc:
    FUN_0079af70(param_1);
    *(undefined4 *)(param_1 + 0x30) = 0xd;
    break;
  case 0xd:
    cVar3 = FUN_0079b4c0(param_1);
    if (cVar3 != '\0') {
      FUN_00087ad0(&local_240);
      uVar2 = FUN_00001f70();
      FUN_00ab8090(&local_240,uVar2);
      FUN_00088af0(&local_240,0x1d,local_138,0x100);
      iVar4 = FUN_000837f0(*(undefined4 *)(param_1 + 0xf8));
      if (iVar4 == 0) {
        if (DAT_01a231f0 != (code *)0x0) {
          (*DAT_01a231f0)(1,s_Unabled_to_close_async_location_0165b63a);
          *(undefined4 *)(param_1 + 0x30) = 0xe;
          break;
        }
        FUN_0005c750(s_Unabled_to_close_async_location_0165b63a);
        s__libexec_ld_elf_so_1_00000000[1] = '*';
        s__libexec_ld_elf_so_1_00000000[2] = '\0';
        s__libexec_ld_elf_so_1_00000000[3] = '\0';
        s__libexec_ld_elf_so_1_00000000[4] = '\0';
      }
      *(undefined4 *)(param_1 + 0x30) = 0xe;
    }
    break;
  case 0xe:
    cVar3 = FUN_007525f0();
    if (cVar3 != '\0') {
      *(undefined4 *)(param_1 + 0x30) = 0xf;
    }
    break;
  case 0xf:
    cVar3 = FUN_007526d0();
    if (cVar3 != '\0') {
      uVar6 = thunk_FUN_0078f6f0();
      FUN_00754410(uVar6);
      *(undefined4 *)(param_1 + 0x30) = 0x10;
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

