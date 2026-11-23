
undefined8 FUN_008e4ee0(undefined4 param_1,long param_2,int param_3,byte param_4)

{
  long *plVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  undefined8 *puVar8;
  long lVar9;
  
  plVar1 = (long *)(param_2 + 0x10);
  iVar3 = (*(code *)**(undefined8 **)(param_2 + 0x10))(plVar1);
  if (param_4 != 0 || iVar3 != param_3) {
    switch(param_3) {
    case 0:
      FUN_008f42b0(*(undefined4 *)(param_2 + 0x348));
      uVar6 = *(undefined4 *)(param_2 + 0x348);
      iVar5 = FUN_009236d0(uVar6);
      if (iVar5 == -1) {
        iVar7 = FUN_009236b0(uVar6);
        iVar5 = -1;
        if (iVar7 != -1) {
          uVar4 = FUN_00071f60(*(long *)(DAT_0273ea80 + 8) + 0x64c + (ulong)(ushort)iVar7 * 0x2af0);
          iVar5 = FUN_006ed9f0(uVar4);
        }
      }
      FUN_008e9e00(plVar1,uVar6,iVar5);
      break;
    case 1:
      uVar6 = *(undefined4 *)(param_2 + 0x348);
      iVar5 = FUN_009236d0(uVar6);
      if (iVar5 == -1) {
        iVar7 = FUN_009236b0(uVar6);
        iVar5 = -1;
        if (iVar7 != -1) {
          uVar4 = FUN_00071f60(*(long *)(DAT_0273ea80 + 8) + 0x64c + (ulong)(ushort)iVar7 * 0x2af0);
          iVar5 = FUN_006ed9f0(uVar4);
        }
      }
      FUN_008f6700(plVar1,uVar6,iVar5);
      break;
    case 2:
      FUN_008e8a20(plVar1,*(undefined4 *)(param_2 + 0x348));
      break;
    case 3:
      FUN_008e8a20(plVar1,*(undefined4 *)(param_2 + 0x348));
      *(undefined ***)(param_2 + 0x10) = &PTR_FUN_0194a9e0;
      break;
    case 4:
      uVar6 = *(undefined4 *)(param_2 + 0x348);
      iVar5 = FUN_009236d0(uVar6);
      if (iVar5 == -1) {
        iVar7 = FUN_009236b0(uVar6);
        iVar5 = -1;
        if (iVar7 != -1) {
          uVar6 = FUN_00071f60(*(long *)(DAT_0273ea80 + 8) + 0x64c + (ulong)(ushort)iVar7 * 0x2af0);
          iVar5 = FUN_006ed9f0(uVar6);
        }
      }
      uVar6 = FUN_006ed8f0(iVar5);
      FUN_008e6870(plVar1,uVar6);
      break;
    case 5:
      FUN_008e1050(plVar1,*(undefined4 *)(param_2 + 0x348));
      break;
    case 6:
      uVar6 = *(undefined4 *)(param_2 + 0x348);
      iVar5 = FUN_009236d0(uVar6);
      if (iVar5 == -1) {
        iVar7 = FUN_009236b0(uVar6);
        iVar5 = -1;
        if (iVar7 != -1) {
          uVar4 = FUN_00071f60(*(long *)(DAT_0273ea80 + 8) + 0x64c + (ulong)(ushort)iVar7 * 0x2af0);
          iVar5 = FUN_006ed9f0(uVar4);
        }
      }
      FUN_008f6700(plVar1,uVar6,iVar5);
      *(undefined ***)(param_2 + 0x10) = &PTR_FUN_0194a1d0;
      *(undefined8 *)(param_2 + 0xdc) = 0xffffffffffffffff;
      lVar9 = FUN_00526f80();
      *(undefined4 *)(param_2 + 0xe4) = *(undefined4 *)(lVar9 + 0x84);
      break;
    case 7:
      FUN_008f9af0(plVar1,*(undefined4 *)(param_2 + 0x348));
      break;
    case 9:
      FUN_008e07a0(plVar1);
      break;
    case 10:
      FUN_008de480(plVar1,*(undefined4 *)(param_2 + 0x348));
      break;
    case 0xb:
      uVar6 = *(undefined4 *)(param_2 + 0x348);
      iVar5 = FUN_009236d0(uVar6);
      if (iVar5 == -1) {
        iVar7 = FUN_009236b0(uVar6);
        iVar5 = -1;
        if (iVar7 != -1) {
          uVar6 = FUN_00071f60(*(long *)(DAT_0273ea80 + 8) + 0x64c + (ulong)(ushort)iVar7 * 0x2af0);
          iVar5 = FUN_006ed9f0(uVar6);
        }
      }
      FUN_008f7700(plVar1,iVar5);
      break;
    case 0xc:
      uVar6 = *(undefined4 *)(param_2 + 0x348);
      iVar5 = FUN_009236d0(uVar6);
      if (iVar5 == -1) {
        iVar7 = FUN_009236b0(uVar6);
        iVar5 = -1;
        if (iVar7 != -1) {
          uVar6 = FUN_00071f60(*(long *)(DAT_0273ea80 + 8) + 0x64c + (ulong)(ushort)iVar7 * 0x2af0);
          iVar5 = FUN_006ed9f0(uVar6);
        }
      }
      FUN_008de180(plVar1,iVar5);
      break;
    case 0xd:
      uVar6 = *(undefined4 *)(param_2 + 0x348);
      iVar5 = FUN_009236d0(uVar6);
      if (iVar5 == -1) {
        iVar7 = FUN_009236b0(uVar6);
        iVar5 = -1;
        if (iVar7 != -1) {
          uVar6 = FUN_00071f60(*(long *)(DAT_0273ea80 + 8) + 0x64c + (ulong)(ushort)iVar7 * 0x2af0);
          iVar5 = FUN_006ed9f0(uVar6);
        }
      }
      FUN_008fb0c0(plVar1,iVar5);
      break;
    case 0xe:
      uVar6 = *(undefined4 *)(param_2 + 0x348);
      iVar5 = FUN_009236d0(uVar6);
      if (iVar5 == -1) {
        iVar7 = FUN_009236b0(uVar6);
        iVar5 = -1;
        if (iVar7 != -1) {
          uVar6 = FUN_00071f60(*(long *)(DAT_0273ea80 + 8) + 0x64c + (ulong)(ushort)iVar7 * 0x2af0);
          iVar5 = FUN_006ed9f0(uVar6);
        }
      }
      FUN_008f9f40(plVar1,iVar5);
      break;
    case 0xf:
      FUN_008ee1f0(plVar1);
      break;
    case 0x10:
      FUN_008ee3d0(plVar1);
      break;
    case 0x11:
      FUN_008e28f0(plVar1,*(undefined4 *)(param_2 + 0x348));
    }
    *(undefined4 *)(param_2 + 0x340) = param_1;
  }
  cVar2 = FUN_00906e00();
  iVar5 = 3;
  if (cVar2 != '\0') {
    iVar7 = (**(code **)(*plVar1 + 8))(plVar1);
    if ((iVar7 == 0) && (iVar7 = 0, 0.0 < *(float *)(param_2 + 0x340))) {
      iVar7 = 1;
    }
    cVar2 = FUN_000014d0();
    iVar5 = 3;
    if (cVar2 == '\0') {
      iVar5 = iVar7;
    }
  }
  puVar8 = &DAT_0273c150;
  lVar9 = (long)*(int *)(param_2 + 0x348);
  if ((*(int *)((long)DAT_0273c150 + lVar9 * 0xc + 0x3d4) != iVar5) ||
     (*(int *)((long)DAT_0273c150 + lVar9 * 0xc + 0x3d8) != param_3)) {
    *(int *)((long)DAT_0273c150 + lVar9 * 0xc + 0x3d4) = iVar5;
    puVar8 = DAT_0273c150;
    *(int *)((long)DAT_0273c150 + (long)*(int *)(param_2 + 0x348) * 0xc + 0x3d8) = param_3;
  }
  return CONCAT71((int7)((ulong)puVar8 >> 8),param_4 & 1 | iVar3 != param_3);
}

