
undefined8 FUN_007ec9b0(long param_1)

{
  undefined8 uVar1;
  long lVar2;
  undefined8 *puVar3;
  long local_40;
  uint local_38;
  uint local_34;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  FUN_00076040(&local_40,&DAT_026e4040,0x10,0xffff,0,0,0);
  if ((ulong)local_38 < (ulong)local_34 + 0x10) {
    *(undefined8 *)(param_1 + 0x10) = 0;
    uVar1 = 0;
  }
  else {
    uVar1 = 0;
    puVar3 = (undefined8 *)(local_40 + (ulong)local_34);
    *(undefined8 **)(param_1 + 0x10) = puVar3;
    if (puVar3 != (undefined8 *)0x0) {
      lVar2 = 0;
      FUN_00076040(&local_40,&DAT_026e4040,0x281c0,0xffff,0,0,0);
      if ((ulong)local_34 + 0x281c0 <= (ulong)local_38) {
        lVar2 = local_40 + (ulong)local_34;
        local_34 = local_34 + 0x281c0;
      }
      *puVar3 = 0x11;
      puVar3[1] = lVar2;
      thunk_FUN_012aa986(*(undefined8 *)(*(long *)(param_1 + 0x10) + 8),0,0x281c0);
      uVar1 = 1;
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return uVar1;
  }
  uVar1 = thunk_FUN_012aa7f6();
  return uVar1;
}

