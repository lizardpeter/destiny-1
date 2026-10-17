
undefined4 FUN_000d8970(undefined8 param_1,undefined4 *param_2)

{
  long *plVar1;
  long lVar2;
  ushort uVar3;
  long lVar4;
  ulong uVar5;
  long *plVar6;
  int iVar7;
  uint uVar8;
  long lVar9;
  ushort uVar10;
  long lVar11;
  uint uVar12;
  ulong uVar13;
  long lVar14;
  long lVar15;
  undefined4 local_54;
  ulong local_48;
  
  plVar6 = DAT_025820a8;
  local_54 = 0xffffffff;
  if (DAT_025838b0 != 0xffff) {
    plVar1 = DAT_025820a8 + 1;
    uVar8 = 0xffff;
    local_48 = 0;
    local_54 = 0xffffffff;
    uVar10 = DAT_025838b0;
    do {
      lVar14 = plVar6[2] * (ulong)uVar10;
      lVar4 = *plVar6;
      lVar11 = *(long *)((long)plVar6 + lVar14 + 0x248 + lVar4);
      if (lVar11 != DAT_01ad4f48) {
        uVar3 = *(ushort *)((long)plVar6 + lVar14 + 4 + lVar4);
        uVar12 = (uint)(short)uVar3;
        if (uVar12 != (uVar8 & 0xffff)) {
          if (*(int *)((long)plVar6 + lVar14 + 0xec + lVar4) == 0) {
            uVar8 = (uint)uVar3;
          }
          else {
            lVar11 = lVar11 + *(long *)(&DAT_01ad5030 +
                                       (ulong)DAT_0257a072 * DAT_01ad5010 + DAT_01ad5000);
            uVar13 = 0;
            uVar8 = uVar12;
            if (param_2 == (undefined4 *)0x0) {
              do {
                lVar2 = lVar11 + 8 + uVar13 * 0x44;
                iVar7 = FUN_00065290(lVar2,0x3c);
                lVar9 = thunk_FUN_012aa816(param_1);
                if (lVar9 <= iVar7) {
                  lVar9 = (long)iVar7;
                }
                if (0x3c < lVar9) {
                  lVar9 = 0x3c;
                }
                iVar7 = FUN_00064f00(lVar2,param_1,lVar9);
                if ((iVar7 == 0) &&
                   (uVar5 = *(ulong *)((long)plVar6 + lVar14 + lVar4 + 0x10), local_48 < uVar5)) {
                  local_54 = *(undefined4 *)(lVar11 + uVar13 * 0x44);
                  local_48 = uVar5;
                }
                uVar12 = (int)uVar13 + 1;
                uVar13 = (ulong)uVar12;
              } while (uVar12 < *(uint *)((long)plVar6 + lVar14 + lVar4 + 0xec));
            }
            else {
              do {
                lVar15 = uVar13 * 0x44;
                lVar2 = lVar11 + 8 + lVar15;
                iVar7 = FUN_00065290(lVar2,0x3c);
                lVar9 = thunk_FUN_012aa816(param_1);
                if (lVar9 <= iVar7) {
                  lVar9 = (long)iVar7;
                }
                if (0x3c < lVar9) {
                  lVar9 = 0x3c;
                }
                iVar7 = FUN_00064f00(lVar2,param_1,lVar9);
                if ((iVar7 == 0) &&
                   (uVar5 = *(ulong *)((long)plVar6 + lVar14 + lVar4 + 0x10), local_48 < uVar5)) {
                  local_54 = *(undefined4 *)(lVar11 + lVar15);
                  *param_2 = *(undefined4 *)(lVar11 + 4 + lVar15);
                  local_48 = uVar5;
                }
                uVar12 = (int)uVar13 + 1;
                uVar13 = (ulong)uVar12;
              } while (uVar12 < *(uint *)((long)plVar6 + lVar14 + lVar4 + 0xec));
            }
          }
        }
      }
    } while ((uVar10 != 0xffff) &&
            (uVar10 = *(ushort *)((long)plVar1 + (ulong)uVar10 * 4 + *plVar1), uVar10 != 0xffff));
  }
  return local_54;
}

