
undefined1 FUN_00b31950(long param_1,undefined1 *param_2,undefined4 *param_3)

{
  int *piVar1;
  undefined4 uVar2;
  undefined *puVar3;
  long *plVar4;
  byte bVar5;
  char cVar6;
  undefined1 uVar7;
  int iVar8;
  long lVar9;
  undefined8 uVar10;
  int iVar11;
  undefined1 uVar12;
  long lVar13;
  undefined4 uVar14;
  char *pcVar15;
  undefined8 in_stack_fffffffffffffdc8;
  undefined4 *puVar16;
  undefined4 local_1fc;
  undefined1 local_1f8 [64];
  undefined1 local_1b8 [64];
  undefined1 local_178 [320];
  long local_38;
  
  uVar14 = (undefined4)((ulong)in_stack_fffffffffffffdc8 >> 0x20);
  local_38 = *DAT_01a1f100;
  local_1fc = 0;
  iVar8 = *(int *)(param_1 + 0x16b8);
  bVar5 = *(byte *)(param_1 + 0x10) & 1;
  if ((bVar5 == 0) || (*(char *)(param_1 + 0x16ac) == '\0')) {
    cVar6 = FUN_00b34ad0((long)&PTR_DAT_00001eb8 + param_1,bVar5 != 0,
                         (undefined8 *)(param_1 + 0x16a8),param_1 + 0x116a,0x80,param_1 + 0x16b0);
    if (cVar6 == '\0') {
      if ((DAT_0282d7e0 == '\0') && (iVar8 = thunk_FUN_012aa7d6(&DAT_0282d7e0), iVar8 != 0)) {
        DAT_0282d7d8 = FUN_000e4a10(s_networking_server_bap___s_Failed_01689c0b);
        thunk_FUN_012aa7e6(&DAT_0282d7e0);
      }
      pcVar15 = s_unencrypted_01689c82;
      if ((*(byte *)(param_1 + 0x10) & 1) != 0) {
        pcVar15 = s_secure_01689c7b;
      }
      uVar2 = *(undefined4 *)(*(long *)(param_1 + 0x16c0) + 4);
      local_1b8[0] = 0;
      if (*(ushort *)(*(long *)(param_1 + 0x16c0) + 0xc) < 0x130) {
        FUN_0100a3d0(local_1b8,&DAT_0160ec9c);
      }
      else {
        FUN_00065030(local_1b8,s_enum_out_of_range_01639778,0x40);
      }
      lVar13 = *(long *)(param_1 + 0x16c0);
      uVar12 = 0;
      FUN_01008290(local_178,s_networking_server_bap___s_Failed_01689c0b,param_1 + 0x1148,pcVar15,
                   uVar2,local_1b8,CONCAT44(uVar14,*(undefined4 *)(lVar13 + 0xe)),
                   *(undefined4 *)(lVar13 + 0x110),*(undefined4 *)(lVar13 + 0x118));
      FUN_000e4aa0(DAT_0282d7d8,local_178);
      local_1fc = 0x1e;
      uVar7 = 0;
      goto LAB_00b31f25;
    }
    lVar13 = *(long *)(param_1 + 0x16c0);
    iVar11 = *(int *)(param_1 + 0x16b0);
    *(int *)(param_1 + 0x16b4) = *(int *)(lVar13 + 0x118) + iVar11;
    *(undefined1 *)(param_1 + 0x16ac) = 1;
  }
  else {
    lVar13 = *(long *)(param_1 + 0x16c0);
    iVar11 = *(int *)(param_1 + 0x16b0);
  }
  if (lVar13 == 0) {
    uVar10 = 0;
    uVar14 = 0;
  }
  else {
    uVar14 = *(undefined4 *)(lVar13 + 0x118);
    uVar10 = *(undefined8 *)(lVar13 + 0x120);
  }
  puVar16 = &local_1fc;
  cVar6 = FUN_00b31fb0(param_1,param_1 + 0x116a,iVar11,uVar10,uVar14,(int *)(param_1 + 0x16b8),
                       puVar16);
  uVar14 = (undefined4)((ulong)puVar16 >> 0x20);
  if (cVar6 == '\0') {
    if (*(long *)(param_1 + 0x16c0) == 0) {
      if ((DAT_0282d800 == '\0') && (iVar8 = thunk_FUN_012aa7d6(&DAT_0282d800), iVar8 != 0)) {
        DAT_0282d7f8 = FUN_000e4a10(s_networking_server_bap___s____s__F_01689cf1);
        thunk_FUN_012aa7e6(&DAT_0282d800);
      }
      FUN_01008290(local_178,s_networking_server_bap___s____s__F_01689cf1,param_1 + 0x1148,
                   (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)],
                   *(undefined4 *)(param_1 + 0x16b4),*(undefined4 *)(param_1 + 0x16b8));
      uVar14 = DAT_0282d7f8;
    }
    else {
      if ((DAT_0282d7f0 == '\0') && (iVar8 = thunk_FUN_012aa7d6(&DAT_0282d7f0), iVar8 != 0)) {
        DAT_0282d7e8 = FUN_000e4a10(s_networking_server_bap____s____s__01689c8e);
        thunk_FUN_012aa7e6(&DAT_0282d7f0);
      }
      puVar3 = (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)];
      uVar2 = *(undefined4 *)(*(long *)(param_1 + 0x16c0) + 8);
      local_1f8[0] = 0;
      if (*(ushort *)(*(long *)(param_1 + 0x16c0) + 0xc) < 0x130) {
        FUN_0100a3d0(local_1f8,&DAT_0160ec9c);
      }
      else {
        FUN_00065030(local_1f8,s_enum_out_of_range_01639778,0x40);
      }
      FUN_01008290(local_178,s_networking_server_bap____s____s__01689c8e,param_1 + 0x1148,puVar3,
                   uVar2,local_1f8,CONCAT44(uVar14,*(undefined4 *)(param_1 + 0x16b4)),
                   *(undefined4 *)(param_1 + 0x16b8));
      uVar14 = DAT_0282d7e8;
    }
    uVar12 = 0;
    FUN_000e4aa0(uVar14,local_178);
    uVar7 = 0;
    goto LAB_00b31f25;
  }
  iVar11 = *(int *)(param_1 + 0x16b8);
  uVar7 = 1;
  if (iVar8 == iVar11) {
    uVar12 = 1;
    goto LAB_00b31f25;
  }
  if (iVar11 != *(int *)(param_1 + 0x16b4)) {
    uVar12 = 0;
    goto LAB_00b31f25;
  }
  uVar7 = 1;
  if (*(undefined4 **)(param_1 + 0x16c0) != (undefined4 *)0x0) {
    **(undefined4 **)(param_1 + 0x16c0) = 3;
    plVar4 = *(long **)(param_1 + 0x80 + (long)*(int *)(*(long *)(param_1 + 0x16c0) + 4) * 8);
    iVar8 = (**(code **)(*plVar4 + 0x18))(plVar4,*(undefined4 *)(*(long *)(param_1 + 0x16c0) + 8));
    cVar6 = (**(code **)(*plVar4 + 0x10))(plVar4,*(undefined4 *)(*(long *)(param_1 + 0x16c0) + 8));
    if (cVar6 == '\0') {
      local_1fc = 0x2a;
      uVar7 = 0;
    }
    else {
      FUN_00297fe0(param_1 + 0x20c8,1);
      uVar7 = 1;
      if (iVar8 != 0) {
        lVar13 = (long)*(int *)(*(long *)(param_1 + 0x16c0) + 4) * 0x198;
        if ((*(int *)(param_1 + 0x1c10 + lVar13) != *(int *)(param_1 + 0x1c08 + lVar13)) &&
           (lVar9 = FUN_000b0aa0((long)&DAT_01ad5000 +
                                 (ulong)*(ushort *)(param_1 + 0x1c00 + lVar13) * DAT_01ad5010 +
                                 DAT_01ad5000,0x130), lVar9 != 0)) {
          piVar1 = (int *)(param_1 + 0x1c10 + lVar13);
          iVar8 = *piVar1;
          iVar11 = (*(int *)(param_1 + 0x1c0c + lVar13) + iVar8) %
                   *(int *)(param_1 + 0x1c08 + lVar13);
          *piVar1 = iVar8 + 1;
          *(long *)(param_1 + lVar13 + 0x1c18 + (long)iVar11 * 8) = lVar9;
          if (iVar11 != -1) {
            thunk_FUN_012aa986(lVar9,0,0x130);
            *(undefined4 *)(lVar9 + 4) = 0xffffffff;
            thunk_FUN_012aa7c6(lVar9,*(undefined8 *)(param_1 + 0x16c0),0x130);
            FUN_00b316e0(param_1,param_1 + 0x1b80 + lVar13);
            goto LAB_00b31e45;
          }
        }
        local_1fc = 0x27;
        uVar7 = 0;
      }
    }
LAB_00b31e45:
    lVar13 = *(long *)(param_1 + 0x16c0);
    iVar8 = *(int *)(lVar13 + 4);
    thunk_FUN_012aa986(lVar13,0,0x130);
    *(undefined4 *)(lVar13 + 4) = 0xffffffff;
    lVar13 = (long)iVar8 * 0x198;
    piVar1 = (int *)(param_1 + 0x18e0 + lVar13);
    lVar9 = -1;
    if (*(int *)(param_1 + 0x18e0 + lVar13) != 0) {
      lVar9 = (long)*(int *)(param_1 + 0x18dc + lVar13);
    }
    FUN_000b0bd0((long)&DAT_01ad5000 +
                 (ulong)*(ushort *)(param_1 + 0x18d0 + lVar13) * DAT_01ad5010 + DAT_01ad5000,
                 *(undefined8 *)(param_1 + lVar13 + 0x18e8 + lVar9 * 8));
    *(undefined8 *)(param_1 + lVar13 + 0x18e8 + lVar9 * 8) = 0;
    iVar8 = *piVar1;
    if (iVar8 != 0) {
      *(int *)(param_1 + 0x18dc + lVar13) =
           (*(int *)(param_1 + 0x18dc + lVar13) + 1) % *(int *)(param_1 + 0x18d8 + lVar13);
      *piVar1 = iVar8 + -1;
    }
  }
  uVar12 = 0;
  *(undefined8 *)(param_1 + 0x16c0) = 0;
  *(undefined8 *)(param_1 + 0x16b8) = 0;
  *(undefined8 *)(param_1 + 0x16b0) = 0;
  *(undefined8 *)(param_1 + 0x16a8) = 0;
LAB_00b31f25:
  *param_3 = local_1fc;
  *param_2 = uVar12;
  if (*DAT_01a1f100 != local_38) {
    uVar7 = thunk_FUN_012aa7f6();
    return uVar7;
  }
  return uVar7;
}

