
void FUN_0079e740(long param_1)

{
  code *pcVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  undefined8 uVar6;
  undefined4 *puVar7;
  long lVar8;
  ulong uVar9;
  int iVar10;
  wchar16 *pwVar11;
  short sVar12;
  uint uVar13;
  undefined4 local_260 [2];
  undefined8 local_258;
  ulong uStack_250;
  undefined8 local_248;
  undefined1 local_240 [256];
  undefined1 local_140 [264];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar6 = FUN_0034cbb0();
  switch(*(undefined4 *)(param_1 + 0x30)) {
  case 0:
    cVar2 = FUN_0034c960(uVar6);
    if (cVar2 == '\0') {
      FUN_000cdba0();
      uVar6 = thunk_FUN_0078f6f0();
      iVar5 = FUN_002b0770();
      if (iVar5 != 0) {
        iVar10 = 0;
        do {
          puVar7 = (undefined4 *)FUN_002b08c0(iVar10);
          cVar2 = FUN_002b1300(*puVar7,0x10);
          if (((cVar2 == '\0') || (lVar8 = FUN_002b1270(*puVar7), *(char *)(lVar8 + 0xc4) != '\0'))
             || (iVar3 = FUN_000b9a00(*puVar7), iVar3 != -1)) {
            FUN_00087ad0(local_140);
            FUN_00087e90(local_140);
            FUN_000884f0(local_140,puVar7 + 1);
            FUN_00088af0(local_140,4,local_240,0x100);
            sVar12 = (short)puVar7[0x42];
            if ((*(char *)((long)puVar7 + 0x105) == '\0') ||
               ((puVar7[0x42] + 0x400 & 0xffff) - 0x40a < 0x17f6)) {
              cVar2 = FUN_007525a0();
              uVar4 = 2;
              if (cVar2 != '\0') {
                uVar4 = 0x2e;
              }
              local_258 = CONCAT44(local_258._4_4_,uVar4);
              FUN_0078af50(uVar6,local_240,&local_258,(int)sVar12,*(undefined8 *)(puVar7 + 0x44));
            }
            else {
              cVar2 = FUN_007525a0();
              if (cVar2 != '\0') {
                if (DAT_01a231f0 == (code *)0x0) {
                  FUN_0005c750(s_package_id__d_is_out_of_range__c_0165bb5c,(int)sVar12);
                  s__libexec_ld_elf_so_1_00000000[1] = '*';
                  s__libexec_ld_elf_so_1_00000000[2] = '\0';
                  s__libexec_ld_elf_so_1_00000000[3] = '\0';
                  s__libexec_ld_elf_so_1_00000000[4] = '\0';
                }
                else {
                  (*DAT_01a231f0)(3,s_package_id__d_is_out_of_range__c_0165bb5c);
                }
              }
            }
          }
          iVar10 = iVar10 + 1;
        } while (iVar5 != iVar10);
      }
      *(undefined4 *)(param_1 + 0x30) = 1;
    }
    break;
  case 1:
    iVar5 = FUN_000cdbb0();
    if (iVar5 == 3) break;
    cVar2 = FUN_007525a0();
    pcVar1 = DAT_01a231f0;
    if ((iVar5 != 1) && (cVar2 == '\x01')) {
      uVar6 = FUN_000cfcb0(iVar5);
      if (pcVar1 == (code *)0x0) {
        FUN_0005c750(s_Patchable_package_registration_f_0165bad6,uVar6,iVar5);
        s__libexec_ld_elf_so_1_00000000[1] = '*';
        s__libexec_ld_elf_so_1_00000000[2] = '\0';
        s__libexec_ld_elf_so_1_00000000[3] = '\0';
        s__libexec_ld_elf_so_1_00000000[4] = '\0';
      }
      else {
        (*pcVar1)(3,s_Patchable_package_registration_f_0165bad6,uVar6,iVar5);
      }
    }
    FUN_002b01f0();
    lVar8 = FUN_000ac660();
    if ((*(int *)(lVar8 + 0x94) != 1) &&
       (((*(int *)(lVar8 + 0x94) != 0 || (cVar2 = FUN_00084720(4), cVar2 == '\0')) ||
        (cVar2 = FUN_00084720(5), cVar2 != '\0')))) {
      *(undefined4 *)(param_1 + 0x30) = 5;
      break;
    }
    DAT_026cff08 = thunk_FUN_012aac96();
    *(undefined4 *)(param_1 + 0x30) = 2;
    FUN_00788e10(0xd);
    uVar13 = 0;
    goto LAB_0079eb88;
  case 2:
    lVar8 = thunk_FUN_012aac96();
    lVar8 = lVar8 - DAT_026cff08;
    uVar9 = thunk_FUN_012aac86();
    if (4999 < (ulong)(lVar8 * 1000) / uVar9) {
      FUN_000cdd10();
      *(undefined4 *)(param_1 + 0x30) = 3;
    }
    break;
  case 3:
    iVar5 = FUN_000cdd80();
    if (iVar5 == 1) {
      local_258 = 0x100000002;
      uStack_250 = 0x3f800000;
      local_248 = 0;
      FUN_0078ef60(3,&local_258);
      *(undefined4 *)(param_1 + 0x30) = 5;
      FUN_00084390(4);
      FUN_00084300(5);
      FUN_00084410();
      FUN_000c73a0(s_successful_package_verification_0165bb10);
      break;
    }
    if (iVar5 != 3) {
      local_260[0] = 0x811c9dc5;
      iVar5 = FUN_00752a40();
      if (iVar5 - 1U < 10) {
        pwVar11 = (wchar16 *)(&PTR_DAT_01946820)[(int)(iVar5 - 1U)];
      }
      else {
        pwVar11 = u_Unreadable_game_content__A_full_D_015d0870;
      }
      FUN_0078eb60(local_260,pwVar11,0,&PTR_PTR_01946770);
      *(undefined4 *)(param_1 + 0x30) = 4;
      break;
    }
    uVar13 = FUN_000cddd0();
LAB_0079eb88:
    local_258 = 0x100000002;
    uStack_250 = (ulong)uVar13;
    local_248 = 0;
    FUN_0078ef60(3,&local_258);
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

