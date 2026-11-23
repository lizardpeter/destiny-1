
undefined8
FUN_00269a50(undefined8 param_1,undefined8 param_2,long param_3,undefined8 *param_4,long *param_5,
            byte *param_6)

{
  undefined1 uVar1;
  char cVar2;
  int iVar3;
  uint uVar4;
  long *plVar5;
  long lVar6;
  undefined8 uVar7;
  long lVar8;
  long lVar9;
  int *piVar10;
  undefined1 uVar11;
  undefined **local_50;
  long local_48;
  undefined4 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  plVar5 = (long *)FUN_0025a550();
  lVar6 = (**(code **)(*plVar5 + 0x410))(plVar5,*(undefined2 *)((long)param_5 + 0x24));
  if (lVar6 != 0) {
    uVar7 = FUN_00265e30();
    lVar8 = FUN_0026c2a0(uVar7,*(undefined1 *)(lVar6 + 0x88));
    if ((((lVar8 == 0) || (*(char *)(lVar8 + 0x11) != '\0')) || (*(long *)(lVar6 + 0x18) == 0)) ||
       (lVar8 = *(long *)(lVar6 + 0x18) + lVar6 + 0x18, lVar8 == 0)) {
      uVar11 = 0;
      if (param_6 == (byte *)0x0) goto LAB_00269b8e;
      *param_6 = *param_6 | 1;
    }
    else {
      uVar11 = *(undefined1 *)(lVar8 + 0x18);
      plVar5 = (long *)FUN_0025a550();
      lVar9 = (**(code **)(*plVar5 + 0x3d0))(plVar5,uVar11);
      cVar2 = FUN_0028eba0(lVar9 + 8);
      uVar11 = 1;
      if (((cVar2 != '\0') && (cVar2 = FUN_0028e560(param_1,lVar9 + 8), cVar2 == '\0')) &&
         (uVar11 = 0, param_6 != (byte *)0x0)) {
        *param_6 = *param_6 | 0x20;
      }
      uVar1 = *(undefined1 *)(lVar8 + 0x18);
      plVar5 = (long *)FUN_0025a550();
      lVar9 = (**(code **)(*plVar5 + 0x3d0))(plVar5,uVar1);
      cVar2 = FUN_0028eba0(lVar9 + 0x18);
      if (((cVar2 != '\0') && (cVar2 = FUN_0028e560(param_1,lVar9 + 0x18), cVar2 == '\0')) &&
         (((*param_5 == 0 ||
           (((*(long *)(lVar6 + 0x18) == 0 ||
             (cVar2 = *(char *)(lVar6 + 0x30 + *(long *)(lVar6 + 0x18)),
             *(long *)(param_3 + (long)cVar2 * 8) != *param_5)) || (cVar2 == -1)))) &&
          (uVar11 = 0, param_6 != (byte *)0x0)))) {
        *param_6 = *param_6 | 0x40;
      }
      plVar5 = (long *)FUN_0025a550();
      piVar10 = (int *)(**(code **)(*plVar5 + 0x1a8))(plVar5);
      if (0 < *piVar10) {
        plVar5 = (long *)(piVar10 + 2);
        cVar2 = '\x01';
        if (param_6 == (byte *)0x0) {
          do {
            iVar3 = FUN_00276510(param_2,*(undefined2 *)
                                          ((long)plVar5 +
                                          (long)(char)(cVar2 + -1) * 8 +
                                          *(long *)(piVar10 + 2) + 0x14));
            uVar1 = 0;
            if (*(int *)((long)param_5 + (long)(char)(cVar2 + -1) * 4 + 0x1c) <= iVar3) {
              uVar1 = uVar11;
            }
            uVar11 = uVar1;
            iVar3 = (int)cVar2;
            cVar2 = cVar2 + '\x01';
          } while (iVar3 < *piVar10);
        }
        else {
          do {
            iVar3 = FUN_00276510(param_2,*(undefined2 *)
                                          ((long)plVar5 +
                                          (long)(char)(cVar2 + -1) * 8 + *plVar5 + 0x14));
            if (iVar3 < *(int *)((long)param_5 + (long)(char)(cVar2 + -1) * 4 + 0x1c)) {
              *param_6 = *param_6 | 8;
              uVar11 = 0;
            }
            iVar3 = (int)cVar2;
            cVar2 = cVar2 + '\x01';
          } while (iVar3 < *piVar10);
        }
      }
      if (*(int *)(lVar8 + 0x14) != 0) {
        local_50 = &PTR_FUN_0190fa00;
        local_40._1_3_ = (uint3)(local_40 >> 8) & 0xffff00;
        local_40 = CONCAT31(local_40._1_3_,0xff);
        local_48 = param_3;
        plVar5 = (long *)FUN_0025a550();
        piVar10 = (int *)(**(code **)(*plVar5 + 0x100))(plVar5);
        local_40._0_2_ = (ushort)(byte)local_40;
        do {
          if (*piVar10 <= (int)(char)local_40) {
            uVar4 = local_40 >> 8;
            break;
          }
          local_40 = CONCAT31(local_40._1_3_,(char)local_40 + '\x01');
          cVar2 = (*(code *)local_50[1])(&local_50);
          if (cVar2 != '\0') goto LAB_00269d58;
          uVar4 = (uint)local_40._1_1_;
        } while (local_40._1_1_ == 0);
LAB_00269e2e:
        if ((char)uVar4 != '\0') {
          if ((((byte)local_40 != *(char *)(lVar8 + 0x18)) &&
              (*(long *)(local_48 + (long)(char)(byte)local_40 * 8) != 0)) &&
             (lVar6 = (**(code **)*param_4)(param_4,local_48 + (long)(char)(byte)local_40 * 8),
             lVar6 != 0)) {
            plVar5 = (long *)FUN_0025a550();
            lVar6 = (**(code **)(*plVar5 + 0x410))(plVar5,*(undefined2 *)(lVar6 + 0x24));
            if (((lVar6 != 0) && (*(long *)(lVar6 + 0x18) != 0)) &&
               ((iVar3 = *(int *)(lVar6 + 0x2c + *(long *)(lVar6 + 0x18)), iVar3 != 0 &&
                ((iVar3 == *(int *)(lVar8 + 0x14) && (uVar11 = 0, param_6 != (byte *)0x0)))))) {
              *param_6 = *param_6 | 2;
            }
          }
          plVar5 = (long *)FUN_0025a550();
          piVar10 = (int *)(**(code **)(*plVar5 + 0x100))(plVar5);
          local_40._0_2_ = (ushort)(byte)local_40;
          do {
            uVar4 = local_40 >> 8 & 0xff;
            if (*piVar10 <= (int)(char)local_40) break;
            local_40 = CONCAT31(local_40._1_3_,(char)local_40 + '\x01');
            cVar2 = (*(code *)local_50[1])(&local_50);
            if (cVar2 != '\0') goto LAB_00269d58;
            uVar4 = (uint)local_40._1_1_;
          } while (local_40._1_1_ == 0);
          goto LAB_00269e2e;
        }
      }
      cVar2 = FUN_0028ea60(param_1,lVar8);
      if (cVar2 != '\0') goto LAB_00269b8e;
      if (param_6 != (byte *)0x0) {
        *param_6 = *param_6 | 4;
      }
    }
  }
  uVar11 = 0;
LAB_00269b8e:
  if (*DAT_01a1f100 != local_38) {
    uVar7 = thunk_FUN_012aa7f6();
    return uVar7;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar11);
LAB_00269d58:
  local_40._0_2_ = CONCAT11(1,(byte)local_40);
  uVar4 = 1;
  goto LAB_00269e2e;
}

