
void FUN_00586180(undefined8 param_1,char *param_2)

{
  long lVar1;
  int iVar2;
  undefined8 uVar3;
  long lVar4;
  uint uVar5;
  ushort uVar6;
  bool bVar7;
  undefined1 local_58;
  undefined7 uStack_57;
  undefined1 uStack_50;
  undefined7 uStack_4f;
  undefined8 local_48;
  undefined8 local_40;
  undefined8 local_38;
  undefined8 local_30;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  if (*param_2 == '\x03') {
    uVar3 = FUN_00582a40();
    FUN_00580380(uVar3,param_2 + 1);
    FUN_0057e060();
  }
  lVar1 = *(long *)(PTR_DAT_019e4d80 + 8);
  uVar3 = FUN_000e8680(lVar1,0,0xffffffff);
  thunk_FUN_012aa986(&local_58,0,uVar3);
  uVar6 = *(ushort *)(lVar1 + 0x1c) & 0x78;
  bVar7 = uVar6 != 0;
  if (uVar6 == 0) {
    uVar5 = *(uint *)(lVar1 + 0x20);
    if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
      lVar4 = FUN_000e8a90(lVar1,&local_58);
      if (lVar4 == 0) {
        uVar5 = uVar5 | 0x5488bf;
      }
      else {
        uVar5 = *(uint *)(lVar4 + 0x20) & 0x5488bf | uVar5;
      }
    }
    bVar7 = (uVar5 & 0xc08070) != 0;
  }
  if (bVar7) {
    FUN_000e6730(lVar1,&local_58,0,0xffffffff,0);
  }
  uStack_57 = 0;
  uStack_50 = 0;
  iVar2 = thunk_FUN_012aa826(param_2,&local_58,0x30);
  if (iVar2 != 0) {
    FUN_002487e0(&uStack_57);
    *(undefined8 *)(param_2 + 0x28) = local_30;
    *(undefined8 *)(param_2 + 0x20) = local_38;
    *(undefined8 *)(param_2 + 0x18) = local_40;
    *(undefined8 *)(param_2 + 0x10) = local_48;
    *(ulong *)(param_2 + 8) = CONCAT71(uStack_4f,uStack_50);
    *(ulong *)param_2 = CONCAT71(uStack_57,local_58);
  }
  if (*DAT_01a1f100 != local_28) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

