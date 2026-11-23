
void FUN_00585e00(long param_1)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined8 uVar5;
  long lVar6;
  long lVar7;
  long lVar8;
  
  FUN_00586f10();
  if (*(char *)(param_1 + 0x48) == '\x01') {
    uVar5 = FUN_0056b260();
    if (DAT_02652ba8 != 0) {
      uVar2 = FUN_0055c360(uVar5);
      lVar6 = FUN_0056dc00(uVar5,5,uVar2,&DAT_02652ba8);
      if (lVar6 != 0) {
        lVar8 = *(long *)(lVar6 + 8);
        lVar7 = *(long *)(param_1 + 0x408) - *(long *)(param_1 + 0x400);
        if (lVar7 != 0 && *(long *)(param_1 + 0x400) <= *(long *)(param_1 + 0x408)) {
          lVar8 = lVar7 / *(long *)(param_1 + 0x410) + lVar8;
        }
        cVar1 = FUN_00906e00();
        if (cVar1 != '\0') {
          iVar3 = FUN_005916f0();
          iVar4 = iVar3 - *(int *)(param_1 + 0x418);
          if (iVar4 != 0 && *(int *)(param_1 + 0x418) <= iVar3) {
            iVar3 = FUN_00591c20(iVar4);
            lVar8 = iVar3 + lVar8;
          }
        }
        lVar7 = *(long *)(param_1 + 0x58);
        FUN_01049e70(param_1 + 0x50,lVar6);
        if (lVar7 <= lVar8) {
          lVar7 = lVar8;
        }
        *(long *)(param_1 + 0x58) = lVar7;
      }
    }
  }
  else if (*(char *)(param_1 + 0x48) == '\0') {
    uVar5 = FUN_0056b260();
    FUN_0056bcd0(uVar5,5,&DAT_02652ba8,2);
    *(undefined1 *)(param_1 + 0x48) = 1;
  }
  return;
}

