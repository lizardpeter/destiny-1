
undefined8 FUN_000ae0c0(uint param_1,undefined8 param_2,undefined8 param_3)

{
  int iVar1;
  undefined8 uVar2;
  undefined1 uVar3;
  ulong uVar4;
  undefined1 local_d0 [4];
  uint local_cc;
  char local_c6;
  byte local_c5;
  undefined1 local_c4;
  undefined1 local_b0 [76];
  char local_64;
  byte local_48;
  long local_38;
  
  uVar4 = (ulong)param_1;
  local_38 = *DAT_01a1f100;
  uVar3 = 0;
  if ((&DAT_01ad4eec)[uVar4 * 0x18] != '\0') {
    iVar1 = thunk_FUN_012ab0e6((&DAT_01ad4edc)[uVar4 * 6],local_b0);
    if ((iVar1 == 0) && (local_64 != '\0')) {
      if ((uint)local_48 != *(uint *)(&DAT_01ad4ee0 + uVar4 * 0x18)) {
        iVar1 = thunk_FUN_012ab0d6((&DAT_01ad4edc)[uVar4 * 6],local_d0);
        if (iVar1 == 0) {
          *(uint *)(&DAT_01ad4ee0 + uVar4 * 0x18) = (uint)local_c5;
          (&DAT_01ad4eed)[uVar4 * 0x18] = local_c4;
          *(float *)(&DAT_01ad4ee4 + uVar4 * 0x18) = (float)(local_cc & 0xffff);
          *(float *)(&DAT_01ad4ee8 + uVar4 * 0x18) = (float)(local_cc >> 0x10);
          (&DAT_01ad4ef1)[uVar4 * 0x18] = local_c6 == '\x01';
        }
      }
      FUN_000adc00(param_1,local_b0,param_3);
      uVar3 = 1;
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar3);
  }
  uVar2 = thunk_FUN_012aa7f6();
  return uVar2;
}

