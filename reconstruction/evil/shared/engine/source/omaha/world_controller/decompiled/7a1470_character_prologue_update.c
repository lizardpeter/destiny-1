
void FUN_007a1470(long param_1)

{
  undefined4 uVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  undefined8 uVar5;
  long lVar6;
  long lVar7;
  uint uVar8;
  ushort uVar9;
  long extraout_RDX;
  long extraout_RDX_00;
  bool bVar10;
  undefined4 local_c0 [2];
  undefined1 local_b8 [2];
  undefined2 local_b6;
  undefined1 local_b4;
  undefined4 local_b0;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  switch(*(undefined4 *)(param_1 + 0x30)) {
  case 0:
    uVar5 = FUN_005494c0();
    FUN_005498e0(uVar5,*(undefined2 *)(param_1 + 0x34));
    if (*(int *)(extraout_RDX + 0x18) == -0x7ee3623b) {
      *(undefined4 *)(param_1 + 0x30) = 4;
    }
    else {
      *(undefined4 *)(param_1 + 0x30) = 1;
    }
    break;
  case 1:
    cVar2 = FUN_000014d0();
    if (cVar2 == '\0') {
      uVar5 = FUN_005494c0();
      FUN_005498e0(uVar5,*(undefined2 *)(param_1 + 0x34));
      uVar1 = *(undefined4 *)(extraout_RDX_00 + 0x18);
      uVar5 = FUN_0033fa20();
      local_c0[0] = uVar1;
      iVar3 = FUN_0033fc20(uVar5,local_c0);
      if (iVar3 == -1) {
        *(undefined4 *)(param_1 + 0x30) = 3;
      }
      else {
        FUN_00788e10(0x20);
        FUN_00765fb0(5);
        if ((DAT_0295c100 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_0295c100), iVar4 != 0)) {
          DAT_0295c0a0 = &PTR_FUN_01914b60;
          thunk_FUN_012aa7e6(&DAT_0295c100);
        }
        FUN_0033e0d0(&DAT_0295c0a0,iVar3,0);
        *(undefined4 *)(param_1 + 0x30) = 2;
      }
    }
    else {
      *(undefined4 *)(param_1 + 0x30) = 3;
    }
    break;
  case 2:
    if ((DAT_0295c100 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_0295c100), iVar3 != 0)) {
      DAT_0295c0a0 = &PTR_FUN_01914b60;
      thunk_FUN_012aa7e6(&DAT_0295c100);
    }
    cVar2 = FUN_0033e140(&DAT_0295c0a0);
    if (cVar2 == '\0') {
      FUN_00552330(*(undefined2 *)(param_1 + 0x34));
      *(undefined4 *)(param_1 + 0x30) = 3;
    }
    else {
      cVar2 = FUN_0078c3a0();
      if (cVar2 != '\0') {
        FUN_000ad120();
        cVar2 = FUN_000ad6f0(10);
        if (cVar2 == '\0') {
          cVar2 = FUN_000ad6f0(0xb);
          FUN_000ad140();
          if (cVar2 == '\0') break;
        }
        else {
          FUN_000ad140();
        }
        if ((DAT_0295c100 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_0295c100), iVar3 != 0)) {
          DAT_0295c0a0 = &PTR_FUN_01914b60;
          thunk_FUN_012aa7e6(&DAT_0295c100);
        }
        FUN_0033e110(&DAT_0295c0a0);
      }
    }
    break;
  case 3:
    uVar5 = FUN_005494c0();
    lVar7 = FUN_005498e0(uVar5,*(undefined2 *)(param_1 + 0x34));
    if (*(long *)(lVar7 + 0x98) == 0) {
      *(undefined2 *)(param_1 + 0x34) = 0xffff;
      *(undefined4 *)(param_1 + 0x30) = 5;
    }
    else {
      *(undefined2 *)(param_1 + 0x34) = *(undefined2 *)(*(long *)(lVar7 + 0x98) + 0xaa + lVar7);
      *(undefined4 *)(param_1 + 0x30) = 0;
    }
    break;
  case 4:
    local_b0 = 0;
    lVar7 = *(long *)(PTR_DAT_0197e288 + 8);
    uVar5 = FUN_000e8680(lVar7,0,0xffffffff);
    thunk_FUN_012aa986(local_b8,0,uVar5);
    uVar9 = *(ushort *)(lVar7 + 0x1c) & 0x78;
    bVar10 = uVar9 != 0;
    if (uVar9 == 0) {
      uVar8 = *(uint *)(lVar7 + 0x20);
      if ((*(ushort *)(lVar7 + 0x1c) & 0x40) != 0) {
        lVar6 = FUN_000e8a90(lVar7,local_b8);
        if (lVar6 == 0) {
          uVar8 = uVar8 | 0x5488bf;
        }
        else {
          uVar8 = *(uint *)(lVar6 + 0x20) & 0x5488bf | uVar8;
        }
      }
      bVar10 = (uVar8 & 0xc08070) != 0;
    }
    if (bVar10) {
      FUN_000e6730(lVar7,local_b8,0,0xffffffff,0);
    }
    local_b4 = 0xff;
    local_b8[0] = 1;
    local_b6 = *(undefined2 *)(param_1 + 0x34);
    lVar7 = FUN_005753c0(4);
    if ((lVar7 != 0) && (cVar2 = FUN_0026b6d0(lVar7,*(undefined2 *)(param_1 + 0x34)), cVar2 != '\0')
       ) {
      local_b4 = FUN_0026b7f0(lVar7,*(undefined2 *)(param_1 + 0x34));
    }
    uVar5 = FUN_00574ef0();
    FUN_00574dc0(uVar5,local_b8);
  default:
    FUN_00783ed0(0x19);
  }
  if (*DAT_01a1f100 != local_28) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

