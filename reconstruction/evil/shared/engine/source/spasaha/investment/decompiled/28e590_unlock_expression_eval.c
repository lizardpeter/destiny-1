
ulong FUN_0028e590(long param_1,long *param_2)

{
  long *plVar1;
  byte bVar2;
  long lVar3;
  ulong uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  long lVar8;
  bool bVar9;
  uint local_154;
  uint local_138 [64];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_154 = 0;
  if (((int)*param_2 != 0) && (0 < *param_2)) {
    plVar1 = param_2 + 1;
    iVar5 = -1;
    lVar8 = 0;
    do {
      lVar3 = *plVar1;
      uVar6 = (uint)*(char *)((long)plVar1 + lVar8 * 8 + lVar3 + 0x10);
      if (uVar6 < 0x15) {
        if (uVar6 < 10) {
          if (uVar6 == 1) {
            iVar7 = iVar5 + 1;
            bVar9 = iVar5 < 0x3f;
            iVar5 = iVar7;
            if (bVar9) {
              bVar2 = FUN_0028cfe0(param_1,*(undefined4 *)((long)plVar1 + lVar8 * 8 + lVar3 + 0x14))
              ;
              local_138[iVar7] = (uint)bVar2;
              goto LAB_0028e75a;
            }
            break;
          }
          if (uVar6 != 2) goto LAB_0028e930;
          if (iVar5 < 0) goto switchD_0028e627_caseD_a;
          local_138[iVar5] = (uint)(local_138[iVar5] == 0);
        }
        else if (uVar6 == 10) {
          iVar7 = iVar5 + 1;
          bVar9 = 0x3e < iVar5;
          iVar5 = iVar7;
          if (bVar9) break;
          uVar6 = FUN_0028d160(param_1 + 0x2000,
                               *(undefined4 *)((long)plVar1 + lVar8 * 8 + lVar3 + 0x14));
          local_138[iVar7] = uVar6;
        }
        else {
          if (uVar6 != 0xb) goto LAB_0028e930;
          iVar7 = iVar5 + 1;
          bVar9 = 0x3e < iVar5;
          iVar5 = iVar7;
          if (bVar9) break;
          local_138[iVar7] = *(uint *)((long)plVar1 + lVar8 * 8 + lVar3 + 0x14);
        }
      }
      else {
        if (uVar6 == 0x15) {
          if (-1 < iVar5) {
            local_138[iVar5] = -local_138[iVar5];
            goto LAB_0028e75a;
          }
          goto switchD_0028e627_caseD_a;
        }
LAB_0028e930:
        if (iVar5 < 1) break;
        switch(uVar6) {
        case 3:
          lVar3 = (long)(iVar5 + -1);
          bVar9 = true;
          if (local_138[lVar3] == 0) {
LAB_0028e670:
            bVar9 = local_138[iVar5] == 0;
            goto LAB_0028e67b;
          }
          break;
        case 4:
          lVar3 = (long)(iVar5 + -1);
          bVar9 = false;
          if (local_138[lVar3] != 0) goto LAB_0028e670;
          break;
        case 5:
          lVar3 = (long)(iVar5 + -1);
          bVar9 = false;
          if (local_138[lVar3] == 0) {
LAB_0028e6b1:
            bVar9 = local_138[iVar5] == 0;
          }
          break;
        case 6:
        case 9:
          lVar3 = (long)(iVar5 + -1);
          bVar9 = local_138[lVar3] == local_138[iVar5];
LAB_0028e67b:
          bVar9 = !bVar9;
          break;
        case 7:
          lVar3 = (long)(iVar5 + -1);
          bVar9 = true;
          if (local_138[lVar3] != 0) goto LAB_0028e6b1;
          break;
        case 8:
          lVar3 = (long)(iVar5 + -1);
          bVar9 = local_138[lVar3] == local_138[iVar5];
          break;
        default:
          goto switchD_0028e627_caseD_a;
        case 0xc:
          lVar3 = (long)(iVar5 + -1);
          bVar9 = (int)local_138[iVar5] < (int)local_138[lVar3];
          break;
        case 0xd:
          lVar3 = (long)(iVar5 + -1);
          bVar9 = (int)local_138[iVar5] <= (int)local_138[lVar3];
          break;
        case 0xe:
          lVar3 = (long)(iVar5 + -1);
          bVar9 = (int)local_138[lVar3] < (int)local_138[iVar5];
          break;
        case 0xf:
          lVar3 = (long)(iVar5 + -1);
          bVar9 = (int)local_138[lVar3] <= (int)local_138[iVar5];
          break;
        case 0x10:
          local_138[iVar5 + -1] = local_138[iVar5 + -1] + local_138[iVar5];
          goto LAB_0028e758;
        case 0x11:
          local_138[iVar5 + -1] = local_138[iVar5 + -1] - local_138[iVar5];
          goto LAB_0028e758;
        case 0x12:
          local_138[iVar5 + -1] = local_138[iVar5] * local_138[iVar5 + -1];
          goto LAB_0028e758;
        case 0x13:
          if (local_138[iVar5] != 0) {
            local_138[iVar5 + -1] = (int)local_138[iVar5 + -1] / (int)local_138[iVar5];
            goto LAB_0028e758;
          }
          goto switchD_0028e627_caseD_a;
        case 0x14:
          if (local_138[iVar5] != 0) {
            local_138[iVar5 + -1] = (int)local_138[iVar5 + -1] % (int)local_138[iVar5];
            goto LAB_0028e758;
          }
          goto switchD_0028e627_caseD_a;
        }
        local_138[lVar3] = (uint)bVar9;
LAB_0028e758:
        iVar5 = iVar5 + -1;
      }
LAB_0028e75a:
      lVar8 = lVar8 + 1;
    } while (lVar8 < *param_2);
    if (iVar5 == 0) {
      local_154 = local_138[0];
    }
  }
switchD_0028e627_caseD_a:
  if (*DAT_01a1f100 == local_38) {
    return (ulong)local_154;
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

