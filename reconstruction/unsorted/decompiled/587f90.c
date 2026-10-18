
void FUN_00587f90(long param_1)

{
  undefined8 *puVar1;
  undefined4 uVar2;
  
  uVar2 = 0xffffffff;
  if (DAT_0193ffa8 != (undefined4 *)0x0) {
    uVar2 = *DAT_0193ffa8;
  }
  FUN_0023e010(param_1 + 8,s_investment_user_message_manager_0163df52,8,4,uVar2,5,3,0x18,
               thunk_FUN_001681a0);
  puVar1 = (undefined8 *)0x0;
  if (*(undefined8 **)(param_1 + 8) != (undefined8 *)0x0) {
    puVar1 = *(undefined8 **)(param_1 + 8);
  }
  *puVar1 = 0;
  return;
}

