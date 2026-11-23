
void FUN_0028d000(long *param_1,short param_2,code param_3)

{
  long lVar1;
  char cVar2;
  long *plVar3;
  long lVar4;
  code *pcVar5;
  undefined1 *puVar6;
  long lVar7;
  
  plVar3 = (long *)FUN_0025a550();
  lVar4 = (**(code **)(*plVar3 + 0x2b8))(plVar3);
  lVar1 = lVar4 + 0x18 + *(long *)(lVar4 + 8);
  lVar7 = (long)param_2;
  cVar2 = *(char *)(lVar4 + *(long *)(lVar4 + 8) + 0x1c + lVar7 * 8);
  if (cVar2 == '\x03') {
    lVar4 = (**(code **)(*param_1 + 0x90))(param_1);
    pcVar5 = (code *)(lVar4 + 0x53c0 + (long)*(short *)(lVar1 + 6 + lVar7 * 8));
  }
  else if (cVar2 == '\x02') {
    lVar4 = (**(code **)(*param_1 + 0x88))(param_1);
    pcVar5 = FUN_00005430 + *(short *)(lVar1 + 6 + lVar7 * 8) + lVar4;
  }
  else {
    if (cVar2 != '\x01') {
      return;
    }
    lVar4 = (**(code **)(*param_1 + 0x88))(param_1);
    pcVar5 = (code *)(lVar4 + 0x383c + (long)*(short *)(lVar1 + 6 + lVar7 * 8));
  }
  if (*pcVar5 != param_3) {
    *pcVar5 = param_3;
    puVar6 = (undefined1 *)(**(code **)(*param_1 + 200))(param_1);
    *puVar6 = 0;
  }
  return;
}

