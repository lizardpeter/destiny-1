
void FUN_0056c780(long param_1,int param_2,undefined8 param_3,int *param_4,undefined8 param_5)

{
  long lVar1;
  long lVar2;
  char cVar3;
  int iVar4;
  undefined8 uVar5;
  long lVar6;
  long *plVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  long lVar10;
  uint uVar11;
  ulong uVar12;
  uint *puVar13;
  int iVar14;
  long local_7848;
  long local_7840;
  uint local_7838;
  long local_7830;
  uint local_7828;
  undefined1 local_7820 [320];
  undefined1 local_76e0 [20];
  undefined4 local_76cc;
  undefined1 local_7608 [30160];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar5 = FUN_00021860(&DAT_026bc270);
  local_76cc = 1;
  FUN_00072240(local_76e0,param_5,param_4[3]);
  local_7848 = *(long *)(param_4 + 1);
  lVar6 = FUN_0056cb20(param_1,param_2,param_3);
  if (lVar6 == 0) {
    FUN_00575990(uVar5,2);
  }
  else {
    puVar13 = (uint *)((long)param_2 * 0x60 + 0x4fd9c + param_1);
    lVar6 = lVar6 + 2;
    iVar14 = 0;
    do {
      if (puVar13[-3] != 0xffffffff) {
        uVar11 = (int)*puVar13 >> 0xd;
        lVar10 = (ulong)((uVar11 >> 0x12 | 0x3ff) & uVar11) * 0x40;
        lVar1 = *DAT_01a238a0;
        lVar2 = *(long *)(lVar1 + 0x10 + lVar10);
        uVar12 = (ulong)((*puVar13 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar10));
        if (*(int *)(((lVar2 + uVar12) -
                     ((long)*(int *)(lVar1 + 0x34 + lVar10) & *(ulong *)(lVar2 + 8 + uVar12))) + 8)
            == *param_4) {
          if (iVar14 != -1) {
            local_7838 = puVar13[-2];
            local_7828 = *puVar13;
            local_7830 = (long)(int)puVar13[-1];
            if ((ulong)puVar13[-3] == 0xffffffff) {
              local_7840 = 0;
            }
            else {
              local_7840 = param_1 + 0x40a0 + (ulong)puVar13[-3];
            }
            plVar7 = (long *)FUN_0056cc40(param_1,&local_7840,lVar6,&local_7848,param_2,iVar14);
            if (plVar7 == (long *)0x0) {
              FUN_00575990(uVar5,4);
            }
            else {
              lVar6 = *plVar7;
              if (lVar6 != 0) {
                thunk_FUN_012aa7c6(local_7608,plVar7,local_7830);
              }
              FUN_00072400(local_76e0);
              uVar11 = local_7828;
              FUN_002c9a90(local_7828,local_76e0,plVar7,plVar7,1);
              FUN_00072650(local_76e0);
              if (*plVar7 == local_7848) {
                if (lVar6 == 0) {
                  FUN_0056e420(plVar7,uVar11,param_2,param_3,iVar14);
                }
                else {
                  iVar4 = thunk_FUN_012aa826(local_7608,plVar7,local_7830);
                  if (iVar4 != 0) {
                    FUN_0056e580(local_7608,plVar7,uVar11,param_2,param_3,iVar14);
                  }
                }
              }
              else {
                cVar3 = FUN_000e4d70(8,4);
                if (cVar3 != '\0') {
                  if ((DAT_026bad20 == '\0') &&
                     (iVar4 = thunk_FUN_012aa7d6(&DAT_026bad20), iVar4 != 0)) {
                    DAT_026bad18 = FUN_000e4a10(s_networking_investment_server_obj_0163c809);
                    thunk_FUN_012aa7e6(&DAT_026bad20);
                  }
                  lVar1 = local_7848;
                  lVar6 = *plVar7;
                  uVar8 = FUN_000e9fa0(param_2);
                  uVar9 = FUN_000e9fa0(iVar14);
                  FUN_01008290(local_7820,s_networking_investment_server_obj_0163c809,lVar1,lVar6,
                               uVar8,uVar9);
                  FUN_000e4aa0(DAT_026bad18,local_7820);
                }
                FUN_00575990(uVar5,5);
              }
            }
            goto LAB_0056c8cf;
          }
          break;
        }
      }
      lVar6 = lVar6 + 4;
      puVar13 = puVar13 + 4;
      iVar14 = iVar14 + 1;
    } while (iVar14 < 6);
    FUN_00575990(uVar5,3);
  }
LAB_0056c8cf:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

