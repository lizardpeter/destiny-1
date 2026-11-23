
ulong FUN_007e13e0(undefined8 param_1,undefined8 *param_2,int *param_3)

{
  ulong *puVar1;
  ulong in_RAX;
  ulong uVar2;
  ulong uVar3;
  
  uVar2 = in_RAX & 0xffffffffffffff00;
  if (*(int *)*param_2 == 0) {
    puVar1 = *(ulong **)((int *)*param_2 + 2);
    uVar3 = *puVar1 & puVar1[1] & puVar1[2] & puVar1[3] & puVar1[4] & puVar1[5] & puVar1[6] &
            puVar1[7] & puVar1[8] & puVar1[9] & puVar1[10] & puVar1[0xb] & puVar1[0xc] & puVar1[0xd]
            & puVar1[0xe] & puVar1[0xf];
    uVar2 = uVar3 >> 0x3f;
    if ((long)uVar3 < 0) {
      *param_3 = ((int)puVar1[0xf] +
                 (((int)puVar1[0xd] +
                  (((int)puVar1[0xb] +
                   (((int)puVar1[9] +
                    (((int)puVar1[7] +
                     (((int)puVar1[5] +
                      (((int)puVar1[3] + ((int)puVar1[1] - (int)*puVar1)) - (int)puVar1[2])) -
                     (int)puVar1[4])) - (int)puVar1[6])) - (int)puVar1[8])) - (int)puVar1[10])) -
                 (int)puVar1[0xc])) - (int)puVar1[0xe];
    }
  }
  return uVar2;
}

