
void FUN_0058b350(long param_1)

{
  long lVar1;
  long lVar2;
  undefined8 uVar3;
  long lVar4;
  ushort uVar5;
  uint uVar6;
  undefined4 uVar7;
  bool bVar8;
  
  uVar7 = 0xffffffff;
  if (DAT_019403a8 != (undefined4 *)0x0) {
    uVar7 = *DAT_019403a8;
  }
  FUN_0023e010(param_1 + 8,s_investment_peer_subscription_pro_0163e0fb,0x150,4,uVar7,5,0,0x18,
               thunk_FUN_001681a0);
  lVar1 = *(long *)(param_1 + 8);
  lVar2 = *(long *)(PTR_DAT_019e4d08 + 8);
  uVar3 = FUN_000e8680(lVar2,0,0xffffffff);
  thunk_FUN_012aa986(lVar1,0,uVar3);
  uVar5 = *(ushort *)(lVar2 + 0x1c) & 0x78;
  bVar8 = uVar5 != 0;
  if (uVar5 != 0) goto LAB_0058b42d;
  uVar6 = *(uint *)(lVar2 + 0x20);
  if ((*(ushort *)(lVar2 + 0x1c) & 0x40) != 0) {
    if (lVar1 != 0) {
      lVar4 = FUN_000e8a90(lVar2,lVar1);
      if (lVar4 != 0) {
        uVar6 = uVar6 | *(uint *)(lVar4 + 0x20) & 0x5488bf;
        goto LAB_0058b424;
      }
    }
    uVar6 = uVar6 | 0x5488bf;
  }
LAB_0058b424:
  bVar8 = (uVar6 & 0xc08070) != 0;
LAB_0058b42d:
  if (bVar8) {
    FUN_000e6730(lVar2,lVar1,0,0xffffffff,0);
  }
  FUN_003000b0(0x2b,&PTR_PTR_019402e8);
  return;
}

