
void FUN_007e12c0(long param_1,undefined8 *param_2)

{
  long lVar1;
  undefined8 *puVar2;
  
  if ((*(int *)*param_2 == 0) && (lVar1 = *(long *)(param_1 + 0x50), lVar1 != 0)) {
    puVar2 = *(undefined8 **)((int *)*param_2 + 2);
    *puVar2 = 0;
    puVar2[1] = 0;
    puVar2[2] = 0;
    puVar2[3] = 0;
    puVar2[4] = 0;
    puVar2[5] = 0;
    puVar2[6] = 0;
    puVar2[7] = 0;
    puVar2[8] = 0;
    puVar2[9] = 0;
    puVar2[10] = 0;
    puVar2[0xb] = 0;
    puVar2[0xc] = 0;
    puVar2[0xd] = 0;
    puVar2[0xe] = 0;
    puVar2[0xf] = 0;
    FUN_00f80ae0(lVar1,0);
    FUN_00f805c0(lVar1,0,1,0);
    return;
  }
  return;
}

