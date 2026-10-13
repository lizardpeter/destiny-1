
undefined8 FUN_00bb1c10(undefined8 param_1,undefined8 param_2,int param_3)

{
  undefined8 *puVar1;
  long *plVar2;
  char cVar3;
  undefined8 uVar4;
  long local_38;
  long local_30;
  
  plVar2 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  cVar3 = FUN_00906f70();
  uVar4 = 1;
  if (cVar3 == '\0') {
    local_38 = 0;
    FUN_00300b00(0x13,param_3 + 0x60,&local_38);
    uVar4 = 0;
    if (local_38 != 0) {
      puVar1 = *(undefined8 **)(local_38 + 8);
      *puVar1 = param_1;
      puVar1[10] = 0;
      puVar1[9] = 0;
      puVar1[8] = 0;
      puVar1[7] = 0;
      puVar1[6] = 0;
      puVar1[5] = 0;
      puVar1[4] = 0;
      puVar1[3] = 0;
      puVar1[2] = 0;
      puVar1[1] = 0;
      *(int *)(puVar1 + 0xb) = param_3;
      thunk_FUN_012aa7c6((long)puVar1 + 0x5c,param_2,(long)param_3);
      FUN_00300b90(local_38);
      uVar4 = 1;
    }
  }
  if (*plVar2 == local_30) {
    return uVar4;
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

