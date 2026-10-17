
void FUN_002b01f0(void)

{
  int iVar1;
  long lVar2;
  ulong uVar3;
  ulong uVar4;
  undefined4 *puVar5;
  uint uVar6;
  bool bVar7;
  
  if (DAT_0265b504 != 2) {
    return;
  }
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
  if (DAT_0265b4e0 == 0) {
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
  if (*(long *)(DAT_0265b4e0 + 0x4408) == 0) {
    DAT_0265b4f0 = 0;
  }
  else {
    uVar6 = 0;
    uVar3 = 0;
    uVar4 = 1;
    do {
      iVar1 = FUN_000b9a00(*(undefined4 *)(DAT_0265b4e0 + 0x4410 + uVar3 * 0xf8));
      if ((iVar1 == -1) || (iVar1 = FUN_000b83e0(iVar1), iVar1 != 3)) {
        uVar6 = uVar6 + 1;
      }
      bVar7 = uVar4 < *(ulong *)(DAT_0265b4e0 + 0x4408);
      uVar3 = uVar4;
      uVar4 = (ulong)((int)uVar4 + 1);
    } while (bVar7);
    DAT_0265b4f0 = uVar6;
    if (uVar6 != 0) {
      lVar2 = FUN_000b4bd0((ulong)uVar6 * 0xf8,0x19);
      puVar5 = (undefined4 *)(DAT_0265b4e0 + 0x4410);
      DAT_0265b4e8 = lVar2;
      do {
        iVar1 = FUN_000b9a00(*puVar5);
        if ((iVar1 == -1) || (iVar1 = FUN_000b83e0(iVar1), iVar1 != 3)) {
          thunk_FUN_012aa7c6(lVar2,puVar5,0xf8);
          uVar6 = uVar6 - 1;
          lVar2 = lVar2 + 0xf8;
        }
        puVar5 = puVar5 + 0x3e;
      } while (uVar6 != 0);
      goto LAB_002b0385;
    }
  }
  DAT_0265b4e8 = 0;
LAB_002b0385:
  DAT_0265b500 = 0;
  DAT_0265b4f8 = 0;
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
  if (DAT_0265b4e0 == 0) {
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
  DAT_0265b50e = 0xffff;
  DAT_0265b504 = 3;
  DAT_0265b4e0 = 0;
  return;
}

