
byte FUN_000ad300(int param_1)

{
  byte bVar1;
  
  bVar1 = 0;
  if (DAT_01ad40d1 == '\0') {
    switch(param_1) {
    case 0x69:
      bVar1 = DAT_01ad495e;
      if (DAT_01ad495e <= DAT_01ad498a) {
        return DAT_01ad498a;
      }
      break;
    case 0x6a:
      bVar1 = DAT_01ad498e;
      if (DAT_01ad498e <= DAT_01ad49aa) {
        return DAT_01ad49aa;
      }
      break;
    case 0x6b:
      bVar1 = DAT_01ad4992;
      if (DAT_01ad4992 <= DAT_01ad49a2) {
        return DAT_01ad49a2;
      }
      break;
    case 0x6c:
      bVar1 = DAT_01ad4996;
      if (DAT_01ad4996 <= DAT_01ad499e) {
        return DAT_01ad499e;
      }
      break;
    default:
      bVar1 = (&DAT_01ad487a)[(long)param_1 * 4];
    }
  }
  return bVar1;
}

