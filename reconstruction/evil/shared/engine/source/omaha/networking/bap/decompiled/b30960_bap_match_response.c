
undefined8 FUN_00b30960(long param_1,undefined1 *param_2,uint *param_3)

{
  long lVar1;
  undefined8 *puVar2;
  undefined *puVar3;
  undefined *puVar4;
  char cVar5;
  ushort uVar6;
  uint uVar7;
  undefined4 uVar8;
  long *plVar9;
  ulong uVar10;
  undefined8 uVar11;
  long lVar12;
  undefined1 uVar13;
  int iVar14;
  uint local_1c0;
  undefined1 local_1b9;
  undefined1 local_1b8 [64];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_1b9 = 0;
  local_1c0 = 0;
  lVar12 = param_1 + 0x1c18;
  iVar14 = 0;
  do {
    if (0 < *(int *)(lVar12 + -8)) {
      lVar1 = *(long *)(lVar12 + (long)*(int *)(lVar12 + -0xc) * 8);
      plVar9 = *(long **)(param_1 + 0x80 + (long)*(int *)(lVar1 + 4) * 8);
      uVar7 = (**(code **)(*plVar9 + 0x18))(plVar9,*(undefined4 *)(lVar1 + 8));
      if ((uVar7 == *(ushort *)(param_1 + 0x1788)) &&
         (*(int *)(lVar1 + 0xe) == *(int *)(param_1 + 0x178a))) {
        *(undefined4 *)(param_1 + 0x1828) = 1;
        *(long *)(param_1 + 0x1848) = lVar1;
        cVar5 = FUN_00b31290(param_1,plVar9,&local_1b9,&local_1c0);
        goto LAB_00b30bd1;
      }
    }
    lVar12 = lVar12 + 0x198;
    iVar14 = iVar14 + 1;
  } while (iVar14 < 2);
  puVar2 = *(undefined8 **)(param_1 + 0x1138);
  if (puVar2 != (undefined8 *)0x0) {
    cVar5 = (**(code **)*puVar2)(puVar2,*(undefined2 *)(param_1 + 0x1788));
    if (cVar5 != '\0') {
      *(undefined4 *)(param_1 + 0x1828) = 2;
      cVar5 = FUN_00b31570(param_1,&local_1b9,&local_1c0);
LAB_00b30bd1:
      if (cVar5 == '\0') {
        if ((local_1c0 == 0x16) || (local_1c0 == 0x19)) {
          local_1c0 = 0;
          uVar13 = 1;
          uVar7 = 0;
        }
        else {
          if (DAT_0282d6f0 == '\0') {
            iVar14 = thunk_FUN_012aa7d6(&DAT_0282d6f0);
            if (iVar14 != 0) {
              DAT_0282d6e8 = FUN_000e4a10(s_networking_server_bap____s____s__01689642);
              thunk_FUN_012aa7e6(&DAT_0282d6f0);
            }
          }
          uVar7 = local_1c0;
          puVar3 = (&PTR_s__none_0196bcd0)[local_1c0];
          puVar4 = (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)];
          uVar8 = *(undefined4 *)(param_1 + 0x178a);
          uVar11 = FUN_00b34440(*(undefined2 *)(param_1 + 0x1788));
          uVar13 = 0;
          FUN_01008290(local_178,s_networking_server_bap____s____s__01689642,param_1 + 0x1148,puVar4
                       ,puVar3,uVar8,uVar11);
          FUN_000e4aa0(DAT_0282d6e8,local_178);
        }
      }
      else {
        if (*(long *)(param_1 + 0x1840) != 0) {
          FUN_000b0bd0((long)&DAT_01ad5000 +
                       (ulong)*(ushort *)(param_1 + 0x1168) * DAT_01ad5010 + DAT_01ad5000);
          *(undefined8 *)(param_1 + 0x1840) = 0;
        }
        thunk_FUN_012aa986(param_1 + 0x16c8,0,0x188);
        uVar13 = 1;
        uVar7 = local_1c0;
      }
      goto LAB_00b30d17;
    }
  }
  plVar9 = (long *)FUN_0055af60(*(undefined2 *)(param_1 + 0x1788));
  uVar8 = (**(code **)(*plVar9 + 8))(plVar9);
  plVar9 = (long *)FUN_0055d370(uVar8);
  uVar10 = (**(code **)*plVar9)(plVar9);
  uVar6 = 0;
  if ((uVar10 & 0x10) != 0) {
    uVar6 = (**(code **)(*plVar9 + 0x78))(plVar9,param_1 + 0x1790);
  }
  if (DAT_0282d700 == '\0') {
    iVar14 = thunk_FUN_012aa7d6(&DAT_0282d700);
    if (iVar14 != 0) {
      DAT_0282d6f8 = FUN_000e4a10(s_networking_server_bap____s____s__016896b9);
      thunk_FUN_012aa7e6(&DAT_0282d700);
    }
  }
  puVar3 = (&PTR_s__none_0196bc80)[*(uint *)(param_1 + 0x1144)];
  uVar8 = *(undefined4 *)(param_1 + 0x178a);
  uVar11 = FUN_00b34440(*(undefined2 *)(param_1 + 0x1788));
  local_1b8[0] = 0;
  if (uVar6 < 0x20a) {
    FUN_0100a3d0(local_1b8,&DAT_0160ec9c,uVar6);
  }
  else {
    FUN_00065030(local_1b8,s_enum_out_of_range_01639778,0x40);
  }
  uVar13 = 0;
  FUN_01008290(local_178,s_networking_server_bap____s____s__016896b9,param_1 + 0x1148,puVar3,uVar8,
               uVar11,local_1b8);
  FUN_000e4aa0(DAT_0282d6f8,local_178);
  uVar7 = 0x12;
  local_1c0 = 0x12;
LAB_00b30d17:
  *param_3 = uVar7;
  *param_2 = local_1b9;
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar13);
  }
  uVar11 = thunk_FUN_012aa7f6();
  return uVar11;
}

