
/* WARNING: Restarted to delay deadcode elimination for space: stack */

bool FUN_002a0d20(long param_1,code *param_2,uint param_3,undefined4 *param_4,char param_5,
                 undefined4 param_6)

{
  long lVar1;
  long *plVar2;
  uint *puVar3;
  char cVar4;
  int iVar5;
  long lVar6;
  long lVar7;
  long lVar8;
  long lVar9;
  byte bVar10;
  byte bVar11;
  undefined1 uVar12;
  uint uVar13;
  undefined4 uVar14;
  long lVar15;
  long lVar16;
  undefined8 uVar17;
  long lVar18;
  ulong uVar19;
  undefined8 *puVar20;
  uint uVar21;
  char *pcVar22;
  ulong uVar23;
  long *plVar24;
  long lVar25;
  ulong uVar26;
  long lVar27;
  uint local_a8;
  uint local_a4;
  uint local_a0;
  uint local_9c;
  undefined8 local_48;
  undefined8 uStack_40;
  
  lVar6 = *DAT_01a1f100;
  lVar25 = (ulong)(((uint)((int)param_3 >> 0xd) >> 0x12 | 0x3ff) & (int)param_3 >> 0xd) * 0x40;
  lVar15 = *DAT_01a238a0;
  lVar16 = *(long *)(lVar15 + 0x10 + lVar25);
  iVar5 = *(int *)(lVar15 + 0x34 + lVar25);
  uVar21 = param_3 & 0x1fff;
  uVar19 = (ulong)(*(int *)(lVar15 + 0x30 + lVar25) * uVar21);
  uVar26 = *(ulong *)(lVar16 + 8 + uVar19);
  *(undefined1 *)(param_1 + 0x1c) = 0;
  *(undefined4 *)(param_1 + 0x20) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x668) = 0;
  FUN_00152f70();
  *(uint *)(param_1 + 0x20) = param_3;
  FUN_002a2860(*(undefined8 *)(param_1 + 0x10),param_3);
  *(undefined4 *)(param_1 + 0xd9c) = param_6;
  lVar15 = FUN_002a2d40(*(undefined8 *)(param_1 + 0x10));
  *(undefined1 *)(param_1 + 0x1d) = *(undefined1 *)(lVar15 + 0x5010);
  FUN_002d04c0(param_1 + 0x28);
  *(undefined4 *)(param_1 + 0x18) = *param_4;
  FUN_002d01e0(param_1 + 0x28);
  if (*(char *)(param_1 + 0x18) != '\0') {
    *(undefined8 *)(param_1 + 0xa80) = 0xffffffffffffffff;
    *(undefined8 *)(param_1 + 0xa78) = 0xffffffffffffffff;
    *(undefined8 *)(param_1 + 0xa70) = 0xffffffffffffffff;
    FUN_002b3830();
  }
  bVar11 = 1;
  if (param_5 == '\0') goto LAB_002a127f;
  lVar15 = (lVar16 + uVar19) - ((long)iVar5 & uVar26);
  lVar16 = FUN_002a2980(*(undefined8 *)(param_1 + 0x10));
  if ((long)*(int *)(lVar16 + 0x10) != *(long *)(lVar15 + 0x48)) {
    lVar25 = FUN_002a2980(*(undefined8 *)(param_1 + 0x10));
    if (*(int *)(lVar25 + 0x10) == 0) {
      pcVar22 = s_invalid_host_activity_state_01622ebf;
    }
    else {
      pcVar22 = s_activity_client_bubble_count_mis_01622edb;
    }
    (*param_2)(6,0,pcVar22);
    bVar11 = 0;
    goto LAB_002a127f;
  }
  uVar17 = FUN_003430b0();
  local_48 = 0;
  uStack_40 = 0;
  uVar26 = *(ulong *)(lVar15 + 0x48);
  *(int *)(param_1 + 0x668) = (int)uVar26;
  if ((int)uVar26 < 1) {
LAB_002a123e:
    bVar11 = 1;
  }
  else {
    lVar16 = lVar25 + 0x34;
    lVar1 = lVar25 + 0x30;
    lVar25 = lVar25 + 0x10;
    puVar20 = (undefined8 *)(param_1 + 0x678);
    do {
      *(undefined4 *)(puVar20 + -1) = 0xffffffff;
      *puVar20 = 0;
      puVar20 = puVar20 + 2;
      uVar13 = (int)uVar26 - 1;
      uVar26 = (ulong)uVar13;
    } while (uVar13 != 0);
    if (*(int *)(param_1 + 0x668) < 1) goto LAB_002a123e;
    bVar11 = 1;
    plVar24 = (long *)(lVar15 + 0x50);
    uVar26 = 0;
    local_9c = 0;
    local_a0 = 0;
    local_a4 = 0;
    local_a8 = 0;
    do {
      if ((bVar11 & 1) == 0) break;
      lVar15 = *plVar24;
      lVar18 = FUN_002a2980(*(undefined8 *)(param_1 + 0x10));
      cVar4 = *(char *)(lVar18 + 0x14 + uVar26);
      lVar18 = (long)cVar4;
      uVar14 = FUN_0012d6c0(uVar26 & 0xffffffff);
      if (lVar18 == -1) {
        bVar10 = FUN_00343a90(uVar17,uVar14,0xffffffff,0);
LAB_002a1120:
        bVar11 = 0;
        if ((bVar10 != 0) &&
           (bVar11 = bVar10, 1 < *(long *)((long)plVar24 + uVar26 * 0x18 + lVar15 + 0x18))) {
          plVar2 = (long *)((long)plVar24 + uVar26 * 0x18 + lVar15 + 0x20);
          lVar18 = 0x68;
          uVar19 = 0;
          do {
            if ((bVar11 & 1) == 0) break;
            lVar27 = *plVar2;
            uVar14 = FUN_0012d6d0(uVar26,uVar19 & 0xffffffff);
            lVar8 = *DAT_01a238a0;
            uVar23 = (ulong)(*(int *)(lVar8 + lVar1) * uVar21);
            bVar11 = FUN_00343a90(uVar17,uVar14,param_3,
                                  (long)plVar2 +
                                  ((((long)*(int *)(lVar8 + lVar16) &
                                    *(ulong *)(*(long *)(lVar8 + lVar25) + 8 + uVar23)) +
                                   lVar18 + lVar27) - (*(long *)(lVar8 + lVar25) + uVar23)));
            lVar18 = lVar18 + 0x3c;
            lVar27 = uVar19 + 2;
            uVar19 = uVar19 + 1;
          } while (lVar27 < *(long *)((long)plVar24 + uVar26 * 0x18 + lVar15 + 0x18));
        }
      }
      else if (cVar4 < '\x01') {
        lVar8 = uVar26 * 0x18 + lVar15 + 0x10;
        lVar27 = *(long *)((long)plVar24 + uVar26 * 0x18 + lVar15 + 0x20);
        lVar9 = lVar27 + 0x10 + lVar8;
        lVar18 = lVar18 * 0x3c;
        if (*(char *)((long)plVar24 + lVar18 + 0x10 + lVar9) != '\0') {
          lVar8 = lVar27 + 0x20 + lVar8;
          lVar27 = *DAT_01a238a0;
          uVar23 = (ulong)(*(int *)(lVar27 + lVar1) * uVar21);
          lVar7 = *(long *)(lVar27 + lVar25);
          iVar5 = *(int *)(lVar27 + lVar16);
          uVar19 = *(ulong *)(lVar7 + 8 + uVar23);
          puVar3 = (uint *)(param_1 + 0x670 + uVar26 * 0x10);
          puVar3[2] = 0;
          puVar3[3] = 0;
          puVar3[0] = 0;
          puVar3[1] = 0;
          *puVar3 = param_3;
          *(ulong *)(param_1 + 0x678 + uVar26 * 0x10) =
               (long)plVar24 + ((((long)iVar5 & uVar19) + lVar18 + 0x10 + lVar9) - (lVar7 + uVar23))
          ;
          lVar27 = *DAT_01a238a0;
          uVar19 = (ulong)(*(int *)(lVar27 + lVar1) * uVar21);
          bVar10 = FUN_00343a90(uVar17,uVar14,param_3,
                                (long)plVar24 +
                                ((((long)*(int *)(lVar27 + lVar16) &
                                  *(ulong *)(*(long *)(lVar27 + lVar25) + 8 + uVar19)) + 0x1c +
                                 lVar18 + lVar8) - (*(long *)(lVar27 + lVar25) + uVar19)));
          if (*(char *)((long)plVar24 + lVar18 + lVar8 + 0x3a) == '\0') {
            local_a8 = local_a8 | *(uint *)((long)plVar24 + lVar18 + lVar8 + 0x20);
            local_a4 = local_a4 | *(uint *)((long)plVar24 + lVar18 + lVar8 + 0x24);
            local_48 = CONCAT44(local_a4,local_a8);
            local_a0 = local_a0 | *(uint *)((long)plVar24 + lVar18 + lVar8 + 0x28);
            local_9c = local_9c | *(uint *)((long)plVar24 + lVar18 + lVar8 + 0x2c);
            uStack_40 = CONCAT44(local_9c,local_a0);
          }
          goto LAB_002a1120;
        }
        (*param_2)(6,0,s_activity_client_bubble_state_ind_01622e26);
        bVar11 = 0;
      }
      else {
        if (lVar18 < *(long *)((long)plVar24 + uVar26 * 0x18 + lVar15 + 0x18)) {
          pcVar22 = s_activity_client_bubble_state_>_1_01622e71;
        }
        else {
          pcVar22 = s_activity_client_bubble_state_mis_01622e99;
        }
        (*param_2)(6,0,pcVar22);
        bVar11 = 0;
      }
      uVar26 = uVar26 + 1;
    } while ((int)uVar26 < *(int *)(param_1 + 0x668));
  }
  FUN_002a2cb0(*(undefined8 *)(param_1 + 0x10),local_48,uStack_40);
LAB_002a127f:
  *(undefined4 *)(param_1 + 0xa84) = *(undefined4 *)(param_1 + 0xa78);
  *(undefined8 *)(param_1 + 0xa7c) = *(undefined8 *)(param_1 + 0xa70);
  FUN_002b3830();
  FUN_00152e70();
  if ((bVar11 & 1) == 0) {
    *(undefined4 *)(param_1 + 0x20) = 0xffffffff;
    *(undefined4 *)(param_1 + 0x668) = 0;
    FUN_002a2880(*(undefined8 *)(param_1 + 0x10));
    FUN_00152f70();
  }
  else {
    *(undefined1 *)(param_1 + 0x1c) = 1;
  }
  if (*DAT_01a1f100 == lVar6) {
    return (bVar11 & 1) != 0;
  }
  uVar12 = thunk_FUN_012aa7f6();
  return (bool)uVar12;
}

