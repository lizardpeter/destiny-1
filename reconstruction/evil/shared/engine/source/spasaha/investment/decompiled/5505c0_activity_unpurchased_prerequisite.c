
ulong FUN_005505c0(undefined4 param_1)

{
  long lVar1;
  char cVar2;
  uint uVar3;
  long lVar4;
  undefined8 uVar5;
  long lVar6;
  long lVar7;
  ulong uVar8;
  long lVar9;
  long *plVar10;
  undefined1 auVar11 [16];
  long *local_e8 [2];
  undefined1 local_d8 [80];
  long local_88 [10];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar4 = FUN_005753c0(4);
  if ((lVar4 != 0) && (cVar2 = FUN_00549510(), cVar2 != '\0')) {
    uVar5 = FUN_005494c0();
    auVar11 = FUN_005498e0(uVar5,param_1);
    lVar7 = auVar11._8_8_;
    lVar9 = auVar11._0_8_;
    if ((lVar9 != 0) && (lVar7 != 0)) {
      plVar10 = local_88;
      FUN_00544910(plVar10,lVar4,lVar9,lVar7);
      FUN_00544820(local_d8,lVar4,lVar9,lVar7);
      lVar9 = 1;
      local_e8[1] = (long *)local_d8;
      local_e8[0] = plVar10;
      while( true ) {
        (**(code **)*plVar10)(plVar10);
        while ((char)plVar10[5] != '\0') {
          uVar5 = FUN_00263a60(plVar10);
          cVar2 = FUN_0028e530(lVar4,uVar5);
          uVar8 = 0xffffffff;
          if ((cVar2 == '\0') && (uVar3 = FUN_00544780(plVar10), uVar3 != 0xffffffff)) {
            lVar6 = (ulong)(((uint)((int)uVar3 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar3 >> 0xd) * 0x40;
            lVar7 = *DAT_01a238a0;
            lVar1 = *(long *)(lVar7 + 0x10 + lVar6);
            uVar8 = (ulong)((uVar3 & 0x1fff) * *(int *)(lVar7 + 0x30 + lVar6));
            if (*(int *)(((lVar1 + uVar8) -
                         ((long)*(int *)(lVar7 + 0x34 + lVar6) & *(ulong *)(lVar1 + 8 + uVar8))) +
                        0xc) == -0x7ee3623b) {
              uVar3 = 0xffffffff;
            }
            uVar8 = (ulong)uVar3;
          }
          (**(code **)(*plVar10 + 8))(plVar10);
          if ((int)uVar8 != -1) goto LAB_0055073e;
        }
        if (1 < (uint)lVar9) break;
        plVar10 = local_e8[lVar9];
        lVar9 = lVar9 + 1;
      }
    }
  }
  uVar8 = 0xffffffff;
LAB_0055073e:
  if (*DAT_01a1f100 != local_38) {
    uVar8 = thunk_FUN_012aa7f6();
    return uVar8;
  }
  return uVar8;
}

