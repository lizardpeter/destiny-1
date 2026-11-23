
void FUN_00798410(long param_1)

{
  char cVar1;
  int iVar2;
  long lVar3;
  undefined8 uVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  uint uVar8;
  ushort uVar9;
  undefined8 unaff_RBX;
  ulong uVar10;
  bool bVar11;
  undefined1 local_c8 [2];
  undefined2 local_c6;
  undefined1 local_c4;
  undefined4 local_c0;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  switch(*(undefined4 *)(param_1 + 0x30)) {
  case 0:
    FUN_00753a60(param_1 + 0x40);
    iVar2 = *(int *)(param_1 + 0x140);
    cVar1 = FUN_00788e50();
    if ((iVar2 - 5U < 2) && (cVar1 != '\0')) {
      *(undefined4 *)(param_1 + 0x30) = 1;
    }
    break;
  case 1:
    FUN_007987e0(param_1);
    break;
  case 2:
    cVar1 = FUN_007777b0(0,9);
    if (cVar1 != '\0') {
      if ((DAT_0295c100 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_0295c100), iVar2 != 0)) {
        DAT_0295c0a0 = &PTR_FUN_01914b60;
        thunk_FUN_012aa7e6(&DAT_0295c100);
      }
      cVar1 = FUN_0033e150(&DAT_0295c0a0);
      if (cVar1 != '\0') {
        if ((DAT_0295c100 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_0295c100), iVar2 != 0)) {
          DAT_0295c0a0 = &PTR_FUN_01914b60;
          thunk_FUN_012aa7e6(&DAT_0295c100);
        }
        FUN_0033e110(&DAT_0295c0a0);
      }
    }
    if ((DAT_0295c100 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_0295c100), iVar2 != 0)) {
      DAT_0295c0a0 = &PTR_FUN_01914b60;
      thunk_FUN_012aa7e6(&DAT_0295c100);
    }
    cVar1 = FUN_0033e150(&DAT_0295c0a0);
    if (cVar1 == '\0') {
      lVar3 = FUN_00775770(0);
      lVar3 = FUN_011c3f80(lVar3 + 0x9b8);
      uVar10 = CONCAT62((int6)((ulong)unaff_RBX >> 0x10),*(short *)(lVar3 + 2));
      if (*(short *)(lVar3 + 2) != -1) {
        FUN_00552330(uVar10 & 0xffffffff);
        uVar4 = FUN_005494c0();
        lVar6 = FUN_005498e0(uVar4,uVar10 & 0xffffffff);
        lVar3 = *(long *)(lVar6 + 0x98);
        if (lVar3 != 0) {
          lVar7 = FUN_005753c0(4);
          lVar3 = lVar6 + 0x98 + lVar3;
          cVar1 = FUN_0028eba0(lVar3);
          if ((cVar1 == '\0') || (cVar1 = FUN_0028e530(lVar7,lVar3), cVar1 != '\0')) {
            local_c0 = 0;
            lVar6 = *(long *)(PTR_DAT_0197e288 + 8);
            uVar4 = FUN_000e8680(lVar6,0,0xffffffff);
            thunk_FUN_012aa986(local_c8,0,uVar4);
            uVar9 = *(ushort *)(lVar6 + 0x1c) & 0x78;
            bVar11 = uVar9 != 0;
            if (uVar9 == 0) {
              uVar8 = *(uint *)(lVar6 + 0x20);
              if ((*(ushort *)(lVar6 + 0x1c) & 0x40) != 0) {
                lVar5 = FUN_000e8a90(lVar6,local_c8);
                if (lVar5 == 0) {
                  uVar8 = uVar8 | 0x5488bf;
                }
                else {
                  uVar8 = *(uint *)(lVar5 + 0x20) & 0x5488bf | uVar8;
                }
              }
              bVar11 = (uVar8 & 0xc08070) != 0;
            }
            if (bVar11) {
              FUN_000e6730(lVar6,local_c8,0,0xffffffff,0);
            }
            local_c4 = 0xff;
            local_c8[0] = *(undefined1 *)(lVar3 + 0x10);
            local_c6 = *(undefined2 *)(lVar3 + 0x12);
            if ((lVar7 != 0) && (cVar1 = FUN_0026b6d0(lVar7), cVar1 != '\0')) {
              local_c4 = FUN_0026b7f0(lVar7,local_c6);
            }
            uVar4 = FUN_00574ef0();
            FUN_00574dc0(uVar4,local_c8);
          }
        }
      }
      FUN_00777550(8);
      *(undefined4 *)(param_1 + 0x30) = 3;
      uVar4 = thunk_FUN_012aac96();
      *(undefined8 *)(param_1 + 0x38) = uVar4;
      FUN_00788e10(0x13);
    }
    break;
  case 3:
    cVar1 = FUN_007754d0(0);
    if ((cVar1 == '\0') || (cVar1 = FUN_00777640(0,0x100), cVar1 == '\0')) {
      lVar6 = thunk_FUN_012aac96();
      lVar3 = *(long *)(param_1 + 0x38);
      lVar7 = FUN_00068e90();
      if ((lVar6 - lVar3) / lVar7 < 0xb) break;
    }
    else {
      FUN_00783e90(0,0x1b,0);
    }
    FUN_00783ed0(0x19);
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

