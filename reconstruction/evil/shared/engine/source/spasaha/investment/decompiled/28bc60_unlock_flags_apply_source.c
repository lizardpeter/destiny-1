
void FUN_0028bc60(long param_1,long param_2,long param_3,long param_4,undefined8 param_5,
                 long param_6,undefined8 param_7,undefined8 param_8,undefined8 param_9,
                 undefined4 param_10,char param_11,long param_12,undefined1 *param_13)

{
  short sVar1;
  undefined4 uVar2;
  int iVar3;
  int *piVar4;
  long lVar5;
  long lVar6;
  long *plVar7;
  long *plVar8;
  short *psVar9;
  long lVar10;
  long lVar11;
  char cVar12;
  undefined1 local_68 [24];
  undefined1 local_50 [24];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  switch(param_10) {
  case 0:
    if (param_11 != '\0') {
      if (param_4 == 0) {
        if (param_13 != (undefined1 *)0x0) {
          *param_13 = 0;
        }
      }
      else {
        if (0 < *(int *)(param_4 + 0x7054)) {
          lVar5 = 0;
          do {
            *(undefined1 *)(param_12 + *(short *)(param_4 + 0x7058 + lVar5 * 4)) =
                 *(undefined1 *)(param_4 + 0x705a + lVar5 * 4);
            lVar5 = lVar5 + 1;
          } while ((int)lVar5 < *(int *)(param_4 + 0x7054));
        }
        if (0 < *(int *)(param_4 + 0x70a8)) {
          lVar5 = 0;
          do {
            *(undefined1 *)(param_12 + 0x2000 + (long)*(short *)(param_4 + 0x70ac + lVar5 * 8) * 8)
                 = 1;
            *(undefined4 *)(param_12 + 0x2004 + (long)*(short *)(param_4 + 0x70ac + lVar5 * 8) * 8)
                 = *(undefined4 *)(param_4 + 0x70b0 + lVar5 * 8);
            lVar5 = lVar5 + 1;
          } while ((int)lVar5 < *(int *)(param_4 + 0x70a8));
        }
      }
    }
    break;
  case 1:
    if (0 < *(int *)(param_2 + 0x3c)) {
      lVar5 = 0;
      do {
        *(undefined1 *)(param_12 + *(short *)(param_2 + 0x40 + lVar5 * 4)) =
             *(undefined1 *)(param_2 + 0x42 + lVar5 * 4);
        lVar5 = lVar5 + 1;
      } while ((int)lVar5 < *(int *)(param_2 + 0x3c));
    }
    if (0 < *(int *)(param_2 + 0x108)) {
      lVar5 = 0;
      do {
        *(undefined1 *)(param_12 + 0x2000 + (long)*(short *)(param_2 + 0x10c + lVar5 * 8) * 8) = 1;
        *(undefined4 *)(param_12 + 0x2004 + (long)*(short *)(param_2 + 0x10c + lVar5 * 8) * 8) =
             *(undefined4 *)(param_2 + 0x110 + lVar5 * 8);
        lVar5 = lVar5 + 1;
      } while ((int)lVar5 < *(int *)(param_2 + 0x108));
    }
    break;
  case 2:
    if (param_4 == 0) {
      if (param_13 != (undefined1 *)0x0) {
        *param_13 = 0;
      }
    }
    else {
      FUN_0028ca70(param_7,*(undefined2 *)(param_4 + 0x2c22),param_12);
      sVar1 = *(short *)(param_4 + 0x2c22);
      if ((sVar1 != -1) && (iVar3 = *(int *)(param_4 + 0x2c24), iVar3 != -1)) {
        plVar7 = (long *)FUN_0025a550();
        lVar5 = (**(code **)(*plVar7 + 0x328))
                          (plVar7,CONCAT62((int6)((ulong)param_4 >> 0x10),sVar1) & 0xffffffff);
        if (lVar5 != 0) {
          lVar6 = *(long *)(lVar5 + 0x18) + 0x18 + lVar5;
          lVar10 = *(long *)(*(long *)(lVar5 + 0x18) + 0x28 + lVar5);
          lVar5 = lVar10 + 0x10 + lVar6;
          lVar11 = (long)iVar3 * 0x38;
          if (0 < *(long *)(lVar11 + 0x38 + lVar5)) {
            plVar7 = (long *)(lVar10 + lVar6 + 0x50 + lVar11);
            lVar6 = 0;
            do {
              *(undefined1 *)(param_12 + *(short *)((long)plVar7 + lVar6 * 4 + *plVar7 + 0x10)) =
                   *(undefined1 *)((long)plVar7 + lVar6 * 4 + *plVar7 + 0x12);
              lVar6 = lVar6 + 1;
            } while (lVar6 < *(long *)(lVar11 + 0x38 + lVar5));
          }
        }
      }
      FUN_0028ca70(param_7,*(undefined2 *)(param_4 + 0x2c20));
    }
    break;
  case 3:
    if (param_3 == 0) {
      if (param_13 != (undefined1 *)0x0) {
        *param_13 = 0;
      }
    }
    else {
      plVar7 = (long *)FUN_0025a550();
      piVar4 = (int *)(**(code **)(*plVar7 + 0x298))(plVar7);
      if ((piVar4 != (int *)0x0) && (0 < *piVar4)) {
        lVar5 = 0;
        do {
          *(code *)(param_12 + *(short *)((long)piVar4 + lVar5 * 8 + *(long *)(piVar4 + 2) + 0x1c))
               = FUN_00005430[lVar5 + param_3];
          lVar5 = lVar5 + 1;
        } while ((int)lVar5 < *piVar4);
      }
    }
    break;
  case 4:
    if (param_3 == 0) {
      if (param_13 != (undefined1 *)0x0) {
        *param_13 = 0;
      }
    }
    else {
      FUN_0028c860(param_3,param_8,param_12);
    }
    break;
  case 5:
    if (param_3 == 0) {
      if (param_13 != (undefined1 *)0x0) {
        *param_13 = 0;
      }
    }
    else {
      if (0 < *(int *)(param_3 + 0x4ac8)) {
        lVar5 = 0;
        do {
          *(undefined1 *)(param_12 + *(short *)(param_3 + 0x4acc + lVar5 * 4)) =
               *(undefined1 *)(param_3 + 0x4ace + lVar5 * 4);
          lVar5 = lVar5 + 1;
        } while ((int)lVar5 < *(int *)(param_3 + 0x4ac8));
      }
      if (0 < *(int *)(param_3 + 0x4bcc)) {
        lVar5 = 0;
        do {
          *(undefined1 *)(param_12 + 0x2000 + (long)*(short *)(param_3 + 0x4bd0 + lVar5 * 8) * 8) =
               1;
          *(undefined4 *)(param_12 + 0x2004 + (long)*(short *)(param_3 + 0x4bd0 + lVar5 * 8) * 8) =
               *(undefined4 *)(param_3 + 0x4bd4 + lVar5 * 8);
          lVar5 = lVar5 + 1;
        } while ((int)lVar5 < *(int *)(param_3 + 0x4bcc));
      }
    }
    break;
  case 6:
    if (param_3 == 0) {
      if (param_13 != (undefined1 *)0x0) {
        *param_13 = 0;
      }
    }
    else if (0 < *(int *)(param_3 + 0x4dd0)) {
      lVar5 = 0;
      do {
        *(undefined1 *)(param_12 + 0x2000 + (long)*(short *)(param_3 + 0x4dd4 + lVar5 * 8) * 8) = 1;
        *(undefined4 *)(param_12 + 0x2004 + (long)*(short *)(param_3 + 0x4dd4 + lVar5 * 8) * 8) =
             *(undefined4 *)(param_3 + 0x4dd8 + lVar5 * 8);
        lVar5 = lVar5 + 1;
      } while ((int)lVar5 < *(int *)(param_3 + 0x4dd0));
    }
    break;
  case 7:
    if (param_4 == 0) {
      if (param_13 != (undefined1 *)0x0) {
        *param_13 = 0;
      }
    }
    else {
      plVar7 = (long *)FUN_0025a550();
      piVar4 = (int *)(**(code **)(*plVar7 + 0x2a0))(plVar7);
      if ((piVar4 != (int *)0x0) && (0 < *piVar4)) {
        lVar5 = 0;
        do {
          *(undefined1 *)
           (param_12 + *(short *)((long)piVar4 + lVar5 * 8 + *(long *)(piVar4 + 2) + 0x1c)) =
               *(undefined1 *)(param_4 + 0x53c0 + lVar5);
          lVar5 = lVar5 + 1;
        } while ((int)lVar5 < *piVar4);
      }
      plVar7 = (long *)FUN_0025a550();
      piVar4 = (int *)(**(code **)(*plVar7 + 0x2c8))(plVar7);
      if ((piVar4 != (int *)0x0) && (0 < *piVar4)) {
        lVar5 = 0;
        do {
          lVar6 = (long)*(short *)((long)piVar4 + lVar5 * 8 + *(long *)(piVar4 + 2) + 0x1c);
          *(undefined1 *)(param_12 + 0x2000 + lVar6 * 8) = 1;
          *(undefined4 *)(param_12 + 0x2004 + lVar6 * 8) =
               *(undefined4 *)(param_4 + 24000 + lVar5 * 4);
          lVar5 = lVar5 + 1;
        } while ((int)lVar5 < *piVar4);
      }
    }
    break;
  case 8:
    if ((param_3 == 0) || (param_4 == 0)) {
      if (param_13 != (undefined1 *)0x0) {
        *param_13 = 0;
      }
    }
    else {
      FUN_00273d30(local_50,param_3);
      FUN_00273e40(local_68,param_4);
      FUN_0028cec0(param_5,local_50,param_12);
      FUN_0028cec0(param_5,local_68,param_12);
    }
    break;
  case 9:
    if (param_4 == 0) {
      if (param_13 != (undefined1 *)0x0) {
        *param_13 = 0;
      }
    }
    else {
      plVar7 = (long *)FUN_00265100(param_2,param_4);
      plVar8 = (long *)FUN_0025a550();
      piVar4 = (int *)(**(code **)(*plVar8 + 0xa8))(plVar8);
      if (0 < *piVar4) {
        cVar12 = '\x01';
        do {
          lVar5 = *(long *)(param_4 + 0x6dc0 + (long)(char)(cVar12 + -1) * 8);
          if (lVar5 != *plVar7 && -1 < lVar5 - *plVar7) {
            lVar5 = *(long *)(piVar4 + 2);
            plVar8 = (long *)FUN_0025a550();
            lVar5 = (**(code **)(*plVar8 + 0x508))
                              (plVar8,*(undefined2 *)
                                       ((long)(piVar4 + 2) +
                                       (long)(char)(cVar12 + -1) * 8 + lVar5 + 0x14));
            if ((lVar5 != 0) && ((long)*(short *)(lVar5 + 4) != -1)) {
              *(undefined1 *)(param_12 + *(short *)(lVar5 + 4)) = 2;
            }
          }
          iVar3 = (int)cVar12;
          cVar12 = cVar12 + '\x01';
        } while (iVar3 < *piVar4);
      }
    }
    break;
  case 10:
    if ((((param_3 == 0) || (param_4 == 0)) || (param_1 == 0)) || (param_6 == 0)) {
      if (param_13 != (undefined1 *)0x0) {
        *param_13 = 0;
      }
    }
    else {
      FUN_0028cbf0(param_1,param_3 + 0x4c0,param_4 + 0x30,param_4 + 0x2b80,param_6,param_7,param_9,
                   param_12,param_13);
    }
    break;
  case 0xb:
    if (param_4 == 0) {
      if (param_13 != (undefined1 *)0x0) {
        *param_13 = 0;
      }
    }
    else {
      lVar5 = FUN_002664c0(param_4 + 8);
      plVar7 = (long *)FUN_0025a550();
      lVar6 = (**(code **)(*plVar7 + 0x68))(plVar7);
      if ((lVar5 != 0) && (0 < *(long *)(lVar5 + 0x98))) {
        lVar10 = 0;
        do {
          *(undefined1 *)
           (param_12 + *(short *)(*(long *)(lVar5 + 0xa0) + lVar5 + 0xb0 + lVar10 * 2)) = 2;
          lVar10 = lVar10 + 1;
        } while (lVar10 < *(long *)(lVar5 + 0x98));
      }
      if ((lVar6 != 0) && (lVar5 = (long)*(short *)(lVar6 + 0x1b0), lVar5 != -1)) {
        uVar2 = *(undefined4 *)(param_4 + 0x7370);
        *(undefined1 *)(param_12 + 0x2000 + lVar5 * 8) = 1;
        *(undefined4 *)(param_12 + 0x2004 + lVar5 * 8) = uVar2;
      }
    }
    break;
  case 0xc:
    plVar7 = (long *)FUN_00265100(param_2,param_4);
    plVar8 = (long *)FUN_0025a550();
    plVar8 = (long *)(**(code **)(*plVar8 + 0x2b0))(plVar8);
    if ((plVar8 != (long *)0x0) && (lVar5 = *plVar8, 0 < lVar5)) {
      lVar6 = plVar8[1];
      for (psVar9 = (short *)(lVar6 + 0x18 + (long)plVar8);
          psVar9 <= (short *)((long)plVar8 +
                             ((lVar5 << 0x20) + -0x100000000 >> 0x20) * 0x10 + lVar6 + 0x18);
          psVar9 = psVar9 + 8) {
        if (*(long *)(psVar9 + 4) <= *plVar7) {
          *(char *)(param_12 + *psVar9) = (char)psVar9[1];
        }
      }
    }
    FUN_0028d5e0(plVar7,param_12,param_12 + 0x2000);
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

