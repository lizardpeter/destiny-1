
void FUN_005872b0(long param_1)

{
  long lVar1;
  undefined4 uVar2;
  
  uVar2 = 0xffffffff;
  if (DAT_0193ff18 != (undefined4 *)0x0) {
    uVar2 = *DAT_0193ff18;
  }
  FUN_0023e010(param_1 + 8,s_zDinvestment_user_manager_0163ddd2 + 2,0x420,4,uVar2,5,0,0x18,
               thunk_FUN_001681a0);
  lVar1 = 0;
  if (*(long *)(param_1 + 8) != 0) {
    lVar1 = *(long *)(param_1 + 8);
  }
  FUN_00585af0(lVar1);
  uVar2 = 0xffffffff;
  if (DAT_0193ff08 != (undefined4 *)0x0) {
    uVar2 = *DAT_0193ff08;
  }
  FUN_0023e010(param_1 + 0x10,s_investment_presence_manager_0163ddec,8,4,uVar2,5,3,0x18,
               thunk_FUN_001681a0);
  lVar1 = 0;
  if (*(long *)(param_1 + 0x10) != 0) {
    lVar1 = *(long *)(param_1 + 0x10);
  }
  FUN_00543ee0(lVar1);
  FUN_003000b0(0x25,&PTR_PTR_0193fe98);
  FUN_003000b0(0x2c,&PTR_PTR_0193fea8);
  FUN_003000b0(0x31,&PTR_PTR_0193fea0);
  return;
}

