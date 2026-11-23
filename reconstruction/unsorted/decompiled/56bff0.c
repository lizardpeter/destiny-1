
void FUN_0056bff0(long param_1,char param_2,char param_3,long *param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  long lVar4;
  long lVar5;
  
  lVar4 = 0x60;
  while ((*(char *)(param_1 + lVar4) != param_2 || (*(long *)(param_1 + 0x20 + lVar4) != *param_4)))
  {
    lVar4 = lVar4 + 0x40;
    lVar5 = 0;
    if ((int)lVar4 == 0x40a0) {
LAB_0056c027:
      cVar1 = *(char *)(lVar5 + 0x2a);
      *(char *)(lVar5 + 0x2a) = param_3;
      if ((param_3 != cVar1) && (param_3 == '\x01')) {
        lVar5 = lVar5 + 0x2c;
        cVar1 = FUN_0012f640(lVar5);
        if (cVar1 != '\0') {
          iVar2 = FUN_00543f20(lVar5);
          lVar4 = FUN_0034e490();
          if (iVar2 < *(int *)(lVar4 + 0x24)) {
            uVar3 = FUN_00543f20(lVar5);
          }
          else {
            lVar4 = FUN_0034e490();
            uVar3 = *(undefined4 *)(lVar4 + 0x24);
          }
          FUN_00543f70(lVar5,uVar3);
          return;
        }
      }
      return;
    }
  }
  lVar5 = param_1 + lVar4;
  goto LAB_0056c027;
}

