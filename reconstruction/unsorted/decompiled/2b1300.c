
bool FUN_002b1300(uint param_1,byte param_2)

{
  bool bVar1;
  
  if (((param_2 & 1) == 0) || (bVar1 = param_1 == 0, !bVar1)) {
    if ((param_2 & 2) != 0) {
      bVar1 = (param_1 & 0xf0000000) == 0xd0000000;
      goto LAB_002b1322;
    }
LAB_002b1326:
    bVar1 = false;
    if ((param_2 & 4) != 0) {
      bVar1 = (param_1 & 0xf0000000) == 0xe0000000;
      goto LAB_002b133d;
    }
  }
  else {
LAB_002b1322:
    if (bVar1 == false) goto LAB_002b1326;
LAB_002b133d:
    if (bVar1 != false) goto LAB_002b1356;
  }
  if ((param_2 & 8) != 0) {
    bVar1 = (param_1 & 0xf0000000) == 0xc0000000;
  }
LAB_002b1356:
  if ((bVar1 == false) && ((param_2 & 0x10) != 0)) {
    bVar1 = (param_1 & 0xf0000000) == 0xb0000000;
  }
  if ((bVar1 == false) && ((param_2 & 0x20) != 0)) {
    bVar1 = (param_1 & 0xf0000000) == 0xa0000000;
  }
  return bVar1;
}

