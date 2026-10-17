
void FUN_00587010(undefined8 param_1,undefined8 *param_2,undefined8 *param_3)

{
  long lVar1;
  int iVar2;
  undefined8 uVar3;
  long lVar4;
  uint uVar5;
  ushort uVar6;
  bool bVar7;
  undefined1 local_60;
  undefined7 uStack_5f;
  undefined1 uStack_58;
  undefined7 uStack_57;
  undefined8 local_50;
  undefined8 local_48;
  undefined8 local_40;
  undefined8 local_38;
  long local_30;
  
  local_30 = *DAT_01a1f100;
  lVar1 = *(long *)(PTR_DAT_019e4d80 + 8);
  uVar3 = FUN_000e8680(lVar1,0,0xffffffff);
  thunk_FUN_012aa986(&local_60,0,uVar3);
  uVar6 = *(ushort *)(lVar1 + 0x1c) & 0x78;
  bVar7 = uVar6 != 0;
  if (uVar6 == 0) {
    uVar5 = *(uint *)(lVar1 + 0x20);
    if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
      lVar4 = FUN_000e8a90(lVar1,&local_60);
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
    FUN_000e6730(lVar1,&local_60,0,0xffffffff,0);
  }
  uStack_5f = (undefined7)*param_3;
  uStack_58 = (undefined1)((ulong)*param_3 >> 0x38);
  local_60 = 1;
  iVar2 = thunk_FUN_012aa826(param_2,&local_60,0x30);
  if (iVar2 != 0) {
    FUN_002487e0(&uStack_5f);
    param_2[5] = local_38;
    param_2[4] = local_40;
    param_2[3] = local_48;
    param_2[2] = local_50;
    param_2[1] = CONCAT71(uStack_57,uStack_58);
    *param_2 = CONCAT71(uStack_5f,local_60);
  }
  FUN_0057e060();
  if (*DAT_01a1f100 != local_30) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

