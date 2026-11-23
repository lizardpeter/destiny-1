
void FUN_005906d0(long param_1,long *param_2)

{
  undefined1 uVar1;
  undefined8 uVar2;
  long lVar3;
  long *plVar4;
  long lVar5;
  uint uVar6;
  ushort uVar7;
  long lVar8;
  long lVar9;
  bool bVar10;
  undefined1 auVar11 [16];
  undefined1 local_e8 [16];
  undefined8 *local_d8 [2];
  char local_c7;
  undefined1 local_b8 [128];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (DAT_0295d370 == '\0') {
    lVar5 = *(long *)(PTR_DAT_019e4dc8 + 8);
    uVar2 = FUN_000e8680(lVar5,0,0xffffffff);
    thunk_FUN_012aa986(local_b8,0,uVar2);
    uVar7 = *(ushort *)(lVar5 + 0x1c) & 0x78;
    bVar10 = uVar7 != 0;
    if (uVar7 == 0) {
      uVar6 = *(uint *)(lVar5 + 0x20);
      if ((*(ushort *)(lVar5 + 0x1c) & 0x40) != 0) {
        lVar3 = FUN_000e8a90(lVar5,local_b8);
        if (lVar3 == 0) {
          uVar6 = uVar6 | 0x5488bf;
        }
        else {
          uVar6 = *(uint *)(lVar3 + 0x20) & 0x5488bf | uVar6;
        }
      }
      bVar10 = (uVar6 & 0xc08070) != 0;
    }
    if (bVar10) {
      FUN_000e6730(lVar5,local_b8,0,0xffffffff,0);
    }
    thunk_FUN_012aa7c6(&DAT_0295d2e5,local_b8,0x80);
    DAT_0295d370 = '\x01';
  }
  thunk_FUN_012aa7c6(param_1,&DAT_0295d2e5,0x80);
  plVar4 = (long *)FUN_0025a550();
  (**(code **)(*plVar4 + 0x240))(plVar4);
  lVar5 = (**(code **)(*param_2 + 0x10))(param_2);
  lVar3 = FUN_002601f0(param_2);
  FUN_002693a0(local_d8,lVar5 + 0x2b80,lVar3 + 0x4804);
  FUN_002692a0(local_d8);
  if (local_c7 != '\0') {
    do {
      uVar2 = (*(code *)*local_d8[0])(local_d8);
      lVar5 = (**(code **)(*param_2 + 0x38))(param_2,uVar2);
      if (*(short *)(lVar5 + 0x58) != -1) {
        uVar2 = FUN_005494c0();
        auVar11 = FUN_0054b1b0(uVar2,*(undefined2 *)(lVar5 + 0x24));
        local_e8 = auVar11;
        if ((auVar11._0_8_ != 0) && (auVar11._8_8_ != 0)) {
          uVar1 = FUN_005537e0(local_e8);
          uVar2 = FUN_005494c0();
          lVar5 = FUN_0054c270(uVar2,uVar1);
          if ((lVar5 != 0) && (0 < *(long *)(lVar5 + 0x20))) {
            lVar3 = 0;
            lVar8 = 0x10;
            do {
              lVar9 = (long)*(char *)(lVar8 + *(long *)(lVar5 + 0x28) + lVar5 + 0x28);
              *(undefined1 *)(param_1 + lVar9 * 2) = uVar1;
              *(char *)(param_1 + 1 + lVar9 * 2) = (char)lVar3;
              lVar8 = lVar8 + 0x28;
              lVar3 = lVar3 + 1;
            } while (lVar3 < *(long *)(lVar5 + 0x20));
          }
        }
      }
      FUN_00269300(local_d8);
    } while (local_c7 != '\0');
  }
  *(byte *)(param_1 + 0x4580) = *(byte *)(param_1 + 0x4580) & 0xfb;
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

