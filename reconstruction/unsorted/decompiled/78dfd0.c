
undefined2 FUN_0078dfd0(void)

{
  int iVar1;
  undefined2 extraout_AX;
  undefined2 extraout_AX_00;
  undefined2 extraout_var;
  undefined2 extraout_var_00;
  undefined4 extraout_var_01;
  undefined4 extraout_var_02;
  undefined2 uVar2;
  
  iVar1 = FUN_0078b270();
  uVar2 = 0xffff;
  if (iVar1 != 3) {
    FUN_007642e0();
    if ((CONCAT44(extraout_var_01,CONCAT22(extraout_var,extraout_AX)) &
        CONCAT44(extraout_var_01,CONCAT22(extraout_var,extraout_AX))) != 0) {
      FUN_002a2980(CONCAT44(extraout_var_01,CONCAT22(extraout_var,extraout_AX)));
      uVar2 = *(undefined2 *)
               (CONCAT44(extraout_var_02,CONCAT22(extraout_var_00,extraout_AX_00)) + 0x682);
    }
  }
  return uVar2;
}

