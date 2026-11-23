
undefined1
FUN_0055bd10(undefined8 param_1,undefined8 param_2,char *param_3,char *param_4,undefined8 param_5,
            undefined4 *param_6)

{
  ushort *puVar1;
  undefined1 uVar2;
  
  *param_4 = *param_3;
  if (*param_3 == '\x03') {
    thunk_FUN_012aa7c6(param_4 + 1,param_3 + 1,0xe0c);
    puVar1 = (ushort *)(param_4 + 0x203);
    *puVar1 = *puVar1 << 8 | *puVar1 >> 8;
    puVar1 = (ushort *)(param_4 + 1);
    *puVar1 = *puVar1 << 8 | *puVar1 >> 8;
  }
  else {
    uVar2 = 0;
    if (*param_3 != '\x01') goto LAB_0055bd7b;
    thunk_FUN_012aa7c6(param_4 + 1,param_3 + 1,0x100e);
    puVar1 = (ushort *)(param_4 + 0x405);
    *puVar1 = *puVar1 << 8 | *puVar1 >> 8;
    puVar1 = (ushort *)(param_4 + 1);
    *puVar1 = *puVar1 << 8 | *puVar1 >> 8;
    puVar1 = (ushort *)(param_4 + 0x203);
    *puVar1 = *puVar1 << 8 | *puVar1 >> 8;
  }
  uVar2 = 1;
LAB_0055bd7b:
  *param_6 = 0x100f;
  return uVar2;
}

