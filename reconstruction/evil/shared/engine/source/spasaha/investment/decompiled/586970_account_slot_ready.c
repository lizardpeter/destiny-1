
void FUN_00586970(undefined8 param_1,char *param_2)

{
  char cVar1;
  long lVar2;
  
  if (param_2[0x28] != '\0') {
    param_2[0x18] = '\0';
    param_2[0x20] = '\0';
    param_2[0x21] = '\0';
    param_2[0x22] = '\0';
    param_2[0x23] = '\0';
    param_2[0x24] = '\0';
    param_2[0x25] = '\0';
    param_2[0x26] = '\0';
    param_2[0x27] = '\0';
    param_2[0x28] = '\0';
  }
  if (*param_2 == '\x03') {
    if ((*(long *)(param_2 + 0x10) != 0) && (param_2[0x18] == '\0')) {
      cVar1 = FUN_005845a0(param_2 + 0x10);
      param_2[0x18] = cVar1;
      if (*param_2 != '\x03') {
        return;
      }
    }
    if ((((*(long *)(param_2 + 0x10) != 0) && (param_2[0x18] != '\0')) &&
        (*(long *)(param_2 + 0x20) == 0)) &&
       (lVar2 = FUN_005845f0(param_2 + 0x10), *(long *)(lVar2 + 0x68) != 0)) {
      cVar1 = FUN_00584510((undefined8 *)(lVar2 + 0x68));
      if (cVar1 != '\0') {
        *(undefined8 *)(param_2 + 0x20) = *(undefined8 *)(lVar2 + 0x68);
      }
    }
  }
  return;
}

