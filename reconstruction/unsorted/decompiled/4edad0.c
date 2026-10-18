
bool FUN_004edad0(long param_1,int param_2)

{
  int iVar1;
  char cVar2;
  int iVar3;
  
  iVar1 = *(int *)(param_1 + 0x2f0 + (long)param_2 * 4);
  iVar3 = -1;
  if (iVar1 != -1) {
    switch(param_2) {
    case 0:
    case 1:
      cVar2 = FUN_0063fed0();
      break;
    case 2:
      cVar2 = FUN_0063ffd0();
      break;
    case 3:
      cVar2 = FUN_0063ff50();
      break;
    case 4:
      cVar2 = FUN_00640050();
      break;
    case 5:
      cVar2 = FUN_006400d0();
      break;
    default:
      iVar3 = iVar1;
      goto LAB_004edb39;
    }
    if (cVar2 != '\0') {
      return false;
    }
    iVar3 = *(int *)(param_1 + 0x2f0 + (long)param_2 * 4);
  }
LAB_004edb39:
  return iVar3 != -1;
}

