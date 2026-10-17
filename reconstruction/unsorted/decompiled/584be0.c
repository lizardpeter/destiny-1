
void FUN_00584be0(long param_1)

{
  int iVar1;
  undefined *puVar2;
  long *plVar3;
  undefined1 uVar4;
  undefined8 uVar5;
  long lVar6;
  long lVar7;
  uint uVar8;
  ushort uVar9;
  bool bVar10;
  undefined1 local_50 [8];
  int local_48;
  undefined4 local_44;
  undefined2 local_40;
  long local_38;
  
  plVar3 = DAT_01a1f100;
  puVar2 = PTR_DAT_019e4d40;
  local_38 = *DAT_01a1f100;
  lVar7 = *(long *)(PTR_DAT_019e4d40 + 8);
  uVar5 = FUN_000e8680(lVar7,0,0xffffffff);
  thunk_FUN_012aa986(&local_40,0,uVar5);
  uVar9 = *(ushort *)(lVar7 + 0x1c) & 0x78;
  bVar10 = uVar9 != 0;
  if (uVar9 == 0) {
    uVar8 = *(uint *)(lVar7 + 0x20);
    if ((*(ushort *)(lVar7 + 0x1c) & 0x40) != 0) {
      lVar6 = FUN_000e8a90(lVar7,&local_40);
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
    FUN_000e6730(lVar7,&local_40,0,0xffffffff,0);
  }
  uVar4 = FUN_0078e8e0();
  local_40 = CONCAT11(local_40._1_1_,uVar4);
  local_44 = 0xffffffff;
  FUN_0010c500(&local_44);
  local_40 = CONCAT11((undefined1)local_44,(undefined1)local_40);
  if (*(short *)(param_1 + 0x40) != local_40) {
    FUN_00300230(0x4a,*(undefined4 *)puVar2,&local_40);
  }
  lVar7 = FUN_005851a0();
  if ((((lVar7 != 0) && (iVar1 = *(int *)(lVar7 + 0x50), iVar1 != -0x7ee3623b)) &&
      (lVar7 = FUN_009503d0(), lVar7 != 0)) &&
     (local_48 = iVar1, lVar7 = FUN_00951b00(lVar7,&local_48,4,0), puVar2 = PTR_DAT_019e4d38,
     lVar7 == 0)) {
    lVar7 = *(long *)(PTR_DAT_019e4d38 + 8);
    uVar5 = FUN_000e8680(lVar7,0,0xffffffff);
    thunk_FUN_012aa986(local_50,0,uVar5);
    uVar9 = *(ushort *)(lVar7 + 0x1c) & 0x78;
    bVar10 = uVar9 != 0;
    if (uVar9 == 0) {
      uVar8 = *(uint *)(lVar7 + 0x20);
      if ((*(ushort *)(lVar7 + 0x1c) & 0x40) != 0) {
        lVar6 = FUN_000e8a90(lVar7,local_50);
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
      FUN_000e6730(lVar7,local_50,0,0xffffffff,0);
    }
    local_50[0] = 2;
    FUN_00300230(0x49,*(undefined4 *)puVar2,local_50);
  }
  if (*plVar3 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

