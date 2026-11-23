
void FUN_0054ed90(undefined1 *param_1,short *param_2,undefined8 param_3,char *param_4,long param_5)

{
  short sVar1;
  int iVar2;
  long lVar3;
  long *plVar4;
  long lVar5;
  char *pcVar6;
  long lVar7;
  long lVar8;
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  *(undefined4 *)(param_5 + 4) = *(undefined4 *)(param_2 + 0xe);
  *(char *)(param_5 + 8) = (char)param_2[0x10];
  lVar3 = FUN_0054c5b0(param_3,*param_2);
  if (lVar3 != 0) {
    plVar4 = (long *)FUN_0025a550();
    (**(code **)(*plVar4 + 0x390))(plVar4,*param_1,param_1[1]);
    FUN_005494c0();
    lVar5 = FUN_0054a610();
    if (lVar5 != 0) {
      lVar8 = 4;
      for (lVar7 = 0; lVar7 < *(long *)(lVar5 + 0x48); lVar7 = lVar7 + 1) {
        if (*param_2 == *(short *)(lVar5 + 0x50 + lVar8 * 4 + *(long *)(lVar5 + 0x50))) {
          *(undefined4 *)(param_5 + 0x10) =
               *(undefined4 *)(lVar5 + 0x30 + lVar7 * 4 + *(long *)(lVar5 + 0x30) + 0x10);
          break;
        }
        lVar8 = lVar8 + 10;
      }
    }
    *(undefined2 *)(param_5 + 0x56) = 0xffff;
    *(undefined1 *)(param_5 + 0x58) = 0xff;
    *(undefined2 *)(param_5 + 0x5a) = 0xffff;
    *(undefined1 *)(param_5 + 0x5c) = 0xff;
    *(undefined2 *)(param_5 + 0x5e) = 0xffff;
    *(undefined1 *)(param_5 + 0x60) = 0xff;
    *(undefined2 *)(param_5 + 0x62) = 0xffff;
    *(undefined1 *)(param_5 + 100) = 0xff;
    *(undefined2 *)(param_5 + 0x66) = 0xffff;
    *(undefined1 *)(param_5 + 0x68) = 0xff;
    *(undefined2 *)(param_5 + 0x6a) = 0xffff;
    *(undefined1 *)(param_5 + 0x54) = 0xff;
    *(undefined8 *)(param_5 + 0x4c) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x44) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x3c) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x34) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x2c) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x24) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x1c) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x14) = 0xffffffffffffffff;
    if ((*param_4 != -1) && (0 < *(long *)(lVar3 + 8))) {
      plVar4 = (long *)(*(long *)(lVar3 + 0x10) + 0x20 + lVar3);
      lVar5 = 0;
      do {
        pcVar6 = (char *)0x0;
        if (*plVar4 != 0) {
          pcVar6 = (char *)(*plVar4 + (long)plVar4);
        }
        if ((*pcVar6 == *param_4) && (*(int *)(pcVar6 + 8) != 0)) {
          local_40[0] = *(undefined4 *)(pcVar6 + *(long *)(pcVar6 + 0x10) + 0x20);
          iVar2 = FUN_0058ea60();
          if (iVar2 != -1) {
            *(int *)(param_5 + 0x14) = iVar2;
          }
          break;
        }
        plVar4 = plVar4 + 1;
        lVar5 = lVar5 + 1;
      } while (lVar5 < *(long *)(lVar3 + 8));
    }
    if ((param_4[1] != -1) && (0 < *(long *)(lVar3 + 8))) {
      plVar4 = (long *)(*(long *)(lVar3 + 0x10) + 0x20 + lVar3);
      lVar5 = 0;
      do {
        pcVar6 = (char *)0x0;
        if (*plVar4 != 0) {
          pcVar6 = (char *)(*plVar4 + (long)plVar4);
        }
        if ((*pcVar6 == param_4[1]) && (*(int *)(pcVar6 + 8) != 0)) {
          local_40[0] = *(undefined4 *)(pcVar6 + *(long *)(pcVar6 + 0x10) + 0x20);
          iVar2 = FUN_0058ea60();
          if (iVar2 != -1) {
            *(int *)(param_5 + 0x34) = iVar2;
          }
          break;
        }
        plVar4 = plVar4 + 1;
        lVar5 = lVar5 + 1;
      } while (lVar5 < *(long *)(lVar3 + 8));
    }
    if ((param_4[8] != -1) && (sVar1 = param_2[3], sVar1 != -1)) {
      lVar5 = 0;
      do {
        lVar7 = lVar5;
        if ('\x05' < (char)lVar7) goto LAB_0054f006;
        lVar5 = lVar7 + 1;
      } while (*(char *)(param_5 + 0x54 + lVar7 * 4) != -1);
      *(char *)(param_5 + 0x54 + lVar7 * 4) = (char)lVar5 + -1;
      *(short *)(param_5 + 0x52 + lVar5 * 4) = sVar1;
    }
LAB_0054f006:
    if ((param_4[9] != -1) && (sVar1 = param_2[4], sVar1 != -1)) {
      lVar5 = 0;
      do {
        lVar7 = lVar5;
        if ('\x05' < (char)lVar7) goto LAB_0054f046;
        lVar5 = lVar7 + 1;
      } while (*(char *)(param_5 + 0x54 + lVar7 * 4) != -1);
      *(char *)(param_5 + 0x54 + lVar7 * 4) = (char)lVar5 + -1;
      *(short *)(param_5 + 0x52 + lVar5 * 4) = sVar1;
    }
LAB_0054f046:
    if ((param_4[10] != -1) && (sVar1 = param_2[5], sVar1 != -1)) {
      lVar5 = 0;
      do {
        lVar7 = lVar5;
        if ('\x05' < (char)lVar7) goto LAB_0054f086;
        lVar5 = lVar7 + 1;
      } while (*(char *)(param_5 + 0x54 + lVar7 * 4) != -1);
      *(char *)(param_5 + 0x54 + lVar7 * 4) = (char)lVar5 + -1;
      *(short *)(param_5 + 0x52 + lVar5 * 4) = sVar1;
    }
LAB_0054f086:
    *(undefined2 *)(param_5 + 0xae) = 0xffff;
    *(undefined1 *)(param_5 + 0xb0) = 0xff;
    *(undefined2 *)(param_5 + 0xb2) = 0xffff;
    *(undefined1 *)(param_5 + 0xb4) = 0xff;
    *(undefined2 *)(param_5 + 0xb6) = 0xffff;
    *(undefined1 *)(param_5 + 0xb8) = 0xff;
    *(undefined2 *)(param_5 + 0xba) = 0xffff;
    *(undefined1 *)(param_5 + 0xbc) = 0xff;
    *(undefined2 *)(param_5 + 0xbe) = 0xffff;
    *(undefined1 *)(param_5 + 0xc0) = 0xff;
    *(undefined2 *)(param_5 + 0xc2) = 0xffff;
    *(undefined1 *)(param_5 + 0xac) = 0xff;
    *(undefined8 *)(param_5 + 0xa4) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x9c) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x94) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x8c) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x84) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x7c) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x74) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x6c) = 0xffffffffffffffff;
    if ((param_4[2] != -1) && (0 < *(long *)(lVar3 + 8))) {
      plVar4 = (long *)(*(long *)(lVar3 + 0x10) + 0x20 + lVar3);
      lVar5 = 0;
      do {
        pcVar6 = (char *)0x0;
        if (*plVar4 != 0) {
          pcVar6 = (char *)(*plVar4 + (long)plVar4);
        }
        if ((*pcVar6 == param_4[2]) &&
           ((ulong)(long)(char)param_2[1] < (ulong)(long)*(int *)(pcVar6 + 8))) {
          local_40[0] = *(undefined4 *)
                         (pcVar6 + (long)(char)param_2[1] * 4 + *(long *)(pcVar6 + 0x10) + 0x20);
          iVar2 = FUN_0058ea60();
          if (iVar2 != -1) {
            *(int *)(param_5 + 0x6c) = iVar2;
          }
          break;
        }
        plVar4 = plVar4 + 1;
        lVar5 = lVar5 + 1;
      } while (lVar5 < *(long *)(lVar3 + 8));
    }
    if ((param_4[3] != -1) && (0 < *(long *)(lVar3 + 8))) {
      plVar4 = (long *)(*(long *)(lVar3 + 0x10) + 0x20 + lVar3);
      lVar5 = 0;
      do {
        pcVar6 = (char *)0x0;
        if (*plVar4 != 0) {
          pcVar6 = (char *)(*plVar4 + (long)plVar4);
        }
        if ((*pcVar6 == param_4[3]) &&
           ((ulong)(long)(char)param_2[1] < (ulong)(long)*(int *)(pcVar6 + 8))) {
          iVar2 = FUN_0058ea60();
          if (iVar2 != -1) {
            *(int *)(param_5 + 0x8c) = iVar2;
          }
          break;
        }
        plVar4 = plVar4 + 1;
        lVar5 = lVar5 + 1;
      } while (lVar5 < *(long *)(lVar3 + 8));
    }
    if ((param_4[0xb] != -1) && (sVar1 = param_2[6], sVar1 != -1)) {
      lVar5 = 0;
      do {
        lVar7 = lVar5;
        if ('\x05' < (char)lVar7) goto LAB_0054f28f;
        lVar5 = lVar7 + 1;
      } while (*(char *)(param_5 + 0xac + lVar7 * 4) != -1);
      *(char *)(param_5 + 0xac + lVar7 * 4) = (char)lVar5 + -1;
      *(short *)(param_5 + 0xaa + lVar5 * 4) = sVar1;
    }
LAB_0054f28f:
    if ((param_4[0xc] != -1) && (sVar1 = param_2[7], sVar1 != -1)) {
      lVar5 = 0;
      do {
        lVar7 = lVar5;
        if ('\x05' < (char)lVar7) goto LAB_0054f2df;
        lVar5 = lVar7 + 1;
      } while (*(char *)(param_5 + 0xac + lVar7 * 4) != -1);
      *(char *)(param_5 + 0xac + lVar7 * 4) = (char)lVar5 + -1;
      *(short *)(param_5 + 0xaa + lVar5 * 4) = sVar1;
    }
LAB_0054f2df:
    if ((param_4[0xd] != -1) && (sVar1 = param_2[8], sVar1 != -1)) {
      lVar5 = 0;
      do {
        lVar7 = lVar5;
        if ('\x05' < (char)lVar7) goto LAB_0054f32f;
        lVar5 = lVar7 + 1;
      } while (*(char *)(param_5 + 0xac + lVar7 * 4) != -1);
      *(char *)(param_5 + 0xac + lVar7 * 4) = (char)lVar5 + -1;
      *(short *)(param_5 + 0xaa + lVar5 * 4) = sVar1;
    }
LAB_0054f32f:
    *(undefined2 *)(param_5 + 0x106) = 0xffff;
    *(undefined1 *)(param_5 + 0x108) = 0xff;
    *(undefined2 *)(param_5 + 0x10a) = 0xffff;
    *(undefined1 *)(param_5 + 0x10c) = 0xff;
    *(undefined2 *)(param_5 + 0x10e) = 0xffff;
    *(undefined1 *)(param_5 + 0x110) = 0xff;
    *(undefined2 *)(param_5 + 0x112) = 0xffff;
    *(undefined1 *)(param_5 + 0x114) = 0xff;
    *(undefined2 *)(param_5 + 0x116) = 0xffff;
    *(undefined1 *)(param_5 + 0x118) = 0xff;
    *(undefined2 *)(param_5 + 0x11a) = 0xffff;
    *(undefined1 *)(param_5 + 0x104) = 0xff;
    *(undefined8 *)(param_5 + 0xfc) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0xf4) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0xec) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0xe4) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0xdc) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0xd4) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0xcc) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0xc4) = 0xffffffffffffffff;
    if ((param_4[4] != -1) && (0 < *(long *)(lVar3 + 8))) {
      plVar4 = (long *)(*(long *)(lVar3 + 0x10) + 0x20 + lVar3);
      lVar5 = 0;
      do {
        pcVar6 = (char *)0x0;
        if (*plVar4 != 0) {
          pcVar6 = (char *)(*plVar4 + (long)plVar4);
        }
        if ((*pcVar6 == param_4[4]) &&
           ((ulong)(long)*(char *)((long)param_2 + 3) < (ulong)(long)*(int *)(pcVar6 + 8))) {
          local_40[0] = *(undefined4 *)
                         (pcVar6 + (long)*(char *)((long)param_2 + 3) * 4 +
                                   *(long *)(pcVar6 + 0x10) + 0x20);
          iVar2 = FUN_0058ea60();
          if (iVar2 != -1) {
            *(int *)(param_5 + 0xc4) = iVar2;
          }
          break;
        }
        plVar4 = plVar4 + 1;
        lVar5 = lVar5 + 1;
      } while (lVar5 < *(long *)(lVar3 + 8));
    }
    if ((param_4[5] != -1) && (0 < *(long *)(lVar3 + 8))) {
      plVar4 = (long *)(*(long *)(lVar3 + 0x10) + 0x20 + lVar3);
      lVar5 = 0;
      do {
        pcVar6 = (char *)0x0;
        if (*plVar4 != 0) {
          pcVar6 = (char *)(*plVar4 + (long)plVar4);
        }
        if ((*pcVar6 == param_4[5]) &&
           ((ulong)(long)*(char *)((long)param_2 + 3) < (ulong)(long)*(int *)(pcVar6 + 8))) {
          iVar2 = FUN_0058ea60();
          if (iVar2 != -1) {
            *(int *)(param_5 + 0xe4) = iVar2;
          }
          break;
        }
        plVar4 = plVar4 + 1;
        lVar5 = lVar5 + 1;
      } while (lVar5 < *(long *)(lVar3 + 8));
    }
    if ((param_4[0xe] != -1) && (sVar1 = param_2[9], sVar1 != -1)) {
      lVar5 = 0;
      do {
        lVar7 = lVar5;
        if ('\x05' < (char)lVar7) goto LAB_0054f54f;
        lVar5 = lVar7 + 1;
      } while (*(char *)(param_5 + 0x104 + lVar7 * 4) != -1);
      *(char *)(param_5 + 0x104 + lVar7 * 4) = (char)lVar5 + -1;
      *(short *)(param_5 + 0x102 + lVar5 * 4) = sVar1;
    }
LAB_0054f54f:
    if ((param_4[0xf] != -1) && (sVar1 = param_2[10], sVar1 != -1)) {
      lVar5 = 0;
      do {
        lVar7 = lVar5;
        if ('\x05' < (char)lVar7) goto LAB_0054f59f;
        lVar5 = lVar7 + 1;
      } while (*(char *)(param_5 + 0x104 + lVar7 * 4) != -1);
      *(char *)(param_5 + 0x104 + lVar7 * 4) = (char)lVar5 + -1;
      *(short *)(param_5 + 0x102 + lVar5 * 4) = sVar1;
    }
LAB_0054f59f:
    if ((param_4[0x10] != -1) && (sVar1 = param_2[0xb], sVar1 != -1)) {
      lVar5 = 0;
      do {
        lVar7 = lVar5;
        if ('\x05' < (char)lVar7) goto LAB_0054f5ef;
        lVar5 = lVar7 + 1;
      } while (*(char *)(param_5 + 0x104 + lVar7 * 4) != -1);
      *(char *)(param_5 + 0x104 + lVar7 * 4) = (char)lVar5 + -1;
      *(short *)(param_5 + 0x102 + lVar5 * 4) = sVar1;
    }
LAB_0054f5ef:
    *(undefined2 *)(param_5 + 0x15e) = 0xffff;
    *(undefined1 *)(param_5 + 0x160) = 0xff;
    *(undefined2 *)(param_5 + 0x162) = 0xffff;
    *(undefined1 *)(param_5 + 0x164) = 0xff;
    *(undefined2 *)(param_5 + 0x166) = 0xffff;
    *(undefined1 *)(param_5 + 0x168) = 0xff;
    *(undefined2 *)(param_5 + 0x16a) = 0xffff;
    *(undefined1 *)(param_5 + 0x16c) = 0xff;
    *(undefined2 *)(param_5 + 0x16e) = 0xffff;
    *(undefined1 *)(param_5 + 0x170) = 0xff;
    *(undefined2 *)(param_5 + 0x172) = 0xffff;
    *(undefined1 *)(param_5 + 0x15c) = 0xff;
    *(undefined8 *)(param_5 + 0x154) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x14c) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x144) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x13c) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x134) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 300) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x124) = 0xffffffffffffffff;
    *(undefined8 *)(param_5 + 0x11c) = 0xffffffffffffffff;
    if ((param_4[6] != -1) && (0 < *(long *)(lVar3 + 8))) {
      plVar4 = (long *)(*(long *)(lVar3 + 0x10) + 0x20 + lVar3);
      lVar5 = 0;
      do {
        pcVar6 = (char *)0x0;
        if (*plVar4 != 0) {
          pcVar6 = (char *)(*plVar4 + (long)plVar4);
        }
        if ((*pcVar6 == param_4[6]) &&
           ((ulong)(long)(char)param_2[2] < (ulong)(long)*(int *)(pcVar6 + 8))) {
          local_40[0] = *(undefined4 *)
                         (pcVar6 + (long)(char)param_2[2] * 4 + *(long *)(pcVar6 + 0x10) + 0x20);
          iVar2 = FUN_0058ea60();
          if (iVar2 != -1) {
            *(int *)(param_5 + 0x11c) = iVar2;
          }
          break;
        }
        plVar4 = plVar4 + 1;
        lVar5 = lVar5 + 1;
      } while (lVar5 < *(long *)(lVar3 + 8));
    }
    if ((param_4[7] != -1) && (0 < *(long *)(lVar3 + 8))) {
      plVar4 = (long *)(*(long *)(lVar3 + 0x10) + 0x20 + lVar3);
      lVar5 = 0;
      do {
        pcVar6 = (char *)0x0;
        if (*plVar4 != 0) {
          pcVar6 = (char *)(*plVar4 + (long)plVar4);
        }
        if ((*pcVar6 == param_4[7]) &&
           ((ulong)(long)(char)param_2[2] < (ulong)(long)*(int *)(pcVar6 + 8))) {
          local_40[0] = *(undefined4 *)
                         (pcVar6 + (long)(char)param_2[2] * 4 + *(long *)(pcVar6 + 0x10) + 0x20);
          iVar2 = FUN_0058ea60(local_40);
          if (iVar2 != -1) {
            *(int *)(param_5 + 0x13c) = iVar2;
          }
          break;
        }
        plVar4 = plVar4 + 1;
        lVar5 = lVar5 + 1;
      } while (lVar5 < *(long *)(lVar3 + 8));
    }
    if ((param_4[0x11] != -1) && (sVar1 = param_2[0xc], sVar1 != -1)) {
      lVar3 = 0;
      do {
        lVar5 = lVar3;
        if ('\x05' < (char)lVar5) goto LAB_0054f80f;
        lVar3 = lVar5 + 1;
      } while (*(char *)(param_5 + 0x15c + lVar5 * 4) != -1);
      *(char *)(param_5 + 0x15c + lVar5 * 4) = (char)lVar3 + -1;
      *(short *)(param_5 + 0x15a + lVar3 * 4) = sVar1;
    }
  }
LAB_0054f80f:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

