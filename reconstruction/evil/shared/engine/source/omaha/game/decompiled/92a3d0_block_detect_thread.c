
/* WARNING: Restarted to delay deadcode elimination for space: stack */

undefined8 FUN_0092a3d0(void)

{
  int iVar1;
  undefined *puVar2;
  code *pcVar3;
  undefined4 uVar4;
  byte bVar5;
  long lVar6;
  byte *pbVar7;
  long lVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  char *pcVar11;
  bool bVar12;
  byte local_d526;
  int local_d504;
  undefined1 local_d468 [16];
  undefined4 local_d458;
  undefined8 local_d450;
  undefined8 local_d448;
  undefined8 local_d440;
  undefined8 local_d438;
  undefined8 local_d430;
  long local_d428;
  long local_d420;
  long local_d418;
  long local_d410;
  long local_d408;
  undefined8 local_d400;
  undefined8 local_d3f8;
  undefined8 local_d3f0;
  undefined4 local_d3e8;
  undefined8 local_d3e0;
  undefined8 local_d3d8;
  undefined8 local_d3d0;
  undefined8 local_d3c8;
  undefined1 auStack_d3c0 [1024];
  undefined1 auStack_cfc0 [1024];
  undefined1 auStack_cbc0 [1024];
  undefined1 auStack_c7c0 [1024];
  undefined8 local_c3c0;
  undefined1 local_c3b8;
  undefined4 local_c3b4;
  undefined1 auStack_c380 [12800];
  undefined1 auStack_9180 [8872];
  undefined1 auStack_6ed8 [1024];
  undefined1 auStack_6ad8 [8];
  undefined8 local_6ad0;
  undefined8 local_6a80;
  undefined8 local_6a78;
  ulong local_6a70;
  undefined4 local_6a68;
  undefined8 local_6a60;
  undefined8 local_6a58;
  undefined8 local_6a50;
  undefined8 local_6a48;
  undefined1 auStack_6a40 [1024];
  undefined1 auStack_6640 [1024];
  undefined1 auStack_6240 [1024];
  undefined1 auStack_5e40 [1024];
  undefined8 local_5a40;
  undefined1 local_5a38;
  undefined4 local_5a34;
  undefined1 auStack_5a00 [12800];
  undefined1 auStack_2800 [8872];
  undefined1 auStack_558 [1024];
  undefined1 auStack_158 [8];
  undefined8 local_150;
  long local_98;
  
  local_98 = *DAT_01a1f100;
  while (bVar5 = FUN_00933950(), ((bVar5 ^ 1) & 1) != 0) {
    bVar12 = true;
    local_d448 = 7;
    local_d450 = 7;
    local_d438 = 7;
    local_d440 = 7;
    local_d430 = 7;
    local_d458 = DAT_027413ec;
    FUN_000f57e0(DAT_027413ec);
    while( true ) {
      local_d526 = 0;
      if (bVar12) {
        local_d526 = FUN_00933950();
        local_d526 = local_d526 ^ 1;
      }
      if ((local_d526 & 1) == 0) break;
      FUN_000f7690(5);
      FUN_0092bda0(local_d468);
      lVar6 = FUN_0092ae90(local_d468);
      bVar12 = (*(byte *)(lVar6 + 0xe0) & 1) != 0;
      for (local_d504 = 0; local_d504 < 4; local_d504 = local_d504 + 1) {
        lVar6 = FUN_0092ae90(local_d468);
        local_d428 = (long)local_d504;
        pbVar7 = (byte *)(lVar6 + local_d428 * 0x38);
        if (0 < *(int *)(pbVar7 + 4)) {
          bVar12 = ((bVar12 || (*pbVar7 & 1) != 0) || (pbVar7[1] & 1) != 0) || (pbVar7[2] & 1) != 0;
        }
        iVar1 = *(int *)(pbVar7 + 4);
        lVar6 = *(long *)(pbVar7 + 0x20);
        local_d420 = local_d428;
        local_d418 = local_d428;
        local_d410 = local_d428;
        local_d408 = local_d428;
        lVar8 = FUN_000694d0();
        if ((((0 < *(int *)(pbVar7 + 4)) && ((DAT_027411c8 & 1) == 0)) &&
            (iVar1 + lVar6 <= lVar8 - *(long *)(pbVar7 + 8))) && (*(int *)(pbVar7 + 0x10) == 0)) {
          if (*(int *)(pbVar7 + 0x2c) == 0) {
            lVar6 = FUN_0092ae90(local_d468);
            *(int *)(lVar6 + 0xe4) = *(int *)(lVar6 + 0xe4) + 1;
            lVar6 = FUN_0092ae90(local_d468);
            *(undefined4 *)(pbVar7 + 0x2c) = *(undefined4 *)(lVar6 + 0xe4);
          }
          if (((pbVar7[1] & 1) != 0) && ((pbVar7[0x30] & 1) == 0)) {
            local_6a80 = 0;
            local_6a78 = 0;
            local_6a70 = 0;
            local_6a68 = 0;
            local_6a60 = 0;
            local_6a58 = 0;
            local_6a50 = 0;
            local_6a48 = 0;
            FUN_010799f0(auStack_6a40);
            FUN_010799f0(auStack_6640);
            FUN_010799f0(auStack_6240);
            FUN_010799f0(auStack_5e40);
            local_5a40 = 0;
            local_5a38 = 0;
            local_5a34 = 0;
            thunk_FUN_012aa986(auStack_5a00,0,0x3200);
            FUN_01079a10(auStack_5a00);
            thunk_FUN_012aa986(auStack_2800,0,&DAT_000022a8);
            FUN_010799f0(auStack_558);
            thunk_FUN_012aa986(auStack_158,0,8);
            local_150 = 0;
            FUN_0092aea0(&local_6a80,*(undefined4 *)(pbVar7 + 4));
            pcVar3 = DAT_01a231f0;
            if (DAT_01a231f0 == (code *)0x0) {
              puVar2 = (&PTR_s_networking_0194b5a0)[local_d504];
              uVar10 = FUN_00783940(local_6a68);
              uVar4 = local_6a68;
              uVar9 = FUN_01079a30(auStack_558);
              pcVar11 = s_resourcerer_cleanup_0166ba48;
              if (local_6a70 < 0x1389) {
                pcVar11 = &DAT_012ad038;
              }
              FUN_0005c750(s_hitch_detected___s_world_control_0166ba0c,puVar2,uVar10,uVar4,uVar9,
                           pcVar11);
              s__libexec_ld_elf_so_1_00000000[1] = '*';
              s__libexec_ld_elf_so_1_00000000[2] = '\0';
              s__libexec_ld_elf_so_1_00000000[3] = '\0';
              s__libexec_ld_elf_so_1_00000000[4] = '\0';
            }
            else {
              puVar2 = (&PTR_s_networking_0194b5a0)[local_d504];
              uVar10 = FUN_00783940(local_6a68);
              uVar4 = local_6a68;
              uVar9 = FUN_01079a30(auStack_558);
              pcVar11 = s_resourcerer_cleanup_0166ba48;
              if (local_6a70 < 0x1389) {
                pcVar11 = &DAT_012ad038;
              }
              (*pcVar3)(0,s_hitch_detected___s_world_control_0166ba0c,puVar2,uVar10,uVar4,uVar9,
                        pcVar11);
            }
            FUN_01079a40(&local_6a80);
          }
          if (((*pbVar7 & 1) != 0) && ((pbVar7[0x28] & 1) == 0)) {
            local_d400 = 0;
            local_d3f8 = 0;
            local_d3f0 = 0;
            local_d3e8 = 0;
            local_d3e0 = 0;
            local_d3d8 = 0;
            local_d3d0 = 0;
            local_d3c8 = 0;
            FUN_010799f0(auStack_d3c0);
            FUN_010799f0(auStack_cfc0);
            FUN_010799f0(auStack_cbc0);
            FUN_010799f0(auStack_c7c0);
            local_c3c0 = 0;
            local_c3b8 = 0;
            local_c3b4 = 0;
            thunk_FUN_012aa986(auStack_c380,0,0x3200);
            FUN_01079a10(auStack_c380);
            thunk_FUN_012aa986(auStack_9180,0,&DAT_000022a8);
            FUN_010799f0(auStack_6ed8);
            thunk_FUN_012aa986(auStack_6ad8,0,8);
            local_6ad0 = 0;
            FUN_0092aea0(&local_d400,*(undefined4 *)(pbVar7 + 4));
            pbVar7[0x28] = 1;
            FUN_01079a40(&local_d400);
          }
        }
      }
      FUN_0092bdd0(local_d468);
      FUN_008dd4e0();
    }
  }
  if (*DAT_01a1f100 != local_98) {
    uVar10 = thunk_FUN_012aa7f6();
    return uVar10;
  }
  return 0;
}

