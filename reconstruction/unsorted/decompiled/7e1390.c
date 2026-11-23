
void FUN_007e1390(long param_1,undefined8 *param_2)

{
  long lVar1;
  
  if ((*(int *)*param_2 == 0) && (lVar1 = *(long *)(param_1 + 0x50), lVar1 != 0)) {
    FUN_00f80ae0(lVar1,1,*(undefined8 *)((int *)*param_2 + 2));
    FUN_00f805c0(lVar1,0,0,0);
    return;
  }
  return;
}

