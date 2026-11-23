
ulong FUN_000a17d0(undefined8 *param_1,uint *param_2,long *param_3)

{
  int *piVar1;
  int iVar2;
  code *pcVar3;
  byte bVar4;
  char *pcVar5;
  byte bVar6;
  long lVar7;
  uint *puVar8;
  uint uVar9;
  long *plVar10;
  uint uVar11;
  ulong uVar12;
  uint *puVar13;
  ulong uVar14;
  ulong uVar15;
  ulong *puVar16;
  uint uVar17;
  ulong uVar18;
  char cVar19;
  int local_e0;
  int local_dc;
  uint local_cc;
  long *local_c8;
  code *local_c0;
  char *local_b8;
  long local_b0;
  undefined8 local_a0;
  undefined8 local_98;
  ulong local_90;
  undefined8 local_88;
  undefined8 local_80;
  undefined8 local_78;
  ulong local_70;
  undefined8 local_68;
  byte local_5b;
  byte local_5a;
  byte local_59;
  undefined8 local_58;
  undefined8 uStack_50;
  char local_42 [10];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_58 = 0;
  uStack_50 = 0;
  uVar12 = param_1[2];
  local_e0 = 0;
  puVar8 = param_2;
  if (uVar12 != 0) {
    local_c8 = (long *)((long)param_3 + (ulong)*(byte *)((long)param_2 + 5));
    puVar16 = (ulong *)((long)*(char *)((long)param_2 + 6) + (ulong)*(byte *)((long)param_2 + 5) +
                       (long)param_3);
    pcVar5 = (char *)0x0;
    local_dc = 0;
    puVar13 = param_2;
LAB_000a1d90:
    local_cc = (uint)pcVar5;
    uVar18 = 0;
    bVar4 = 0;
    do {
      if (0x3f < bVar4) {
        if (param_1[3] == 0) {
          pcVar5 = s_varint_overflow_016121f7;
LAB_000a1e36:
          param_1[3] = pcVar5;
        }
LAB_000a1e3a:
        uVar18 = (ulong)pcVar5 & 0xffffffffffffff00;
        local_e0 = 0;
        if (param_1[2] == 0) goto LAB_000a1e80;
        goto LAB_000a1ef9;
      }
      if (uVar12 == 0) {
        if (param_1[3] == 0) {
          pcVar5 = s_end_of_stream_016121e0;
          goto LAB_000a1e36;
        }
        goto LAB_000a1e3a;
      }
      pcVar5 = (char *)(*(code *)*param_1)(param_1,&local_59,1);
      if ((char)pcVar5 == '\0') {
        if (param_1[3] == 0) {
          pcVar5 = s_io_error_016121ee;
          goto LAB_000a1e36;
        }
        goto LAB_000a1e3a;
      }
      uVar12 = param_1[2] - 1;
      param_1[2] = uVar12;
      pcVar5 = (char *)(ulong)local_59;
      uVar18 = uVar18 | ((ulong)pcVar5 & 0x7f) << (bVar4 & 0x3f);
      bVar4 = bVar4 + 7;
    } while ((char)local_59 < '\0');
    local_e0 = 0;
    uVar17 = (uint)uVar18;
    if (uVar17 != 0) {
      uVar11 = uVar17 & 7;
      uVar9 = local_cc;
      do {
        if (*puVar13 == uVar17 >> 3) {
          bVar4 = (byte)puVar13[1];
          if ((bVar4 < 0x10) && (local_dc < 0x80)) {
            *(byte *)((long)&local_58 + (long)(local_dc >> 3)) =
                 *(byte *)((long)&local_58 + (long)(local_dc >> 3)) |
                 (byte)(1 << ((byte)local_dc & 7));
            bVar4 = (byte)puVar13[1];
          }
          uVar18 = (ulong)(bVar4 & 0xf);
          pcVar3 = (code *)(&PTR_FUN_01905070)[uVar18];
          bVar6 = bVar4 & 0xf0;
          plVar10 = local_c8;
          local_cc = uVar9;
          if (bVar6 < 0x10) {
            if ((bVar4 & 0xf0) != 0) {
LAB_000a1e5a:
              uVar18 = 0;
              if (param_1[3] == 0) {
                param_1[3] = s_invalid_field_type_016122b1;
              }
              goto LAB_000a1ef9;
            }
LAB_000a1aea:
            uVar18 = (*pcVar3)(param_1,puVar13,plVar10);
          }
          else {
            if (bVar6 == 0x10) {
              *(undefined1 *)puVar16 = 1;
              goto LAB_000a1aea;
            }
            if (bVar6 == 0x20) {
              if ((uVar11 == 2) && ((bVar4 & 0xf) < 4)) {
                uVar14 = 0;
                bVar4 = 0;
                goto LAB_000a19dd;
              }
              uVar18 = *puVar16;
              if (uVar18 < *(uint *)((long)puVar13 + 0xb)) {
                uVar17 = *(uint *)((long)puVar13 + 7);
                *puVar16 = uVar18 + 1;
                plVar10 = (long *)(uVar17 * uVar18 + (long)local_c8);
                goto LAB_000a1aea;
              }
              uVar18 = uVar18 & 0xffffffffffffff00;
              if (param_1[3] == 0) {
                param_1[3] = s_array_overflow_01612292;
              }
              goto LAB_000a1ef9;
            }
            if (bVar6 != 0x30) goto LAB_000a1e5a;
            if (*local_c8 != 0) {
              if (uVar11 < 6) {
                bVar4 = 0;
                uVar14 = 0;
                uVar18 = (long)&switchD_000a1b3b::switchdataD_000a1ff4 +
                         (long)(int)(&switchD_000a1b3b::switchdataD_000a1ff4)[uVar11];
                switch(uVar11) {
                case 0:
                  goto switchD_000a1b3b_caseD_0;
                case 1:
                  if (uVar12 < 8) goto LAB_000a1fb4;
                  uVar18 = (*(code *)*param_1)(param_1,local_42,8);
                  if ((char)uVar18 == '\0') goto LAB_000a1fd1;
                  param_1[2] = param_1[2] + -8;
                  local_b0 = 8;
                  goto LAB_000a1d45;
                case 2:
                  goto switchD_000a1b3b_caseD_2;
                case 5:
                  if (uVar12 < 4) goto LAB_000a1fb4;
                  uVar18 = (*(code *)*param_1)(param_1,local_42,4);
                  if ((char)uVar18 == '\0') goto LAB_000a1fd1;
                  param_1[2] = param_1[2] + -4;
                  local_b0 = 4;
                  goto LAB_000a1d45;
                }
              }
              uVar18 = uVar18 & 0xffffffffffffff00;
              if (param_1[3] == 0) {
                param_1[3] = s_invalid_wire_type_01612207;
              }
              goto LAB_000a1ef9;
            }
            uVar18 = FUN_000a15a0();
          }
          cVar19 = (char)uVar18;
          goto LAB_000a1af5;
        }
        uVar18 = (ulong)*(uint *)((long)puVar13 + 7);
        if (((byte)puVar13[1] & 0xf0) == 0x20) {
          uVar18 = *(uint *)((long)puVar13 + 0xb) * uVar18;
        }
        local_dc = local_dc + (uint)((byte)puVar13[1] < 0x10);
        piVar1 = (int *)((long)puVar13 + 0x17);
        puVar13 = (uint *)((long)puVar13 + 0x17);
        plVar10 = local_c8;
        if (*piVar1 == 0) {
          local_dc = 0;
          uVar18 = 0;
          puVar13 = param_2;
          plVar10 = param_3;
        }
        uVar9 = uVar9 + 1;
        if (*piVar1 == 0) {
          uVar9 = 0;
        }
        lVar7 = *(byte *)((long)puVar13 + 5) + uVar18;
        local_c8 = (long *)((long)plVar10 + lVar7);
        puVar16 = (ulong *)(*(char *)((long)puVar13 + 6) + lVar7 + (long)plVar10);
      } while (uVar9 != local_cc);
      uVar12 = FUN_000a15a0();
      uVar18 = uVar12 & 0xffffffffffffff00;
      if ((char)uVar12 != '\0') goto LAB_000a1aff;
      goto LAB_000a1ef9;
    }
  }
LAB_000a1e80:
  do {
    bVar4 = (byte)puVar8[1];
    if (((((bVar4 & 0xf0) == 0) && (local_e0 < 0x80)) &&
        ((*(byte *)((long)&local_58 + (long)(local_e0 >> 3)) >> ((byte)local_e0 & 7) & 1) == 0)) &&
       ((*(long *)((long)puVar8 + 0xf) == 0 && ((bVar4 & 0xf) != 6)))) {
      uVar18 = 0;
      if (param_1[3] == 0) {
        param_1[3] = s_missing_required_field_01612231;
      }
      break;
    }
    local_e0 = local_e0 + (uint)(bVar4 < 0x10);
    iVar2 = *(int *)((long)puVar8 + 0x17);
    puVar8 = (uint *)((long)puVar8 + 0x17);
    if (iVar2 == 0) {
      local_e0 = 0;
      puVar8 = param_2;
    }
    uVar18 = CONCAT71((uint7)(uint3)((uint)iVar2 >> 8),1);
  } while (iVar2 != 0);
LAB_000a1ef9:
  if (*DAT_01a1f100 != local_38) {
    uVar12 = thunk_FUN_012aa7f6();
    return uVar12;
  }
  return uVar18;
  while( true ) {
    if (uVar12 == 0) goto LAB_000a1fb4;
    uVar18 = (*(code *)*param_1)(param_1,&local_5b,1);
    if ((char)uVar18 == '\0') {
      uVar18 = uVar18 & 0xffffffffffffff00;
      if (param_1[3] == 0) {
        param_1[3] = s_io_error_016121ee;
      }
      goto LAB_000a1ef9;
    }
    uVar12 = param_1[2] - 1;
    param_1[2] = uVar12;
    uVar14 = uVar14 | ((ulong)local_5b & 0x7f) << (bVar4 & 0x3f);
    bVar4 = bVar4 + 7;
    if (-1 < (char)local_5b) break;
LAB_000a19dd:
    uVar18 = 0;
    if (0x3f < bVar4) goto LAB_000a1f61;
  }
  local_70 = param_1[2];
  local_68 = param_1[3];
  local_80 = *param_1;
  local_78 = param_1[1];
  uVar18 = uVar14 & 0xffffffff;
  if (local_70 < uVar18) goto LAB_000a1f77;
  param_1[2] = uVar12 - uVar18;
  local_70 = uVar18;
  if (uVar18 == 0) {
    uVar18 = 0;
  }
  else {
    uVar12 = *puVar16;
    do {
      uVar18 = local_70;
      if (*(uint *)((long)puVar13 + 0xb) <= uVar12) goto LAB_000a1be1;
      uVar12 = (*pcVar3)(&local_80,puVar13,
                         (long *)(*(uint *)((long)puVar13 + 7) * uVar12 + (long)local_c8));
      uVar18 = uVar12 & 0xffffffffffffff00;
      if ((char)uVar12 == '\0') goto LAB_000a1ef9;
      uVar12 = *puVar16 + 1;
      *puVar16 = uVar12;
    } while (local_70 != 0);
    uVar18 = 0;
  }
LAB_000a1be1:
  param_1[1] = local_78;
  cVar19 = uVar18 == 0;
LAB_000a1af5:
  uVar18 = uVar18 & 0xffffffffffffff00;
  if (cVar19 == '\0') goto LAB_000a1ef9;
LAB_000a1aff:
  local_e0 = 0;
  uVar12 = param_1[2];
  pcVar5 = (char *)(ulong)local_cc;
  if (uVar12 == 0) goto LAB_000a1e80;
  goto LAB_000a1d90;
  while( true ) {
    if (uVar12 == 0) goto LAB_000a1fb4;
    uVar18 = (*(code *)*param_1)(param_1,&local_5a,1);
    if ((char)uVar18 == '\0') goto LAB_000a1fd1;
    uVar12 = param_1[2] - 1;
    param_1[2] = uVar12;
    uVar18 = (ulong)local_5a;
    uVar14 = uVar14 | (uVar18 & 0x7f) << (bVar4 & 0x3f);
    bVar4 = bVar4 + 7;
    if (-1 < (char)local_5a) break;
switchD_000a1b3b_caseD_2:
    if (0x3f < bVar4) goto LAB_000a1f61;
  }
  local_90 = param_1[2];
  local_88 = param_1[3];
  local_a0 = *param_1;
  local_98 = param_1[1];
  uVar18 = uVar14 & 0xffffffff;
  if (local_90 < uVar18) {
LAB_000a1f77:
    uVar18 = uVar18 & 0xffffffffffffff00;
    if (param_1[3] == 0) {
      param_1[3] = s_parent_stream_too_short_01612219;
    }
    goto LAB_000a1ef9;
  }
  param_1[2] = uVar12 - uVar18;
  local_90 = uVar18;
  while (local_90 != 0) {
    uVar18 = (*(code *)*local_c8)(&local_a0,puVar13,local_c8[1]);
    if ((char)uVar18 == '\0') {
      uVar18 = uVar18 & 0xffffffffffffff00;
      if (param_1[3] == 0) {
        param_1[3] = s_callback_failed_016122a1;
      }
      goto LAB_000a1ef9;
    }
  }
  param_1[1] = local_98;
  goto LAB_000a1aff;
LAB_000a1f61:
  uVar18 = uVar18 & 0xffffffffffffff00;
  if (param_1[3] == 0) {
    param_1[3] = s_varint_overflow_016121f7;
  }
  goto LAB_000a1ef9;
switchD_000a1b3b_caseD_0:
  if (uVar12 == 0) goto LAB_000a1fb4;
  uVar18 = (*(code *)*param_1)(param_1,local_42 + uVar14,1);
  if ((char)uVar18 == '\0') goto LAB_000a1fd1;
  uVar12 = param_1[2] - 1;
  param_1[2] = uVar12;
  if (-1 < local_42[uVar14]) goto LAB_000a1d3f;
  uVar15 = uVar14 + 2;
  uVar18 = uVar18 & 0xffffffffffffff00;
  uVar14 = uVar14 + 1;
  if (10 < uVar15) goto LAB_000a1ef9;
  goto switchD_000a1b3b_caseD_0;
LAB_000a1fb4:
  uVar18 = uVar18 & 0xffffffffffffff00;
  if (param_1[3] == 0) {
    param_1[3] = s_end_of_stream_016121e0;
  }
  goto LAB_000a1ef9;
LAB_000a1fd1:
  uVar18 = uVar18 & 0xffffffffffffff00;
  if (param_1[3] == 0) {
    param_1[3] = s_io_error_016121ee;
  }
  goto LAB_000a1ef9;
LAB_000a1d3f:
  local_b0 = uVar14 + 1;
LAB_000a1d45:
  local_c0 = FUN_000a1430;
  local_b8 = local_42;
  uVar18 = (*(code *)*local_c8)(&local_c0,puVar13,local_c8[1]);
  cVar19 = (char)uVar18;
  goto LAB_000a1af5;
}

