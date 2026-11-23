
void FUN_0056cda0(long param_1,int param_2,undefined8 param_3,int *param_4)

{
  uint uVar1;
  long lVar2;
  long lVar3;
  undefined8 uVar4;
  char *pcVar5;
  undefined8 *puVar6;
  uint uVar7;
  long lVar8;
  ulong uVar9;
  long lVar10;
  long lVar11;
  int iVar12;
  undefined8 local_7630;
  long local_7628;
  undefined4 local_7620;
  long local_7618;
  undefined4 local_7610;
  undefined1 local_7608 [30160];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar4 = FUN_00021860(&DAT_026bc270);
  local_7630 = *(undefined8 *)(param_4 + 1);
  pcVar5 = (char *)FUN_0056cb20(param_1,param_2,param_3);
  if (pcVar5 == (char *)0x0) {
    FUN_00575990(uVar4,2);
  }
  else {
    lVar8 = (long)param_2 * 0x60 + 0x4fd9c + param_1;
    iVar12 = 0;
    lVar11 = 0;
    do {
      if (*(int *)(lVar8 + -0xc + lVar11 * 4) != -1) {
        uVar1 = *(uint *)(lVar8 + lVar11 * 4);
        uVar7 = (int)uVar1 >> 0xd;
        lVar10 = (ulong)((uVar7 >> 0x12 | 0x3ff) & uVar7) * 0x40;
        lVar2 = *DAT_01a238a0;
        lVar3 = *(long *)(lVar2 + 0x10 + lVar10);
        uVar9 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar10));
        if (*(int *)(((lVar3 + uVar9) -
                     ((long)*(int *)(lVar2 + 0x34 + lVar10) & *(ulong *)(lVar3 + 8 + uVar9))) + 8)
            == *param_4) {
          if ((int)lVar11 != -4) {
            lVar8 = (long)*pcVar5 * 0x60 + param_1;
            local_7620 = *(undefined4 *)(lVar8 + 0x4fd94 + lVar11 * 4);
            local_7610 = *(undefined4 *)(lVar8 + 0x4fd9c + lVar11 * 4);
            local_7618 = (long)*(int *)(lVar8 + 0x4fd98 + lVar11 * 4);
            uVar9 = (ulong)*(uint *)(lVar8 + 0x4fd90 + lVar11 * 4);
            if (uVar9 == 0xffffffff) {
              local_7628 = 0;
            }
            else {
              local_7628 = param_1 + 0x40a0 + uVar9;
            }
            puVar6 = (undefined8 *)
                     FUN_0056cfe0(param_1,&local_7628,pcVar5 + lVar11 + 2,&local_7630,param_2,iVar12
                                 );
            lVar8 = local_7618;
            if (puVar6 == (undefined8 *)0x0) {
              FUN_00575990(uVar4,4);
            }
            else {
              thunk_FUN_012aa7c6(local_7608,puVar6,local_7618);
              thunk_FUN_012aa986(puVar6,0,lVar8);
              *puVar6 = 0;
              FUN_0056f940(local_7608,local_7610,param_2,param_3,iVar12);
            }
            goto LAB_0056ceb0;
          }
          break;
        }
      }
      lVar11 = lVar11 + 4;
      iVar12 = iVar12 + 1;
    } while (iVar12 < 6);
    FUN_00575990(uVar4,3);
  }
LAB_0056ceb0:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

