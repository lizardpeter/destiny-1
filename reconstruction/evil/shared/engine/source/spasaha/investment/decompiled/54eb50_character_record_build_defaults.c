
undefined1 FUN_0054eb50(undefined1 *param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  undefined4 *puVar5;
  undefined8 uVar6;
  long *plVar7;
  long lVar8;
  long lVar9;
  long lVar10;
  undefined8 extraout_RDX;
  long lVar11;
  long lVar12;
  long lVar13;
  undefined1 auVar14 [16];
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar4 = FUN_005494c0();
  FUN_0054a010(uVar4);
  FUN_0054dd80(param_2);
  *param_2 = param_1[2];
  param_2[1] = param_1[1];
  param_2[2] = *param_1;
  auVar14 = FUN_0054a0f0(uVar4,param_1[2]);
  if ((auVar14._0_8_ == 0) || (auVar14._8_8_ == 0)) {
    *(undefined4 *)(param_2 + 0xc) = 0xffffffff;
  }
  else {
    puVar5 = (undefined4 *)FUN_0054c7b0(uVar4,*(undefined2 *)(auVar14._8_8_ + 4));
    uVar6 = FUN_0033fa20();
    local_40[0] = *puVar5;
    uVar3 = FUN_0033fc20(uVar6,local_40);
    *(undefined4 *)(param_2 + 0xc) = uVar3;
  }
  FUN_0054ed90(param_1,param_1 + 4,uVar4,extraout_RDX,param_2);
  plVar7 = (long *)FUN_0025a550();
  lVar8 = (**(code **)(*plVar7 + 0x388))(plVar7,param_1[2]);
  uVar2 = 1;
  if ((lVar8 != 0) && (0 < *(long *)(lVar8 + 0x18))) {
    uVar2 = 1;
    lVar13 = 0;
    do {
      lVar9 = *(long *)(lVar8 + 0x20);
      plVar7 = (long *)FUN_0025cbd0();
      lVar9 = (**(code **)(*plVar7 + 0x410))
                        (plVar7,*(undefined2 *)(lVar8 + 0x20 + lVar13 * 2 + lVar9 + 0x10));
      uVar1 = 0;
      if (((lVar9 != 0) && (uVar1 = uVar2, *(long *)(lVar9 + 0x18) != 0)) &&
         (lVar10 = *(long *)(lVar9 + 0x60), lVar10 != 0)) {
        lVar11 = lVar9 + 0x60 + lVar10;
        lVar12 = (long)*(char *)(lVar9 + 0x30 + *(long *)(lVar9 + 0x18));
        lVar10 = FUN_0054c5b0(uVar4,*(undefined2 *)
                                     (*(long *)(lVar9 + 0x68 + lVar10) + 0x1a + lVar11));
        if (lVar10 != 0) {
          FUN_00289d40(0,lVar9,0,0,param_2 + lVar12 * 0x40 + 0x618);
          FUN_0054f840(uVar4,param_1[1],lVar10,*(undefined2 *)(lVar11 + 0x60),0,0,0,
                       param_2 + lVar12 * 0x20 + 0x178);
        }
      }
      uVar2 = uVar1;
      lVar13 = lVar13 + 1;
    } while (lVar13 < *(long *)(lVar8 + 0x18));
  }
  if (*DAT_01a1f100 != local_38) {
    uVar2 = thunk_FUN_012aa7f6();
    return uVar2;
  }
  return uVar2;
}

