
ushort FUN_000ad3a0(int param_1)

{
  ushort uVar1;
  ushort uVar2;
  
  if (DAT_01ad40d1 == '\0') {
    switch(param_1) {
    case 0x69:
      uVar1 = DAT_01ad4988;
      uVar2 = DAT_01ad495c;
      break;
    case 0x6a:
      uVar1 = DAT_01ad49a8;
      uVar2 = DAT_01ad498c;
      break;
    case 0x6b:
      uVar1 = DAT_01ad49a0;
      uVar2 = DAT_01ad4990;
      break;
    case 0x6c:
      uVar1 = DAT_01ad499c;
      uVar2 = DAT_01ad4994;
      break;
    default:
      return *(ushort *)(&DAT_01ad4878 + (long)param_1 * 4);
    }
    if (uVar1 < uVar2) {
      uVar1 = uVar2;
    }
    return uVar1;
  }
  return 0;
}

