
void FUN_002b0980(void)

{
  short sVar1;
  int iVar2;
  ulong *puVar3;
  char cVar4;
  uint uVar5;
  int iVar6;
  ulong uVar7;
  long lVar8;
  uint uVar9;
  uint uVar10;
  int iVar11;
  ulong uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  long local_c78;
  undefined1 local_c70 [36];
  undefined4 local_c4c;
  undefined8 local_c48;
  int local_c40;
  int aiStack_c34 [639];
  short local_238 [128];
  short local_138 [128];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if ((DAT_0265b504 != 0) || (cVar4 = FUN_0009e490(DAT_0265b4a8), cVar4 == '\0')) goto LAB_002b0a59;
  cVar4 = FUN_0009e4b0(DAT_0265b4a8);
  lVar8 = DAT_0265b4b0;
  if (cVar4 == '\0') {
    DAT_0265b504 = 1;
    iVar14 = FUN_0009e470(DAT_0265b4a8);
    DAT_0265b508 = 2;
    if (iVar14 == 0x194) {
      DAT_0265b508 = 8;
    }
  }
  else {
    local_c78 = DAT_0265b4b0;
    uVar7 = FUN_0009e4e0(DAT_0265b4a8);
    if (DAT_018dc974 != '\0') {
      if (uVar7 < 0x108) {
        DAT_0265b504 = 1;
        DAT_0265b508 = 5;
        goto LAB_002b0a4d;
      }
      local_c78 = lVar8 + 0x108;
      uVar7 = uVar7 - 0x108;
      uVar9 = 0;
      do {
        uVar5 = FUN_000eee00();
        if (uVar5 <= uVar9) {
          DAT_0265b504 = 1;
          DAT_0265b508 = 6;
          goto LAB_002b0a4d;
        }
        FUN_000eee10(uVar9,&local_c48,&local_c4c);
        cVar4 = FUN_000eef90(local_c78,uVar7 & 0xffffffff,local_c48,local_c4c,lVar8);
        uVar9 = uVar9 + 1;
      } while (cVar4 == '\0');
    }
    if (DAT_0265b4e0 == (ulong *)0x0) {
      if (DAT_0265b50e != -1) {
        if (DAT_01a231f0 == (code *)0x0) {
          FUN_0005c750(s_content_manifest_container_alloc_01624cb2);
          s__libexec_ld_elf_so_1_00000000[1] = '*';
          s__libexec_ld_elf_so_1_00000000[2] = '\0';
          s__libexec_ld_elf_so_1_00000000[3] = '\0';
          s__libexec_ld_elf_so_1_00000000[4] = '\0';
        }
        else {
          (*DAT_01a231f0)(0,s_content_manifest_container_alloc_01624cb2);
        }
      }
      if (DAT_0265b4e0 != (ulong *)0x0) {
        if (DAT_01a231f0 == (code *)0x0) {
          FUN_0005c750(s_content_manifest_buffer_allocate_01624cd7);
          s__libexec_ld_elf_so_1_00000000[1] = '*';
          s__libexec_ld_elf_so_1_00000000[2] = '\0';
          s__libexec_ld_elf_so_1_00000000[3] = '\0';
          s__libexec_ld_elf_so_1_00000000[4] = '\0';
        }
        else {
          (*DAT_01a231f0)(0,s_content_manifest_buffer_allocate_01624cd7);
        }
      }
      DAT_0265b4e0 = (ulong *)FUN_000af600(0xffff,10,0xa23e8,0x19,s_CdnContentManifest_01624d48,
                                           &DAT_0265b50e);
      if (DAT_0265b50e == -1) {
        if (DAT_01a231f0 == (code *)0x0) {
          FUN_0005c750(s_content_manifest_container_not_a_01624cf9);
          s__libexec_ld_elf_so_1_00000000[1] = '*';
          s__libexec_ld_elf_so_1_00000000[2] = '\0';
          s__libexec_ld_elf_so_1_00000000[3] = '\0';
          s__libexec_ld_elf_so_1_00000000[4] = '\0';
        }
        else {
          (*DAT_01a231f0)(0,s_content_manifest_container_not_a_01624cf9);
        }
      }
      if (DAT_0265b4e0 == (ulong *)0x0) {
        if (DAT_01a231f0 == (code *)0x0) {
          FUN_0005c750(s_content_manifest_buffer_not_allo_01624d22);
          s__libexec_ld_elf_so_1_00000000[1] = '*';
          s__libexec_ld_elf_so_1_00000000[2] = '\0';
          s__libexec_ld_elf_so_1_00000000[3] = '\0';
          s__libexec_ld_elf_so_1_00000000[4] = '\0';
        }
        else {
          (*DAT_01a231f0)(0,s_content_manifest_buffer_not_allo_01624d22);
        }
      }
    }
    FUN_000a1470(local_c70,local_c78,uVar7);
    puVar3 = DAT_0265b4e0;
    iVar14 = 0;
    thunk_FUN_012aa986(DAT_0265b4e0,0,0xa23e8);
    cVar4 = FUN_000a2020(local_c70,&DAT_01911470,puVar3);
    if (cVar4 == '\0') {
      if (DAT_0265b50e == -1) {
        if (DAT_01a231f0 == (code *)0x0) {
          FUN_0005c750(s_content_manifest_container_not_a_01624cf9);
          s__libexec_ld_elf_so_1_00000000[1] = '*';
          s__libexec_ld_elf_so_1_00000000[2] = '\0';
          s__libexec_ld_elf_so_1_00000000[3] = '\0';
          s__libexec_ld_elf_so_1_00000000[4] = '\0';
        }
        else {
          (*DAT_01a231f0)(0,s_content_manifest_container_not_a_01624cf9);
        }
      }
      if (DAT_0265b4e0 == (ulong *)0x0) {
        if (DAT_01a231f0 == (code *)0x0) {
          FUN_0005c750(s_content_manifest_buffer_not_allo_01624d22);
          s__libexec_ld_elf_so_1_00000000[1] = '*';
          s__libexec_ld_elf_so_1_00000000[2] = '\0';
          s__libexec_ld_elf_so_1_00000000[3] = '\0';
          s__libexec_ld_elf_so_1_00000000[4] = '\0';
        }
        else {
          (*DAT_01a231f0)(0,s_content_manifest_buffer_not_allo_01624d22);
        }
      }
      FUN_000af8f0(DAT_0265b50e);
      DAT_0265b50e = -1;
      DAT_0265b4e0 = (ulong *)0x0;
      DAT_0265b504 = 1;
      DAT_0265b508 = 1;
    }
    else {
      local_c40 = 0;
      thunk_FUN_012aa986(local_238,0,0x100);
      thunk_FUN_012aa986(local_138,0xff,0x100);
      uVar7 = DAT_0265b4e0[0x881];
      if (uVar7 == 0) {
        iVar15 = 0;
      }
      else {
        uVar12 = 0;
        iVar15 = 0;
        do {
          iVar2 = (int)DAT_0265b4e0[uVar12 * 0x1f + 0x882];
          uVar9 = iVar2 * 0xceb & 0x7f;
          sVar1 = local_238[uVar9];
          iVar13 = (int)sVar1;
          if (0 < sVar1) {
            iVar6 = 0;
            iVar11 = iVar13;
            uVar5 = uVar9;
            do {
              lVar8 = (long)(int)uVar5;
              if ((int)local_138[lVar8] == uVar9) {
                if (((aiStack_c34[lVar8 * 5] == iVar2) && (aiStack_c34[lVar8 * 5 + 1] == 0)) &&
                   (aiStack_c34[lVar8 * 5 + 2] == 0)) {
                  if (uVar5 != 0xffffffff) {
                    iVar15 = iVar15 + 1;
                    goto LAB_002b0eb4;
                  }
                  break;
                }
                if (iVar11 < 2) break;
                iVar11 = iVar11 + -1;
              }
              uVar5 = (uVar5 + 1) -
                      (uVar5 + 1 + ((uint)((int)(uVar5 + 1) >> 0x1f) >> 0x19) & 0xffffff80);
              iVar6 = iVar6 + 1;
            } while (iVar6 < 0x80);
          }
          if (iVar14 < 0x80) {
            uVar5 = uVar9;
            uVar10 = uVar9;
            if (0 < sVar1) {
              do {
                uVar5 = uVar10 + 1;
                iVar13 = iVar13 - (uint)((int)local_138[(int)uVar10 % 0x80] == uVar9);
                uVar10 = uVar5;
              } while (0 < iVar13);
            }
            iVar13 = (int)uVar5 % 0x80;
            do {
              lVar8 = (long)iVar13;
              uVar5 = uVar5 + (local_138[lVar8] != -1);
              iVar13 = (int)uVar5 % 0x80;
            } while (local_138[lVar8] != -1);
            if (iVar13 != -1) {
              lVar8 = (long)iVar13;
              aiStack_c34[lVar8 * 5] = iVar2;
              aiStack_c34[lVar8 * 5 + 1] = 0;
              aiStack_c34[lVar8 * 5 + 2] = 0;
              local_138[lVar8] = (short)uVar9;
              local_238[uVar9] = sVar1 + 1;
              iVar14 = local_c40;
            }
            iVar14 = iVar14 + 1;
            uVar7 = DAT_0265b4e0[0x881];
            local_c40 = iVar14;
          }
LAB_002b0eb4:
          uVar12 = uVar12 + 1;
        } while (uVar12 < uVar7);
      }
      uVar7 = *DAT_0265b4e0;
      if (uVar7 != 0) {
        uVar12 = 0;
        do {
          iVar2 = (int)DAT_0265b4e0[uVar12 * 0x22 + 1];
          uVar9 = iVar2 * 0xceb & 0x7f;
          sVar1 = local_238[uVar9];
          iVar13 = (int)sVar1;
          if (0 < sVar1) {
            iVar6 = 0;
            iVar11 = iVar13;
            uVar5 = uVar9;
            do {
              lVar8 = (long)(int)uVar5;
              if ((int)local_138[lVar8] == uVar9) {
                if (((aiStack_c34[lVar8 * 5] == iVar2) && (aiStack_c34[lVar8 * 5 + 1] == 0)) &&
                   (aiStack_c34[lVar8 * 5 + 2] == 0)) {
                  if (uVar5 != 0xffffffff) {
                    iVar15 = iVar15 + 1;
                    goto LAB_002b1060;
                  }
                  break;
                }
                if (iVar11 < 2) break;
                iVar11 = iVar11 + -1;
              }
              uVar5 = (uVar5 + 1) -
                      (uVar5 + 1 + ((uint)((int)(uVar5 + 1) >> 0x1f) >> 0x19) & 0xffffff80);
              iVar6 = iVar6 + 1;
            } while (iVar6 < 0x80);
          }
          if (iVar14 < 0x80) {
            uVar5 = uVar9;
            uVar10 = uVar9;
            if (0 < sVar1) {
              do {
                uVar5 = uVar10 + 1;
                iVar13 = iVar13 - (uint)((int)local_138[(int)uVar10 % 0x80] == uVar9);
                uVar10 = uVar5;
              } while (0 < iVar13);
            }
            iVar13 = (int)uVar5 % 0x80;
            do {
              lVar8 = (long)iVar13;
              uVar5 = uVar5 + (local_138[lVar8] != -1);
              iVar13 = (int)uVar5 % 0x80;
            } while (local_138[lVar8] != -1);
            if (iVar13 != -1) {
              lVar8 = (long)iVar13;
              aiStack_c34[lVar8 * 5] = iVar2;
              aiStack_c34[lVar8 * 5 + 1] = 0;
              aiStack_c34[lVar8 * 5 + 2] = 0;
              local_138[lVar8] = (short)uVar9;
              local_238[uVar9] = sVar1 + 1;
              iVar14 = local_c40;
            }
            iVar14 = iVar14 + 1;
            uVar7 = *DAT_0265b4e0;
            local_c40 = iVar14;
          }
LAB_002b1060:
          uVar12 = uVar12 + 1;
        } while (uVar12 < uVar7);
      }
      if (DAT_0265b4e0[0x1042] == 0) {
        uVar7 = 0;
        for (lVar8 = 0x821c; *(char *)((long)DAT_0265b4e0 + lVar8) != '\0'; lVar8 = lVar8 + 0x118) {
          DAT_0265b4e0[0x1042] = DAT_0265b4e0[0x1042] + 1;
          uVar7 = uVar7 + 1;
          if (0x5db < uVar7) break;
        }
      }
      if ((DAT_0265b4dd == '\0') ||
         (((char)DAT_0265b4e0[0x14478] != '\0' &&
          (iVar14 = thunk_FUN_012aab16(&DAT_0265b4b8,(long)DAT_0265b4e0 + 0xa23c1,0x25), iVar14 == 0
          )))) {
        DAT_0265b504 = 2;
        if (0 < iVar15) {
          DAT_0265b504 = 1;
          DAT_0265b508 = 3;
        }
      }
      else {
        if (DAT_0265b50e == -1) {
          if (DAT_01a231f0 == (code *)0x0) {
            FUN_0005c750(s_content_manifest_container_not_a_01624cf9);
            s__libexec_ld_elf_so_1_00000000[1] = '*';
            s__libexec_ld_elf_so_1_00000000[2] = '\0';
            s__libexec_ld_elf_so_1_00000000[3] = '\0';
            s__libexec_ld_elf_so_1_00000000[4] = '\0';
          }
          else {
            (*DAT_01a231f0)(0,s_content_manifest_container_not_a_01624cf9);
          }
        }
        if (DAT_0265b4e0 == (ulong *)0x0) {
          if (DAT_01a231f0 == (code *)0x0) {
            FUN_0005c750(s_content_manifest_buffer_not_allo_01624d22);
            s__libexec_ld_elf_so_1_00000000[1] = '*';
            s__libexec_ld_elf_so_1_00000000[2] = '\0';
            s__libexec_ld_elf_so_1_00000000[3] = '\0';
            s__libexec_ld_elf_so_1_00000000[4] = '\0';
          }
          else {
            (*DAT_01a231f0)(0,s_content_manifest_buffer_not_allo_01624d22);
          }
        }
        FUN_000af8f0(DAT_0265b50e);
        DAT_0265b50e = -1;
        DAT_0265b4e0 = (ulong *)0x0;
        DAT_0265b504 = 1;
        DAT_0265b508 = 4;
      }
    }
  }
LAB_002b0a4d:
  FUN_000b4d40(DAT_0265b4b0);
LAB_002b0a59:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

