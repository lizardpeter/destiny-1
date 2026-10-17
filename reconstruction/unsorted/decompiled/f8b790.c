
void FUN_00f8b790(long param_1,uint *param_2,undefined4 param_3,undefined8 param_4)

{
  long lVar1;
  long *plVar2;
  undefined8 local_30;
  undefined8 local_28;
  long local_20;
  
  plVar2 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  *(undefined1 *)(param_1 + 0x2ee) = 1;
  *(uint **)(param_1 + 0x2a8) = param_2;
  *(undefined8 *)(param_1 + 0x278) = param_4;
  *(undefined4 *)(param_1 + 0x298) = param_3;
  *(undefined8 *)(param_1 + 0x308) = 0;
  if (param_2 != (uint *)0x0) {
    *(byte *)(param_1 + 0x2f6) = (byte)(*param_2 >> 0x17) & 1;
    if ((ushort)param_2[1] != 0) {
      FUN_00f7d180(&local_30,((ulong)*param_2 & 0x7fffff) + *(long *)(param_2 + 2) * 0x100,
                   (ulong)(ushort)param_2[1] << 4);
      lVar1 = *(long *)(param_1 + 8);
      *(undefined8 *)(lVar1 + 0x4808) = local_28;
      *(undefined8 *)(lVar1 + 0x4800) = local_30;
      *(byte *)(param_1 + 0xf0) = *(byte *)(param_1 + 0xf0) | 0x80;
      *(byte *)(param_1 + 0x2e) = *(byte *)(param_1 + 0x2e) | 1;
    }
  }
  if (*plVar2 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

