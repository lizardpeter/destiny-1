
void FUN_0054f840(undefined8 param_1,char param_2,int *param_3,undefined4 param_4,char param_5,
                 long param_6,long param_7,int *param_8)

{
  long *plVar1;
  char *pcVar2;
  char cVar3;
  long lVar4;
  long lVar5;
  int iVar6;
  int iVar7;
  long *plVar8;
  long lVar9;
  long lVar10;
  int *piVar11;
  long *plVar12;
  int iVar13;
  uint uVar14;
  long lVar15;
  long extraout_RDX;
  long lVar16;
  long lVar17;
  long lVar18;
  long lVar19;
  short *psVar20;
  long *plVar21;
  uint local_6c;
  undefined4 local_60 [2];
  int local_58 [2];
  int local_50 [2];
  int local_48 [2];
  int local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  plVar8 = (long *)FUN_0025a550();
  lVar9 = (**(code **)(*plVar8 + 0x68))(plVar8);
  FUN_0054b0c0(param_1);
  lVar10 = FUN_0054c7b0(param_1,param_4);
  local_6c = 0;
  if (param_5 == '\0') {
    if (((*(char *)(lVar9 + 0x13b) != param_2) || (param_3[1] == -0x7ee3623b)) ||
       (local_50[0] = param_3[1], iVar6 = FUN_0058ea60(local_50), iVar6 == -1)) {
      iVar6 = -1;
      if (*param_3 != -0x7ee3623b) {
        local_58[0] = *param_3;
        iVar6 = FUN_0058ea60(local_58);
      }
    }
    if ((iVar6 != -1) && (param_7 != 0)) {
      lVar17 = 0;
      do {
        if ((*(short *)(param_7 + lVar17 * 2) != -1) &&
           ((((piVar11 = (int *)FUN_0054c5b0(param_1), *(char *)(lVar9 + 0x13b) == param_2 &&
              (piVar11[1] != -0x7ee3623b)) &&
             (local_40[0] = piVar11[1], iVar7 = FUN_0058ea60(local_40), iVar7 != -1)) ||
            ((*piVar11 != -0x7ee3623b &&
             (local_48[0] = *piVar11, iVar7 = FUN_0058ea60(local_48), iVar7 != -1)))))) {
          iVar6 = iVar7;
        }
        lVar17 = lVar17 + 1;
      } while ((int)lVar17 != 8);
    }
    if (iVar6 != -1) {
      *param_8 = iVar6;
      local_6c = 1;
    }
  }
  if ((lVar10 != 0) && (0 < *(long *)(lVar10 + 0x10))) {
    plVar8 = (long *)(param_3 + 4);
    plVar1 = (long *)(lVar10 + 0x18);
    lVar9 = 0;
    do {
      lVar17 = *plVar1;
      pcVar2 = (char *)((long)plVar1 + lVar9 * 0x18 + lVar17 + 0x10);
      lVar15 = 0x10;
      lVar16 = 0;
      do {
        if (*(long *)(param_3 + 2) <= lVar16) goto LAB_0054fc80;
        lVar18 = *(long *)((long)plVar8 + lVar15 + *plVar8);
        lVar19 = lVar15 + *plVar8;
        lVar15 = lVar15 + 8;
        lVar16 = lVar16 + 1;
      } while (*(char *)((long)plVar8 + lVar18 + lVar19) != *pcVar2);
      plVar21 = (long *)((long)plVar8 + lVar18 + lVar19 + 8);
      lVar15 = 0;
      if (param_7 == 0) {
LAB_0054fafb:
        if (0 < *plVar21) {
          iVar6 = 0;
          if (param_6 != 0) {
            cVar3 = *(char *)((long)plVar1 + lVar9 * 0x18 + lVar17 + 0x11);
            lVar15 = 0;
            iVar6 = 0;
            iVar7 = 0;
            if (cVar3 != -1) {
              do {
                if (*(char *)(param_6 + lVar15 * 8) == cVar3) {
                  iVar7 = *(int *)(param_6 + 4 + lVar15 * 8);
                }
                lVar15 = lVar15 + 1;
              } while ((int)lVar15 != 0x10);
              lVar15 = *(long *)((long)plVar1 + lVar9 * 0x18 + lVar17 + 0x18);
              if (0 < lVar15) {
                psVar20 = (short *)((long)plVar1 +
                                   *(long *)((long)plVar1 + lVar9 * 0x18 + lVar17 + 0x20) +
                                   lVar9 * 0x18 + lVar17 + 0x34);
                iVar6 = 0;
                do {
                  if (*(int *)(psVar20 + -2) <= iVar7) {
                    iVar6 = (int)*psVar20;
                  }
                  psVar20 = psVar20 + 4;
                  lVar15 = lVar15 + -1;
                } while (lVar15 != 0);
              }
            }
          }
          if (iVar6 < 0) {
            iVar6 = 0;
          }
          iVar7 = (int)*plVar21 + -1;
          if (iVar6 <= iVar7) {
            iVar7 = iVar6;
          }
          local_60[0] = *(undefined4 *)((long)plVar21 + (long)iVar7 * 4 + plVar21[1] + 0x18);
          iVar6 = FUN_0058ea60(local_60);
          if (param_5 != '\0') {
            cVar3 = *pcVar2;
            iVar7 = 2;
            if (*(char *)(extraout_RDX + 0xe) != cVar3) {
              iVar7 = -1;
            }
            iVar13 = 2;
            if (*(char *)(extraout_RDX + 0x11) != cVar3) {
              iVar13 = iVar7;
            }
            iVar7 = 0;
            if (*(char *)(extraout_RDX + 0xf) != cVar3) {
              iVar7 = iVar13;
            }
            iVar13 = 1;
            if (*(char *)(extraout_RDX + 0x10) != cVar3) {
              iVar13 = iVar7;
            }
            iVar7 = 3;
            if (*(char *)(extraout_RDX + 0x12) != cVar3) {
              iVar7 = iVar13;
            }
            iVar13 = 4;
            if (*(char *)(extraout_RDX + 0x13) != cVar3) {
              iVar13 = iVar7;
            }
            iVar7 = 5;
            if (*(char *)(extraout_RDX + 0x14) != cVar3) {
              iVar7 = iVar13;
            }
            iVar13 = 6;
            if (*(char *)(extraout_RDX + 0x15) != cVar3) {
              iVar13 = iVar7;
            }
            if (iVar13 != -1) {
              param_8[iVar13] = iVar6;
              goto LAB_0054fc80;
            }
          }
          uVar14 = local_6c + 7;
          if (param_5 == '\0') {
            uVar14 = local_6c;
          }
          if ((-1 < (int)uVar14) && (uVar14 < 8)) {
            param_8[(int)uVar14] = iVar6;
          }
          local_6c = local_6c + 1;
        }
      }
      else {
        do {
          if (*(short *)(param_7 + lVar15 * 2) != -1) {
            lVar16 = FUN_0054c5b0();
            plVar12 = (long *)(lVar16 + 0x10);
            lVar18 = 0x10;
            lVar19 = 0;
            do {
              if (*(long *)(lVar16 + 8) <= lVar19) {
                plVar12 = (long *)0x0;
                goto LAB_0054fae2;
              }
              lVar4 = *(long *)((long)plVar12 + lVar18 + *plVar12);
              lVar5 = lVar18 + *plVar12;
              lVar18 = lVar18 + 8;
              lVar19 = lVar19 + 1;
            } while (*(char *)((long)plVar12 + lVar4 + lVar5) != *pcVar2);
            plVar12 = (long *)((long)plVar12 + lVar4 + lVar5 + 8);
LAB_0054fae2:
            if (plVar12 != (long *)0x0) {
              plVar21 = plVar12;
            }
          }
          lVar15 = lVar15 + 1;
        } while ((int)lVar15 != 8);
        if (plVar21 != (long *)0x0) goto LAB_0054fafb;
      }
LAB_0054fc80:
      lVar9 = lVar9 + 1;
    } while (lVar9 < *(long *)(lVar10 + 0x10));
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

