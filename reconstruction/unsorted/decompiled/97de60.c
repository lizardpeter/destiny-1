
ulong FUN_0097de60(long param_1,long param_2,uint *param_3)

{
  long *plVar1;
  ulong uVar2;
  ulong uVar3;
  uint local_24;
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  uVar2 = 0x82166bc0;
  if (param_2 == 0x82166bc0) {
    *param_3 = 0;
  }
  else {
    local_24 = 0xffffffff;
    uVar2 = FUN_0097e410(*(undefined8 *)(param_1 + 0x90),param_2,&local_24);
    uVar3 = uVar2 & 0xffffffffffffff00;
    if (uVar2 == 0) goto LAB_0097deb6;
    uVar2 = (ulong)local_24;
    *param_3 = local_24;
  }
  uVar3 = CONCAT71((int7)(uVar2 >> 8),1);
LAB_0097deb6:
  if (*plVar1 == local_20) {
    return uVar3;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return uVar2;
}

